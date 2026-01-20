from flask import Flask, render_template, request
import mysql.connector, os
from resume_utils import process_resume

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mysql@1234",
    database="resume_db"
)

def is_completely_invalid_resume(result):
    return (
        not result.get("email") and
        not result.get("mobile") and
        result.get("tenth") is None and
        result.get("twelfth") is None
    )

# ---------------------------
# APPLICANT PAGE
# ---------------------------
@app.route("/upload")
def upload_page():
    return render_template("upload.html")

@app.route("/submit", methods=["POST"])
def submit_resume():
    file = request.files["resume"]
    experience = request.form["experience"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    result = process_resume(path, experience)

    if is_completely_invalid_resume(result):
        os.remove(path)  # cleanup wrong document
        return (
            "<h3>❌ Invalid document uploaded. "
            "Please upload a valid resume.</h3>"
        )

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO resumes
        (resume_name, resume_text, email, mobile, skills,
         tenth_percentage, twelfth_percentage,
         job_role, experience, score)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        file.filename,
        result["resume_text"],
        result["email"],
        result["mobile"],
        result["skills"],
        result["tenth"],
        result["twelfth"],
        result["job_role"],
        experience,
        result["score"]
    ))
    db.commit()

    return "<h3>✅ Resume uploaded successfully</h3>"

# ---------------------------
# ADMIN PAGE
# ---------------------------
@app.route("/admin")
def admin_page():
    cursor = db.cursor()
    cursor.execute("""
        SELECT resume_name, email, mobile, skills,
            tenth_percentage, twelfth_percentage,
            job_role, experience, score, uploaded_at
        FROM resumes
        ORDER BY score DESC
    """)
    data = cursor.fetchall()
    return render_template("admin.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
