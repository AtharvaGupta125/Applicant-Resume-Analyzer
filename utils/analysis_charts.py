import matplotlib
matplotlib.use("Agg")

import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid")

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close(fig)
    return img

def job_role_distribution_chart(job_role_dist):
    df = pd.DataFrame(job_role_dist, columns=["Job Role", "Count"])

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(data=df, x="Count", y="Job Role", ax=ax)
    # ax.set_title("Job Role Distribution")

    return fig_to_base64(fig)

def score_distribution_chart(scores):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(scores, bins=10, kde=True, ax=ax)
    # ax.set_title("Score Distribution")
    ax.set_xlabel("Score")

    return fig_to_base64(fig)

def experience_vs_score_chart(exp_score):
    df = pd.DataFrame(exp_score, columns=["Experience", "Score"])

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(data=df, x="Experience", y="Score", ax=ax)
    # ax.set_title("Experience vs Score")

    return fig_to_base64(fig)

def top_skills_chart(skills):
    skill_counts = pd.Series(skills).value_counts().head(10)

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        x=skill_counts.values,
        y=skill_counts.index,
        ax=ax
    )

    # ax.set_title("Top Skills")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Skill")

    return fig_to_base64(fig)