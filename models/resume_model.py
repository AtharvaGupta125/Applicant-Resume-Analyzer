import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

def insert_resume(data):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO resumes
        (resume_name, resume_text, email, mobile, skills,
         tenth_percentage, twelfth_percentage,
         job_role, experience, score)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["resume_name"],
        data["resume_text"],
        data["email"],
        data["mobile"],
        data["skills"],
        data["tenth"],
        data["twelfth"],
        data["job_role"],
        data["experience"],
        data["score"]
    ))
    db.commit()

def get_all_resumes():
    cursor = db.cursor()
    cursor.execute("""
        SELECT resume_name, email, mobile, skills,
            tenth_percentage, twelfth_percentage,
            job_role, experience, score, uploaded_at
        FROM resumes
        ORDER BY score DESC
    """)
    return cursor.fetchall()

def get_distinct_job_roles():
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT job_role FROM resumes")
    return [r[0] for r in cursor.fetchall()]

def get_filtered_resumes(job_role=None, min_exp=None, sort_by="score", page=1, per_page=10):
    offset = (page - 1) * per_page
    cursor = db.cursor()

    query = """
        SELECT resume_name, email, mobile, skills,
               tenth_percentage, twelfth_percentage,
               job_role, experience, score, uploaded_at
        FROM resumes
        WHERE 1=1
    """
    params = []

    # Filter by job role
    if job_role:
        query += " AND job_role = %s"
        params.append(job_role)

    # ✅ UPDATED EXPERIENCE FILTER
    if min_exp is not None:
        if min_exp == 0:
            # Fresher = 0 to 2 years
            query += " AND experience BETWEEN %s AND %s"
            params.extend([0, 2])
        else:
            # Experienced candidates (2+ or 5+)
            query += " AND experience >= %s"
            params.append(min_exp)

    # Sorting
    if sort_by == "experience":
        query += " ORDER BY experience DESC"
    else:
        query += " ORDER BY score DESC"

    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, tuple(params))
    return cursor.fetchall()

def get_analysis_overview():
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_resumes,
            COUNT(DISTINCT job_role) AS total_roles,
            ROUND(AVG(score), 2) AS avg_score
        FROM resumes
    """)
    return cursor.fetchone()

def get_job_role_distribution():
    cursor = db.cursor()
    cursor.execute("""
        SELECT job_role, COUNT(*) 
        FROM resumes
        GROUP BY job_role
    """)
    return cursor.fetchall()

def get_score_distribution():
    cursor = db.cursor()
    cursor.execute("SELECT score FROM resumes WHERE score IS NOT NULL")
    return [float(r[0]) for r in cursor.fetchall()]

def get_experience_vs_score():
    cursor = db.cursor()
    cursor.execute("""
        SELECT experience, score FROM resumes
    """)
    return cursor.fetchall()

def get_top_skills():
    cursor = db.cursor()
    cursor.execute("SELECT skills FROM resumes WHERE skills IS NOT NULL")
    skills = []

    for row in cursor.fetchall():
        if row[0]:
            skills.extend(
                [s.strip() for s in row[0].split(",") if s.strip()]
            )

    return skills