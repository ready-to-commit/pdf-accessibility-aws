import json
import boto3
import os
import csv
import datetime
import zipfile
import shutil
from PyPDF2 import PdfReader

s3 = boto3.client('s3')

OUTPUT_BUCKET = "pdf-accessibility-level-1-check-output"
timestamp = datetime.datetime.now().strftime("%Y%m%d")
CSV_KEY = f"reports/csv/report_{timestamp}.csv"


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

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return "Error", "Error", "No", "Failed"


def lambda_handler(event, context):
    print("Lambda triggered")
    print(json.dumps(event))

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    file_path = f"/tmp/{os.path.basename(key)}"
    s3.download_file(bucket, key, file_path)

    print(f"Downloaded file: {file_path}")

    files_to_process = []

    # Handle ZIP
    if key.endswith(".zip"):
        extract_path = "/tmp/extracted"

        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)

        os.makedirs(extract_path)

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.endswith(".pdf"):
                    files_to_process.append(os.path.join(root, file))

    else:
        files_to_process.append(file_path)

    # Process PDFs
    for pdf_file in files_to_process:
        filename = os.path.basename(pdf_file)
        print(f"Processing: {filename}")

        title, language, tagged, status = check_pdf(pdf_file)

        result = {
            "file": filename,
            "title": title,
            "language": language,
            "tagged": tagged,
            "status": status
        }

        # Save JSON
        json_key = f"reports/json/{filename}.json"

        s3.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=json_key,
            Body=json.dumps(result),
            ContentType="application/json"
        )

        print(f"JSON uploaded: {json_key}")


    return {
        "statusCode": 200,
        "body": json.dumps("Processed successfully")
    }