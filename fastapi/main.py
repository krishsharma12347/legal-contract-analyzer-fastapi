import joblib
import pdfplumber
import re
import numpy as np
from collections import defaultdict
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

# ✅ FastAPI app
app = FastAPI()

# ✅ CORS setup (React frontend ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development ke liye sab origins allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load model + vectorizer
model = joblib.load("contract_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

# ✅ Functions
def extract_text_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    return full_text

def analyze_contract_professional(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    paragraphs = re.split(r'\n(?=[A-Z0-9])', text)
    category_map = defaultdict(list)

    for para in paragraphs:
        cleaned = para.strip()
        if len(cleaned) > 60:
            vec = vectorizer.transform([cleaned])
            probs = model.predict_proba(vec)
            prediction = model.classes_[np.argmax(probs)]
            confidence = np.max(probs)
            if confidence > 0.5:
                category_map[prediction].append({
                    "text": cleaned,
                    "confidence": round(float(confidence), 2)
                })
    return category_map

def generate_risk_analysis(category_map):
    critical_clauses = ["Termination", "Liability", "Legal"]
    important_clauses = ["Restrictive", "Intellectual Property"]

    risk_score = 0
    missing = []

    for clause in critical_clauses:
        if clause not in category_map:
            risk_score += 2
            missing.append(clause)

    for clause in important_clauses:
        if clause not in category_map:
            risk_score += 1
            missing.append(clause)

    if risk_score >= 5:
        risk_level = "HIGH RISK"
    elif risk_score >= 3:
        risk_level = "MEDIUM RISK"
    else:
        risk_level = "LOW RISK"

    return risk_level, missing

# ✅ FastAPI route
@app.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    with open("temp.pdf", "wb") as f:
        f.write(contents)

    category_map = analyze_contract_professional("temp.pdf")
    risk_level, missing = generate_risk_analysis(category_map)

    return {
        "categories": category_map,
        "risk_level": risk_level,
        "missing_clauses": missing
    }





#   uvicorn main:app --reload --port 8000