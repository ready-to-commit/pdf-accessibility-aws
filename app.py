import json
import boto3
import os
import csv
import datetime
import zipfile
from PyPDF2 import PdfReader

s3 = boto3.client('s3')

OUTPUT_BUCKET = "pdf-accessibility-level-1-check-output"


def check_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        info = reader.metadata

        title = info.title if info.title else "Missing"

        try:
            language = reader.trailer["/Root"].get("/Lang", "Missing")
        except:
            language = "Missing"

        tagged = "Yes" if "/StructTreeRoot" in reader.trailer["/Root"] else "No"

        status = "Passed" if (title != "Missing" and language != "Missing" and tagged == "Yes") else "Failed"

        return title, language, tagged, status

    except Exception:
        return "Error", "Error", "No", "Failed"


def create_csv(results, csv_path):
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["File Name", "Title", "Language", "Tagged", "Status"])

        for row in results:
            writer.writerow(row)


def lambda_handler(event, context):
    print("Lambda triggered")
    print(json.dumps(event))

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    file_path = f"/tmp/{os.path.basename(key)}"
    s3.download_file(bucket, key, file_path)

    files_to_process = []

    # Handle ZIP
    if key.lower().endswith(".zip"):
        extract_path = "/tmp/extracted"
        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    files_to_process.append(os.path.join(root, file))
    else:
        files_to_process.append(file_path)

    results = []

    # Process PDFs
    for pdf_file in files_to_process:
        filename = os.path.basename(pdf_file)

        title, language, tagged, status = check_pdf(pdf_file)

        # Store JSON per file
        json_key = f"reports/json/{filename}.json"

        result_json = {
            "file": filename,
            "title": title,
            "language": language,
            "tagged": tagged,
            "status": status
        }

        s3.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=json_key,
            Body=json.dumps(result_json),
            ContentType="application/json"
        )

        # Collect for CSV
        results.append([filename, title, language, tagged, status])

    # Create ONE CSV per upload event
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"report_{timestamp}.csv"
    local_csv_path = f"/tmp/{csv_filename}"

    create_csv(results, local_csv_path)

    # Upload CSV
    s3.upload_file(
        local_csv_path,
        OUTPUT_BUCKET,
        f"reports/csv/{csv_filename}"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Processed successfully",
            "csv_file": csv_filename
        })
    }