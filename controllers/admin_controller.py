from flask import Blueprint, render_template, redirect, url_for, request, session
import os
from dotenv import load_dotenv

from models.resume_model import (
    get_all_resumes,
    get_filtered_resumes,
    get_distinct_job_roles,
    get_analysis_overview,
    get_job_role_distribution,
    get_score_distribution,
    get_experience_vs_score,
    get_top_skills
)

from utils.analysis_charts import (
    job_role_distribution_chart,
    score_distribution_chart,
    experience_vs_score_chart,
    top_skills_chart
)

load_dotenv()

admin_bp = Blueprint("admin", __name__)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# ================= ADMIN LOGIN =================
@admin_bp.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin.admin_page"))
        else:
            return render_template("admin_login.html", message="Invalid credentials")

    return render_template("admin_login.html")


# ================= ADMIN DASHBOARD (ALL TABS) =================
@admin_bp.route("/admin")
def admin_page():
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))

    # ---------- DATA TAB ----------
    all_data = get_all_resumes()

    # ---------- FILTER TAB ----------
    is_filter = request.args.get("filter") == "1"

    filtered_data = all_data
    selected_role = selected_exp = selected_sort = None

    if is_filter:
        selected_role = request.args.get("job_role")
        selected_exp = request.args.get("min_exp")
        selected_sort = request.args.get("sort", "score")

        filtered_data = get_filtered_resumes(
            job_role=selected_role,
            min_exp=float(selected_exp) if selected_exp else None,
            sort_by=selected_sort
        )

    job_roles = get_distinct_job_roles()

    # ---------- ANALYSIS TAB (SERVER-SIDE VISUALS) ----------
    overview = get_analysis_overview()

    job_role_dist = get_job_role_distribution()
    scores = get_score_distribution()
    exp_score = get_experience_vs_score()
    skills = get_top_skills()

    charts = {
        "job_role": job_role_distribution_chart(job_role_dist),
        "score": score_distribution_chart(scores),
        "exp_score": experience_vs_score_chart(exp_score),
        "skills": top_skills_chart(skills)
    }

    return render_template(
        "admin.html",

        # Data tab
        all_data=all_data,

        # Filter tab
        filtered_data=filtered_data,
        job_roles=job_roles,
        selected_role=selected_role,
        selected_exp=selected_exp,
        selected_sort=selected_sort,
        is_filter=is_filter,

        # Analysis tab
        overview=overview,
        charts=charts
    )


# ================= ADMIN LOGOUT =================
@admin_bp.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin.admin_login"))