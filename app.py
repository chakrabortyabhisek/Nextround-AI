import html
from statistics import mean

import streamlit as st

from db import init_db, save_report
from evaluator import evaluate_interview
from transcribe import transcribe_file


st.set_page_config(
    page_title="NextRound AI — Interview Coach",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def theme_switch(label: str) -> bool:
    """Use the modern toggle where available and gracefully support older Streamlit."""
    if hasattr(st, "toggle"):
        return st.toggle(label, key="dark_mode")
    return st.checkbox(label, key="dark_mode")


def inject_styles(dark_mode: bool) -> None:
    if dark_mode:
        colors = {
            "bg": "#080b12",
            "bg_rgb": "8, 11, 18",
            "surface": "rgba(18, 23, 35, 0.82)",
            "surface_solid": "#121723",
            "surface_2": "#171d2b",
            "text": "#f4f6fb",
            "muted": "#949db0",
            "border": "rgba(255,255,255,.09)",
            "shadow": "0 22px 70px rgba(0,0,0,.35)",
            "input": "rgba(255,255,255,.045)",
            "scheme": "dark",
            "header": "rgba(8,11,18,.72)",
        }
    else:
        colors = {
            "bg": "#f8f9fd",
            "bg_rgb": "248, 249, 253",
            "surface": "rgba(255, 255, 255, 0.9)",
            "surface_solid": "#ffffff",
            "surface_2": "#f0f2f8",
            "text": "#101322",
            "muted": "#60697b",
            "border": "rgba(31,38,58,.12)",
            "shadow": "0 22px 70px rgba(40,48,76,.11)",
            "input": "#fbfcff",
            "scheme": "light",
            "header": "rgba(248,249,253,.76)",
        }

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

        :root {{
            --app-bg: {colors["bg"]};
            --surface: {colors["surface"]};
            --surface-solid: {colors["surface_solid"]};
            --surface-2: {colors["surface_2"]};
            --text: {colors["text"]};
            --muted: {colors["muted"]};
            --border: {colors["border"]};
            --shadow: {colors["shadow"]};
            --input: {colors["input"]};
            --violet: #7c5cff;
            --cyan: #20d5ec;
            --lime: #b8f34a;
            color-scheme: {colors["scheme"]};
        }}

        html, body, [class*="css"] {{
            font-family: "DM Sans", sans-serif;
            color: var(--text) !important;
            background: var(--app-bg) !important;
        }}
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            background:
                radial-gradient(circle at 10% 5%, rgba(124,92,255,.14), transparent 26rem),
                radial-gradient(circle at 90% 0%, rgba(32,213,236,.10), transparent 23rem),
                var(--app-bg) !important;
            color: var(--text) !important;
            transition: background .45s ease, color .35s ease;
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: .3;
            background-image: linear-gradient(var(--border) 1px, transparent 1px),
                              linear-gradient(90deg, var(--border) 1px, transparent 1px);
            background-size: 72px 72px;
            mask-image: linear-gradient(to bottom, black, transparent 55%);
            animation: grid-breathe 9s ease-in-out infinite;
        }}
        .stApp::after {{
            content: "";
            position: fixed;
            z-index: 0;
            width: 27rem;
            aspect-ratio: 1;
            right: -10rem;
            top: 38%;
            pointer-events: none;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(124,92,255,.14), rgba(32,213,236,.04) 45%, transparent 70%);
            filter: blur(8px);
            animation: ambient-float 13s ease-in-out infinite alternate;
        }}
        header[data-testid="stHeader"] {{
            background: {colors["header"]} !important;
            backdrop-filter: blur(16px);
            transition: background .4s ease;
            height: 3.75rem;
        }}
        [data-testid="stToolbar"], [data-testid="stDecoration"] {{
            color: var(--text) !important;
            background: transparent !important;
        }}
        #MainMenu, footer {{ visibility: hidden; }}
        .block-container {{
            position: relative;
            z-index: 1;
            max-width: 1180px;
            padding-top: 5.25rem;
            padding-bottom: 5rem;
        }}
        h1, h2, h3, h4, h5, h6 {{ font-family: "Manrope", sans-serif !important; color: var(--text) !important; }}
        p, label, .stMarkdown, .stText, [data-testid="stCaptionContainer"],
        [data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"] {{
            color: var(--text) !important;
        }}
        [data-testid="stCaptionContainer"], small {{ color: var(--muted) !important; }}

        .topbar {{
            display: flex;
            align-items: center;
            gap: .75rem;
            padding: .3rem 0 3.8rem;
            animation: enter .65s ease both;
        }}
        .brand-mark {{
            display: grid;
            place-items: center;
            width: 2.25rem;
            height: 2.25rem;
            border-radius: .75rem;
            color: #090b10;
            font: 800 .72rem/1 "Manrope", sans-serif;
            letter-spacing: -.03em;
            background: linear-gradient(135deg, var(--lime), var(--cyan));
            box-shadow: 0 0 28px rgba(32,213,236,.22);
            animation: mark-float 4.5s ease-in-out infinite;
        }}
        .brand-name {{
            font: 800 1.08rem/1 "Manrope", sans-serif;
            letter-spacing: -.03em;
        }}
        .brand-pill {{
            margin-left: .2rem;
            padding: .28rem .52rem;
            border: 1px solid var(--border);
            border-radius: 2rem;
            color: var(--muted);
            font-size: .67rem;
            font-weight: 700;
            letter-spacing: .08em;
        }}
        .hero {{ max-width: 900px; margin: 0 auto 2.4rem; text-align: center; }}
        .eyebrow {{
            display: inline-flex;
            align-items: center;
            gap: .5rem;
            padding: .42rem .72rem;
            border: 1px solid var(--border);
            border-radius: 2rem;
            background: var(--surface);
            color: var(--muted);
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
            animation: enter .65s .08s ease both;
        }}
        .pulse-dot {{
            width: .45rem; height: .45rem; border-radius: 50%;
            background: var(--lime); box-shadow: 0 0 0 0 rgba(184,243,74,.5);
            animation: pulse 2s infinite;
        }}
        .hero h1 {{
            max-width: 850px;
            margin: 1.25rem auto .9rem;
            font-size: clamp(2.65rem, 6vw, 5.2rem);
            line-height: .99;
            letter-spacing: -.065em;
            animation: enter .7s .13s ease both;
        }}
        .gradient-text {{
            background: linear-gradient(100deg, var(--violet), var(--cyan) 52%, #55dfaf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 180% auto;
            animation: shimmer 5s linear infinite;
        }}
        .hero-copy {{
            max-width: 650px; margin: 0 auto; color: var(--muted) !important;
            font-size: 1.05rem; line-height: 1.7;
            animation: enter .7s .2s ease both;
        }}
        .trust-row {{
            display: flex; justify-content: center; flex-wrap: wrap; gap: 1.25rem;
            margin-top: 1.35rem; color: var(--muted); font-size: .78rem;
            animation: enter .7s .27s ease both;
        }}
        .trust-row span::before {{ content: "✓"; margin-right: .35rem; color: #55dfaf; }}

        [data-testid="stVerticalBlockBorderWrapper"]:has(.input-panel-marker) {{
            border: 1px solid var(--border) !important;
            border-radius: 1.4rem !important;
            background: var(--surface);
            backdrop-filter: blur(20px);
            box-shadow: var(--shadow);
            animation: panel-enter .8s .3s cubic-bezier(.2,.8,.2,1) both;
            transition: background .4s ease, border-color .4s ease, box-shadow .4s ease;
        }}
        .input-panel-marker {{
            width: 0;
            height: 0;
            overflow: hidden;
            position: absolute;
            pointer-events: none;
        }}
        [data-testid="stFileUploaderDropzone"] {{
            width: 100%;
            min-height: 174px;
            aspect-ratio: 16 / 6.4;
            border: 1px dashed rgba(124,92,255,.42);
            border-radius: 1rem;
            background: linear-gradient(135deg, rgba(124,92,255,.07), rgba(32,213,236,.035));
            transition: transform .25s ease, border-color .25s ease, background .25s ease;
        }}
        [data-testid="stFileUploaderDropzone"]:hover {{
            transform: translateY(-2px);
            border-color: var(--violet);
            background: linear-gradient(135deg, rgba(124,92,255,.12), rgba(32,213,236,.06));
        }}
        textarea {{
            width: 100% !important;
            min-height: 174px !important;
            aspect-ratio: 16 / 6.4;
            border-color: var(--border) !important;
            border-radius: 1rem !important;
            background: var(--input) !important;
            color: var(--text) !important;
        }}
        textarea:focus {{ border-color: var(--violet) !important; box-shadow: 0 0 0 3px rgba(124,92,255,.12) !important; }}
        [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span {{ color: var(--muted) !important; }}
        [data-testid="stFileUploaderDropzone"] button,
        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div {{
            color: var(--text) !important;
            background: var(--surface-solid) !important;
            border-color: var(--border) !important;
        }}
        [data-testid="stToggle"] label, [data-testid="stCheckbox"] label {{ color: var(--text) !important; }}
        [data-baseweb="checkbox"] > div:first-child {{
            background-color: var(--surface-2);
            border-color: var(--border);
        }}
        div.stButton > button {{
            min-height: 3.25rem;
            border: 0;
            border-radius: .9rem;
            background: linear-gradient(100deg, #6c4dff, #8f6cff 52%, #3ecbdd);
            background-size: 180% auto;
            color: white;
            font-weight: 800;
            box-shadow: 0 12px 28px rgba(108,77,255,.25);
            transition: transform .2s ease, box-shadow .2s ease, background-position .4s ease;
        }}
        div.stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 16px 34px rgba(108,77,255,.34);
            background-position: right center;
            color: white;
        }}
        div.stButton > button:active {{ transform: translateY(0) scale(.99); }}
        [data-testid="stAlert"] {{ border-radius: 1rem; border: 1px solid var(--border); }}
        [data-testid="stAlert"], [data-baseweb="notification"] {{
            color: var(--text) !important;
            background: var(--surface-solid) !important;
        }}

        .section-head {{ margin: 4.3rem 0 1.2rem; }}
        .section-kicker {{ color: var(--violet); font-size: .7rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }}
        .section-head h2 {{ margin: .35rem 0 0; font-size: clamp(1.8rem, 3vw, 2.55rem); letter-spacing: -.045em; }}
        [data-testid="stMetric"] {{
            min-height: 132px;
            padding: 1.1rem 1.2rem;
            border: 1px solid var(--border);
            border-radius: 1.1rem;
            background: var(--surface);
            box-shadow: var(--shadow);
            transition: transform .22s ease, border-color .22s ease;
        }}
        [data-testid="stMetric"]:hover {{ transform: translateY(-3px); border-color: rgba(124,92,255,.35); }}
        [data-testid="stMetricLabel"] {{ color: var(--muted) !important; }}
        [data-testid="stMetricValue"] {{ color: var(--text); font-family: "Manrope", sans-serif; }}
        .summary-card {{
            padding: 1.35rem 1.45rem;
            border: 1px solid var(--border);
            border-radius: 1.15rem;
            background: var(--surface);
            color: var(--text);
            line-height: 1.75;
            box-shadow: var(--shadow);
        }}
        [data-testid="stExpander"] {{
            margin-bottom: .75rem;
            border: 1px solid var(--border) !important;
            border-radius: 1rem !important;
            background: var(--surface) !important;
            overflow: hidden;
        }}
        [data-testid="stExpander"] summary:hover {{ color: var(--violet); }}
        .topic-wrap {{ display: flex; flex-wrap: wrap; gap: .5rem; margin: .6rem 0; }}
        .topic {{
            padding: .38rem .65rem; border-radius: 2rem;
            background: rgba(124,92,255,.11); border: 1px solid rgba(124,92,255,.18);
            color: var(--text); font-size: .76rem; font-weight: 600;
        }}
        .score-label {{ color: var(--muted); font-size: .75rem; margin-bottom: .25rem; }}
        [data-testid="stProgressBar"] > div > div {{ background: linear-gradient(90deg, var(--violet), var(--cyan)); }}
        [data-baseweb="tab-list"] {{ gap: .35rem; background: var(--surface-2); padding: .35rem; border-radius: .85rem; }}
        [data-baseweb="tab"] {{ border-radius: .65rem; padding-left: 1rem; padding-right: 1rem; color: var(--text) !important; }}
        [aria-selected="true"] {{ background: var(--surface-solid) !important; box-shadow: 0 3px 12px rgba(0,0,0,.08); }}
        .plan-step {{
            display: grid; grid-template-columns: 2.35rem 1fr; gap: .85rem;
            padding: .9rem 0; border-bottom: 1px solid var(--border);
            color: var(--text); align-items: start;
        }}
        .step-number {{
            width: 2.25rem; height: 2.25rem; display: grid; place-items: center;
            border-radius: .7rem; background: linear-gradient(135deg, rgba(124,92,255,.2), rgba(32,213,236,.14));
            color: var(--violet); font: 800 .78rem "Manrope", sans-serif;
        }}
        .footer-note {{
            margin-top: 4rem;
            text-align: center;
            font: 800 clamp(.86rem, 1.5vw, 1.05rem)/1.4 "Manrope", sans-serif;
            letter-spacing: .025em;
            background: linear-gradient(90deg, #7c5cff, #20d5ec, #55dfaf, #f7c94b, #ff6b9d, #7c5cff);
            background-size: 300% auto;
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            color: transparent;
            animation: footer-colors 6s linear infinite;
        }}

        @keyframes enter {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes panel-enter {{ from {{ opacity: 0; transform: translateY(24px) scale(.985); }} to {{ opacity: 1; transform: translateY(0) scale(1); }} }}
        @keyframes shimmer {{ to {{ background-position: 180% center; }} }}
        @keyframes pulse {{ 70% {{ box-shadow: 0 0 0 7px rgba(184,243,74,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(184,243,74,0); }} }}
        @keyframes mark-float {{ 0%, 100% {{ transform: translateY(0) rotate(0); }} 50% {{ transform: translateY(-4px) rotate(7deg); }} }}
        @keyframes ambient-float {{ from {{ transform: translate3d(0,-4%,0) scale(.94); }} to {{ transform: translate3d(-14%,8%,0) scale(1.08); }} }}
        @keyframes grid-breathe {{ 0%, 100% {{ opacity: .22; }} 50% {{ opacity: .38; }} }}
        @keyframes footer-colors {{ to {{ background-position: 300% center; }} }}
        @media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation: none !important; transition: none !important; }} }}
        @media (max-width: 700px) {{
            .block-container {{ width: 100%; max-width: 100%; padding: 4.75rem 1rem 3rem; }}
            .topbar {{ padding-bottom: 2.5rem; }}
            .brand-pill {{ display: none; }}
            .hero {{ width: 100%; max-width: 100%; margin-bottom: 1.8rem; }}
            .hero h1 {{ max-width: 100%; font-size: clamp(2.35rem, 12vw, 3.3rem); line-height: 1.02; }}
            .hero-copy {{ max-width: 34rem; font-size: .95rem; line-height: 1.6; }}
            .trust-row {{ gap: .6rem 1rem; }}
            .section-head {{ margin-top: 3rem; }}
            [data-testid="stFileUploaderDropzone"], textarea {{
                width: 100% !important;
                min-height: 142px !important;
                aspect-ratio: 16 / 6.4;
            }}
            [data-testid="stVerticalBlockBorderWrapper"]:has(.input-panel-marker) {{ border-radius: 1.1rem !important; }}
            [data-testid="stMetric"] {{ min-height: 112px; }}
            [data-baseweb="tab-list"] {{ width: 100%; overflow-x: auto; }}
            [data-baseweb="tab"] {{ flex: 1 0 auto; padding-left: .7rem; padding-right: .7rem; }}
            .stApp::after {{ width: 18rem; right: -11rem; }}
        }}
        @media (max-width: 420px) {{
            .block-container {{ padding-left: .8rem; padding-right: .8rem; }}
            .hero h1 {{ font-size: 2.35rem; }}
            .eyebrow {{ font-size: .62rem; letter-spacing: .06em; }}
            .trust-row {{ font-size: .7rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_text(value, fallback: str = "") -> str:
    return html.escape(str(value if value is not None else fallback))


def score_value(question: dict) -> float:
    raw = question.get("score_overall", question.get("score", 0))
    try:
        return max(0.0, min(10.0, float(raw)))
    except (TypeError, ValueError):
        return 0.0


def render_report(report: dict, transcript: str) -> None:
    questions = report.get("questions") or []
    scores = [score_value(question) for question in questions]
    average = mean(scores) if scores else 0
    weak_topics = report.get("weak_topics") or []

    st.markdown(
        """
        <div class="section-head">
            <div class="section-kicker">Your debrief</div>
            <h2>Signal, not noise.</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Overall score", f"{average:.1f}/10" if scores else "—")
    metric_2.metric("Questions reviewed", len(questions))
    metric_3.metric("Focus areas", len(weak_topics))
    metric_4.metric("Action plan", f"{len(report.get('study_plan') or [])} steps")

    st.markdown("#### Executive summary")
    st.markdown(
        f'<div class="summary-card">{safe_text(report.get("summary"), "No summary was returned.")}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Question-by-question")
    if not questions:
        st.info("No individual questions were detected in this transcript.")
    for index, question in enumerate(questions, start=1):
        title = question.get("question") or f"Question {index}"
        overall = score_value(question)
        with st.expander(f"{index:02d}  ·  {title}", expanded=index == 1):
            score_columns = st.columns(3)
            scoring = [
                ("Overall", overall),
                ("Technical", question.get("score_technical", overall)),
                ("Communication", question.get("score_communication", overall)),
            ]
            for column, (label, raw_score) in zip(score_columns, scoring):
                try:
                    numeric_score = max(0.0, min(10.0, float(raw_score)))
                except (TypeError, ValueError):
                    numeric_score = 0.0
                with column:
                    st.markdown(f'<div class="score-label">{label} · {numeric_score:g}/10</div>', unsafe_allow_html=True)
                    st.progress(numeric_score / 10)

            if question.get("answer_excerpt"):
                st.caption("ANSWER SNAPSHOT")
                st.write(question["answer_excerpt"])
            st.caption("COACH'S FEEDBACK")
            st.write(question.get("feedback") or "No feedback returned.")
            topics = question.get("topics") or []
            if topics:
                topic_html = "".join(f'<span class="topic">{safe_text(topic)}</span>' for topic in topics)
                st.markdown(f'<div class="topic-wrap">{topic_html}</div>', unsafe_allow_html=True)

    plan_tab, focus_tab, follow_up_tab = st.tabs(["7-day plan", "Focus areas", "Follow-ups"])
    with plan_tab:
        plan = report.get("study_plan") or []
        if plan:
            for index, step in enumerate(plan, start=1):
                st.markdown(
                    f'<div class="plan-step"><div class="step-number">{index:02d}</div>'
                    f'<div>{safe_text(step)}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No study plan was returned.")
    with focus_tab:
        if weak_topics:
            topic_html = "".join(f'<span class="topic">{safe_text(topic)}</span>' for topic in weak_topics)
            st.markdown(f'<div class="topic-wrap">{topic_html}</div>', unsafe_allow_html=True)
        else:
            st.caption("No focus areas were identified.")
    with follow_up_tab:
        follow_ups = report.get("follow_ups") or []
        if follow_ups:
            for index, question in enumerate(follow_ups, start=1):
                st.markdown(
                    f'<div class="plan-step"><div class="step-number">{index:02d}</div>'
                    f'<div>{safe_text(question)}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No follow-up questions were generated.")

    st.write("")
    save_col, status_col = st.columns([1, 3])
    with save_col:
        if st.button("Save this report", use_container_width=True):
            init_db()
            save_report(transcript, report)
            st.session_state.report_saved = True
    with status_col:
        if st.session_state.get("report_saved"):
            st.success("Report saved securely to your local database.")


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "report" not in st.session_state:
    st.session_state.report = None
if "report_transcript" not in st.session_state:
    st.session_state.report_transcript = ""

inject_styles(st.session_state.dark_mode)

brand_col, theme_col = st.columns([8.2, 1.8])
with brand_col:
    st.markdown(
        """
        <div class="topbar">
            <div class="brand-mark">AC</div>
            <div class="brand-name">NextRound AI</div>
            <div class="brand-pill">BETA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with theme_col:
    theme_switch("Dark mode")

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow"><span class="pulse-dot"></span> AI-powered interview intelligence</div>
        <h1>Turn every interview into your <span class="gradient-text">next advantage.</span></h1>
        <p class="hero-copy">
            Upload your interview or paste the transcript. Get a sharp, structured debrief
            with answer scoring, candid feedback, and a practice plan built around you.
        </p>
        <div class="trust-row">
            <span>Private by design</span>
            <span>Actionable feedback</span>
            <span>Personalized roadmap</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown('<span class="input-panel-marker"></span>', unsafe_allow_html=True)
    st.markdown("### Start your debrief")
    st.caption("Choose either option. Your audio and transcript stay within your configured environment.")
    upload_col, transcript_col = st.columns(2, gap="large")
    with upload_col:
        uploaded_file = st.file_uploader(
            "Drop in your interview recording",
            type=["mp3", "wav", "m4a"],
            help="Supported formats: MP3, WAV, and M4A",
        )
    with transcript_col:
        transcript_input = st.text_area(
            "Or paste your transcript",
            placeholder="Interviewer: Tell me about a challenging project...\n\nYou: In my last role...",
            label_visibility="visible",
        )

    analyze_col, helper_col = st.columns([1.15, 2.85])
    with analyze_col:
        analyze_clicked = st.button("Analyze interview  →", type="primary", use_container_width=True)
    with helper_col:
        st.caption("Usually takes under a minute · Results appear below")

if analyze_clicked:
    if not uploaded_file and not transcript_input.strip():
        st.warning("Add an audio file or paste a transcript to begin.")
    else:
        with st.spinner("Listening for the signal in your interview…"):
            try:
                transcript = transcript_input.strip()
                if uploaded_file and not transcript:
                    transcript = transcribe_file(uploaded_file)
                st.session_state.report = evaluate_interview(transcript)
                st.session_state.report_transcript = transcript
                st.session_state.report_saved = False
            except Exception as exc:
                st.error("The analysis could not be completed. Check your model configuration and try again.")
                st.exception(exc)

if st.session_state.report:
    render_report(st.session_state.report, st.session_state.report_transcript)

st.markdown(
    '<div class="footer-note">Built by ABHISEK &amp; COMPANY</div>',
    unsafe_allow_html=True,
)
