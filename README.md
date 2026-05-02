# 📄 PDF Accessibility Checker (Serverless)

A cloud-based serverless application that analyzes PDF files for accessibility compliance by checking key attributes like Title, Language, and Tagging structure.

Users can upload single PDFs or ZIP files via a web UI, and the system automatically processes them and generates structured reports (CSV + JSON).

---

## 🚀 Features

- 📤 Upload PDF or ZIP files via UI
- 🔍 Automated accessibility checks:
  - Title metadata
  - Language (`/Lang`)
  - Tagged structure (`/StructTreeRoot`)
- 📦 Supports bulk processing (ZIP files)
- 📊 Generates:
  - JSON report (per file)
  - CSV report (per upload batch)
- 🔐 Secure uploads using pre-signed URLs
- ⚡ Fully serverless and scalable
- 🔄 CI/CD enabled using GitHub Actions

---

## 🏗️ Architecture
User (Browser UI)
↓
API Gateway
↓
Lambda (Upload URL Generator)
↓
S3 (Input Bucket)
↓ (Event Trigger)
Lambda (PDF Processor - Dockerized)
↓
S3 (Output Bucket: CSV + JSON)
↓
Lambda (Download Latest Report)
↓
UI (Download CSV)

---

## 🛠️ Tech Stack

- **Frontend:** HTML, JavaScript, Bootstrap
- **Backend:** AWS Lambda (Python)
- **Storage:** Amazon S3
- **API Layer:** API Gateway
- **PDF Processing:** PyPDF2
- **Containerization:** Docker
- **CI/CD:** GitHub Actions + Amazon ECR

---

## 📂 Project Structure
.
├── app.py # Lambda processing logic
├── Dockerfile # Container setup
├── requirements.txt # Python dependencies
├── index.html # UI
├── .github/workflows/ # CI/CD pipeline
└── README.md

---

## ⚙️ How It Works

1. User uploads PDF/ZIP via UI
2. API Gateway → Lambda generates pre-signed S3 URL
3. File uploaded directly to S3 (input bucket)
4. S3 triggers Lambda
5. Lambda:
   - Extracts metadata
   - Processes PDFs
   - Generates JSON + CSV
6. Output stored in S3 (output bucket)
7. User clicks "Download Latest CSV"

---

## 🔐 Security

- Pre-signed URLs used for secure uploads/downloads
- No direct S3 exposure
- IAM roles control access

---

## 📊 Sample Output

### JSON (per file)
{
  "file": "sample.pdf",
  "title": "Document Title",
  "language": "en-US",
  "tagged": "Yes",
  "status": "Passed"
}

### CSV (per batch)
File Name,Title,Language,Tagged,Status
sample.pdf,Document Title,en-US,Yes,Passed

---

🚀 Deployment (CI/CD)
- Code pushed to GitHub
- GitHub Actions:
  - Builds Docker image
  - Pushes to Amazon ECR
  - Updates Lambda automatically
    
---

🧪 How to Run UI Locally
python -m http.server 8000
   
---

Then open:
http://localhost:8000
   
--- 

📌 Future Improvements
- Job tracking system
- Progress indicator in UI
- Authentication layer
- File size validation
- Retry mechanism (SQS / DLQ)
