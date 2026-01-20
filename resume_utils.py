import re
import pdfplumber
import spacy
import fasttext
from spacy.matcher import PhraseMatcher
from skills_list import skills_list   # ✅ IMPORTANT

# -----------------------------
# LOAD MODELS
# -----------------------------
nlp = spacy.load("en_core_web_sm")
model = fasttext.load_model("models/resume_fasttext_model.bin")

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

patterns = [nlp(skill) for skill in skills_list]
matcher.add("SKILLS", patterns)

# -----------------------------
# EXTRACTION FUNCTIONS (YOURS)
# -----------------------------
def extract_text_from_resume(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_email(text):
    match = re.search(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text
    )
    return match.group(0) if match else ""

def extract_mobile(text):
    match = re.search(
        r"(?:\+91[-\s]?[6-9]\d{9})|\b[6-9]\d{9}\b", text
    )
    return match.group(0) if match else ""

def extract_skills(text):
    doc = nlp(text.lower())
    matches = matcher(doc)
    found = set([doc[start:end].text for _, start, end in matches])
    return ", ".join(found)

def extract_percentage(text, std):
    text = text.lower().replace("\n", " ").replace("\r", " ")

    if std == 10:
        keywords = (
            r"(10th|10\s*th|tenth|\bx\b|class\s*10|class\s*x\b|class-x\b|"
            r"std\s*10|std\s*x\b|grade\s*10|ssc|sslc|matric|matriculation|"
            r"cbse\s*10|icse\s*10)"
        )
    else:
        keywords = (
            r"(12th|12\s*th|twelfth|\bxii\b|class\s*12|class\s*xii\b|class-xii\b|class\s*x11\b|"
            r"std\s*12|std\s*xii\b|grade\s*12|hsc|higher\s*secondary|intermediate|"
            r"puc|puc\s*ii|cbse\s*12|icse\s*12)"
        )

    patterns = [
        rf"{keywords}([^%]*?)(\d{{2,3}}(?:\.\d+)?)(?=\s*%)",
        rf"{keywords}(.*?)(\d{{2,3}}(?:\.\d+)?)(?=\s*(percent|percentage|pct|per)\b)",
    ]

    MAX_WORD_GAP = 15

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue

        between_words = match.group(2)
        number = match.group(3) if match.lastindex >= 3 else match.group(2)

        if len(between_words.strip().split()) > MAX_WORD_GAP:
            continue

        try:
            num = float(number)
        except:
            continue

        if num < 34 or num > 100:
            continue

        if len(number.split('.')[0]) == 3 and num != 100:
            continue

        return num

    return None

# -----------------------------
# FINAL PROCESS FUNCTION
# -----------------------------
def process_resume(path, experience):
    text = extract_text_from_resume(path)

    skills = extract_skills(text)
    tenth = extract_percentage(text, 10)
    twelfth = extract_percentage(text, 12)

    label, score = model.predict(skills.replace(",", " "), k=1)

    exp_norm = min(float(experience) / 10, 1.0)
    academics = ((tenth or 0) / 100 + (twelfth or 0) / 100) / 2

    final_score = round(
        (exp_norm * 0.55) +
        (score[0] * 0.35) +
        (academics * 0.10),
        2
    ) * 100

    return {
        "resume_text": text,
        "email": extract_email(text),
        "mobile": extract_mobile(text),
        "skills": skills,
        "tenth": tenth,
        "twelfth": twelfth,
        "job_role": label[0].replace("__label__", ""),
        "score": round(final_score, 2)
    }
