import json
from groq import Groq
from backend.config import get_settings
from backend.schemas import AnalysisResult

settings = get_settings()
client = Groq(api_key=settings.openai_api_key)

PROMPT_TEMPLATE = """You are an expert ATS resume coach. Analyze the resume and return ONLY valid JSON.

Return this exact schema:
{{
  "ats_score": <integer 0-100>,
  "ats_verdict": <"Excellent"|"Good"|"Average"|"Poor">,
  "job_match_percent": <integer 0-100>,
  "matched_skills": [<string>, ...],
  "missing_skills": [
    {{"skill": <string>, "importance": <"high"|"medium"|"low">, "suggestion": <string>}}
  ],
  "improvements": [
    {{"section": <string>, "issue": <string>, "recommendation": <string>}}
  ],
  "strengths": [<string>, ...],
  "summary": <string>
}}

Job Role: {job_role}

Resume:
{resume_text}

Return ONLY the JSON object, no extra text."""


async def analyze_resume(resume_text: str, job_role: str) -> AnalysisResult:
    prompt = PROMPT_TEMPLATE.format(
        job_role=job_role,
        resume_text=resume_text[:12000]
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert ATS resume coach. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()

    # Remove markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    return AnalysisResult(**data)