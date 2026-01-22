from flask import Blueprint, render_template, request
import os
from services.resume_service import process_resume
from models.resume_model import insert_resume

applicant_bp = Blueprint("applicant", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def is_completely_invalid_resume(result):
    return (
        not result.get("email") and
        not result.get("mobile") and
        result.get("tenth") is None and
        result.get("twelfth") is None
    )

@applicant_bp.route("/upload")
def upload_page():
    return render_template("upload.html")

@applicant_bp.route("/submit", methods=["POST"])
def submit_resume():
    file = request.files["resume"]
    experience = request.form["experience"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    result = process_resume(path, experience)

    if is_completely_invalid_resume(result):
        os.remove(path)
        return render_template(
            "upload.html",
            message="Invalid document uploaded. Please upload a valid resume.",
            msg_type="error"
        )

    data = {
        "resume_name": file.filename,
        "resume_text": result["resume_text"],
        "email": result["email"],
        "mobile": result["mobile"],
        "skills": result["skills"],
        "tenth": result["tenth"],
        "twelfth": result["twelfth"],
        "job_role": result["job_role"],
        "experience": experience,
        "score": result["score"]
    }

    insert_resume(data)

    return render_template(
        "upload.html",
        message="Resume uploaded successfully!",
        info_message="You will be notified via email once your profile is reviewed.",
        msg_type="success",
        job_role=result["job_role"]
    )