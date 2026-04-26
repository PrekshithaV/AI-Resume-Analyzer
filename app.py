import streamlit as st
import httpx
import json
from pathlib import Path

# ── Config ────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
  .main-title { font-size: 2.6rem; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
  .sub-title  { font-size: 1.1rem; color: #555; margin-bottom: 2rem; }

  /* Score ring */
  .score-card { text-align: center; padding: 1.5rem; border-radius: 16px; 
                background: #f8f9ff; border: 1px solid #e0e4ff; }
  .score-number { font-size: 4rem; font-weight: 800; line-height: 1; }
  .score-label  { font-size: 0.9rem; color: #666; margin-top: 4px; }

  /* Verdict badges */
  .badge-excellent { background:#d4edda; color:#155724; padding:4px 14px; border-radius:20px; font-weight:600; font-size:.85rem; }
  .badge-good      { background:#cce5ff; color:#004085; padding:4px 14px; border-radius:20px; font-weight:600; font-size:.85rem; }
  .badge-average   { background:#fff3cd; color:#856404; padding:4px 14px; border-radius:20px; font-weight:600; font-size:.85rem; }
  .badge-poor      { background:#f8d7da; color:#721c24; padding:4px 14px; border-radius:20px; font-weight:600; font-size:.85rem; }

  /* Skill chips */
  .skill-chip-green { display:inline-block; background:#d4edda; color:#155724; padding:3px 12px;
                      border-radius:20px; font-size:.82rem; margin:3px; }
  .skill-chip-red   { display:inline-block; background:#f8d7da; color:#721c24; padding:3px 12px;
                      border-radius:20px; font-size:.82rem; margin:3px; }

  /* Importance badges */
  .imp-high   { background:#f8d7da; color:#721c24; border-radius:8px; padding:2px 8px; font-size:.75rem; }
  .imp-medium { background:#fff3cd; color:#856404; border-radius:8px; padding:2px 8px; font-size:.75rem; }
  .imp-low    { background:#d4edda; color:#155724; border-radius:8px; padding:2px 8px; font-size:.75rem; }

  /* Improvement cards */
  .imp-card { background:#fff; border:1px solid #e5e7eb; border-left: 4px solid #6366f1;
              border-radius:10px; padding:14px 18px; margin-bottom:12px; }
  .strength-item { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px;
                   padding:10px 16px; margin-bottom:8px; }

  div[data-testid="stFileUploader"] { border: 2px dashed #6366f1; border-radius: 12px; padding: 1rem; }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────
st.markdown('<div class="main-title">📄 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Get an instant ATS score, skill gap analysis, and personalized improvement suggestions.</div>', unsafe_allow_html=True)
st.divider()


# ── Input Section ─────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📁 Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Supports PDF and DOCX",
        type=["pdf", "docx"],
        help="Maximum file size: 5 MB",
    )

with col_right:
    st.subheader("🎯 Target Job Role")
    job_role = st.text_input(
        "Enter the job role you're applying for",
        placeholder="e.g. Senior Python Developer, Data Scientist, Product Manager",
        max_chars=200,
    )
    st.caption("Be specific — include level and domain for best results.")

st.markdown("")
analyze_btn = st.button("🚀 Analyze Resume", type="primary", use_container_width=True,
                         disabled=not (uploaded_file and job_role))


# ── Analysis ──────────────────────────────────────────────────
def badge(verdict: str) -> str:
    cls = f"badge-{verdict.lower()}"
    return f'<span class="{cls}">{verdict}</span>'


def importance_badge(level: str) -> str:
    return f'<span class="imp-{level.lower()}">{level.upper()}</span>'


def do_analysis(file, role: str):
    with st.spinner("🤖 Analyzing your resume with AI... this may take 15-30 seconds"):
        try:
            response = httpx.post(
                f"{BACKEND_URL}/analyze/",
                files={"file": (file.name, file.getvalue(), file.type)},
                data={"job_role": role},
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            detail = e.response.json().get("detail", str(e))
            st.error(f"❌ Analysis failed: {detail}")
            return None
        except httpx.ConnectError:
            st.error("❌ Cannot connect to the backend. Make sure FastAPI is running on port 8000.")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None


def render_results(data: dict):
    ats = data["ats_score"]
    match = data["job_match_percent"]
    verdict = data["ats_verdict"]

    st.divider()
    st.subheader("📊 Analysis Results")

    # ── Score row ──
    c1, c2, c3 = st.columns(3)
    with c1:
        color = "#22c55e" if ats >= 80 else "#f59e0b" if ats >= 60 else "#ef4444"
        st.markdown(f"""
        <div class="score-card">
          <div class="score-number" style="color:{color}">{ats}</div>
          <div class="score-label">ATS Score / 100</div>
          <div style="margin-top:8px">{badge(verdict)}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        mcolor = "#22c55e" if match >= 80 else "#f59e0b" if match >= 60 else "#ef4444"
        st.markdown(f"""
        <div class="score-card">
          <div class="score-number" style="color:{mcolor}">{match}%</div>
          <div class="score-label">Job Match</div>
          <div style="margin-top:8px;font-size:.85rem;color:#555">for: {job_role[:40]}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        n_missing = len(data["missing_skills"])
        n_matched = len(data["matched_skills"])
        st.markdown(f"""
        <div class="score-card">
          <div class="score-number" style="color:#6366f1">{n_matched}</div>
          <div class="score-label">Skills Matched</div>
          <div style="margin-top:8px;font-size:.85rem;color:#e44">
            {n_missing} skills missing
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Summary ──
    st.markdown("")
    st.info(f"💬 **AI Summary:** {data['summary']}")

    # ── Skills ──
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["✅ Matched Skills", "❌ Missing Skills", "🛠 Improvements", "💪 Strengths"])

    with tab1:
        if data["matched_skills"]:
            chips = " ".join(f'<span class="skill-chip-green">✓ {s}</span>' for s in data["matched_skills"])
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.warning("No matching skills detected.")

    with tab2:
        for item in data["missing_skills"]:
            imp = importance_badge(item["importance"])
            st.markdown(f"""
            <div class="imp-card">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <strong>{item['skill']}</strong> {imp}
              </div>
              <div style="color:#555;font-size:.9rem">💡 {item['suggestion']}</div>
            </div>""", unsafe_allow_html=True)

    with tab3:
        for item in data["improvements"]:
            st.markdown(f"""
            <div class="imp-card">
              <div style="font-weight:600;margin-bottom:4px">📌 {item['section']}</div>
              <div style="color:#c0392b;font-size:.9rem;margin-bottom:4px">⚠ {item['issue']}</div>
              <div style="color:#2c7a3a;font-size:.9rem">✅ {item['recommendation']}</div>
            </div>""", unsafe_allow_html=True)

    with tab4:
        for s in data["strengths"]:
            st.markdown(f'<div class="strength-item">✅ {s}</div>', unsafe_allow_html=True)

    # ── Download JSON ──
    st.markdown("---")
    st.download_button(
        label="⬇ Download Full Report (JSON)",
        data=json.dumps(data, indent=2),
        file_name="resume_analysis_report.json",
        mime="application/json",
    )


# ── Trigger ───────────────────────────────────────────────────
if analyze_btn and uploaded_file and job_role:
    result = do_analysis(uploaded_file, job_role)
    if result:
        render_results(result)

elif not uploaded_file and not job_role:
    st.markdown("""
    <div style="text-align:center;padding:2rem;color:#888">
      <div style="font-size:3rem">📋</div>
      <div style="font-size:1.1rem;margin-top:1rem">Upload your resume and enter a job role to get started</div>
    </div>""", unsafe_allow_html=True)
