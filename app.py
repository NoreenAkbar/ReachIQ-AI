import streamlit as st
import sys
import os
import json
import importlib

st.set_page_config(
    page_title="ReachIQ AI v2.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp{background-color:#0a0e1a !important}
h1{color:#0ea5e9 !important;font-size:38px !important;font-weight:900 !important;line-height:1.2}
h2{color:#f1f5f9 !important;font-size:26px !important;font-weight:700 !important;margin-top:24px}
h3{color:#0ea5e9 !important;font-size:20px !important;font-weight:700 !important}
p,.stMarkdown p{color:#e2e8f0 !important;font-size:16px !important;line-height:1.8 !important}
li{color:#e2e8f0 !important;font-size:16px !important;line-height:1.8 !important}
label{color:#f1f5f9 !important;font-size:15px !important;font-weight:600 !important}
[data-testid="stSidebar"]{background-color:#020617 !important;
  border-right:1px solid #1e293b !important;min-width:260px}
[data-testid="stSidebar"] p{color:#94a3b8 !important;font-size:14px !important}
[data-testid="stSidebar"] label{color:#f1f5f9 !important;font-size:14px !important}
.stButton>button{background:linear-gradient(135deg,#0ea5e9,#7c3aed) !important;
  color:#fff !important;font-size:16px !important;font-weight:700 !important;
  border:none !important;border-radius:8px !important;
  padding:14px 28px !important;width:100% !important;
  min-height:48px !important;letter-spacing:0.02em}
.stButton>button:hover{opacity:0.88 !important}
.stTextInput input{background-color:#111827 !important;color:#f1f5f9 !important;
  border:1px solid #334155 !important;border-radius:6px !important;
  font-size:15px !important;padding:10px 12px !important}
.stTextArea textarea{background-color:#111827 !important;color:#f1f5f9 !important;
  border:1px solid #334155 !important;border-radius:6px !important;
  font-size:15px !important;padding:10px 12px !important}
[data-testid="metric-container"]{background-color:#111827 !important;
  border:1px solid #1e293b !important;border-radius:10px !important;
  padding:16px !important}
[data-testid="metric-container"] label{color:#94a3b8 !important;
  font-size:13px !important;font-weight:600 !important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{
  color:#0ea5e9 !important;font-size:30px !important;font-weight:900 !important}
.card{background:#111827;border:1px solid #1e293b;border-radius:12px;
  padding:18px;margin:8px 0}
.ok{background:#05966914;border:1px solid #059669;border-radius:8px;
  padding:12px 18px;color:#4ade80 !important;font-weight:700;
  font-size:15px !important;margin:6px 0;display:block}
.warn{background:#d9780614;border:1px solid #d97806;border-radius:8px;
  padding:12px 18px;color:#fbbf24 !important;font-weight:700;
  font-size:15px !important;margin:6px 0;display:block}
.fail{background:#dc262614;border:1px solid #dc2626;border-radius:8px;
  padding:12px 18px;color:#f87171 !important;font-weight:700;
  font-size:15px !important;margin:6px 0;display:block}
.pass-box{background:#111827;border-left:4px solid #0ea5e9;
  border-radius:0 8px 8px 0;padding:14px 18px;margin:8px 0;
  font-size:15px !important;color:#e2e8f0 !important}
hr{border-color:#1e293b !important}
.stSelectbox>div>div{background-color:#111827 !important;
  border:1px solid #334155 !important;color:#f1f5f9 !important;
  font-size:15px !important}
div[data-testid="stExpander"]{background:#111827 !important;
  border:1px solid #1e293b !important;border-radius:8px !important}
div[data-testid="stExpander"] summary{color:#f1f5f9 !important;
  font-size:15px !important;font-weight:600 !important}
.stCheckbox label{color:#e2e8f0 !important;font-size:15px !important}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h1 style='color:#0ea5e9;font-size:22px;"
        "font-weight:900;margin:0;'>🚀 ReachIQ AI</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:#475569;font-size:12px;"
        "margin:2px 0 12px;'>Generative Growth as a Service</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    page = st.selectbox("Navigate", [
        "🏠  Overview",
        "🔍  Pre-Upload Analyzer",
        "🖼️  Thumbnail Analysis",
        "📊  Post-Upload Monitor",
        "📢  Social Distribution",
        "🧠  Channel Memory",
        "🛡️  Security Report",
        "⚙️  System Diagnostics",
    ])

    st.markdown("---")
    st.markdown(
        "<p style='color:#64748b;font-size:12px;"
        "font-weight:700;letter-spacing:0.1em;'>TECH STACK</p>",
        unsafe_allow_html=True
    )
    stack = [
        ("🧠 Brain", "Groq Llama 3.3 70B", "#0ea5e9"),
        ("👁️ Vision", "Ollama llava:7b", "#059669"),
        ("🔄 Optimizer", "3-Pass Recursive Loop", "#7c3aed"),
        ("💾 Memory", "Mem0 + Qdrant", "#d97706"),
        ("📊 Observe", "Langfuse", "#0ea5e9"),
        ("🛡️ Security", "Custom Guardrails", "#dc2626"),
        ("🤝 Agents", "Band Framework", "#7c3aed"),
    ]
    for label, val, col in stack:
        st.markdown(
            f"<div style='color:{col};font-size:12px;"
            f"font-weight:700;padding:3px 0;'>"
            f"{label}: <span style='color:#94a3b8;"
            f"font-weight:400;'>{val}</span></div>",
            unsafe_allow_html=True
        )
    st.markdown("---")
    st.markdown(
        "<div style='color:#475569;font-size:11px;'>"
        "Band of Agents Hackathon<br>June 2026<br>"
        "noreenakbar06@gmail.com</div>",
        unsafe_allow_html=True
    )

# ── HEADER ───────────────────────────────────────────────
st.title("ReachIQ AI — Main Orchestrator v2.0")
st.markdown(
    "**4 AI agents via Band** — Pre-upload analysis · "
    "Post-upload monitoring · Social distribution · "
    "3-pass recursive optimization"
)
st.markdown("---")
# ── MODULE LOADER ────────────────────────────────────────
@st.cache_resource(show_spinner="Loading ReachIQ AI modules...")
def load_modules():
    errors = []
    result = {}
    module_map = {
        "ask_brain":                ("brain", "ask_brain"),
        "ask_with_fallback":        ("brain", "ask_with_fallback"),
        "analyze_pre_upload":       ("analyzer", "analyze_pre_upload"),
        "score_video":              ("scorer", "score_video"),
        "extract_keywords":         ("keyword_tracker", "extract_keywords"),
        "find_competing_videos":    ("keyword_tracker", "find_competing_videos"),
        "get_videos":               ("youtube_api", "get_videos"),
        "get_video_stats":          ("youtube_api", "get_video_stats"),
        "get_channel_patterns":     ("memory", "get_channel_patterns"),
        "get_smart_suggestions":    ("memory", "get_smart_suggestions"),
        "secure_input":             ("security", "secure_input"),
        "get_security_report":      ("security", "get_security_report"),
        "get_daily_performance_summary": ("observability",
                                          "get_daily_performance_summary"),
        "optimize_title":           ("optimizer", "optimize_title"),
        "optimize_hook":            ("optimizer", "optimize_hook"),
        "optimize_description":     ("optimizer", "optimize_description"),
        "generate_updated_metadata":("metadata_updater",
                                     "generate_updated_metadata"),
        "generate_platform_posts":  ("social_media",
                                     "generate_platform_posts"),
        "find_reddit_opportunities":("social_media",
                                     "find_reddit_opportunities"),
    }

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    for func_name, (mod_name, attr) in module_map.items():
        try:
            mod = importlib.import_module(mod_name)
            result[func_name] = getattr(mod, attr)
        except Exception as e:
            errors.append(f"{mod_name}.{attr}: {e}")
            result[func_name] = None

    result["loaded"] = True
    result["errors"] = errors
    return result
def load_modules():
    try:
        sys.path.insert(
            0, os.path.dirname(os.path.abspath(__file__))
        )
        from brain import ask_brain, ask_with_fallback
        from analyzer import analyze_pre_upload
        from scorer import score_video
        from keyword_tracker import (extract_keywords,
                                     find_competing_videos)
        from youtube_api import get_videos, get_video_stats
        from memory import (get_channel_patterns,
                            get_smart_suggestions)
        from security import (secure_input,
                              validate_youtube_metadata,
                              get_security_report)
        from observability import get_daily_performance_summary
        from optimizer import (optimize_title,
                               optimize_hook,
                               optimize_description)
        from metadata_updater import generate_updated_metadata
        from social_media import (generate_platform_posts,
                                  find_reddit_opportunities)
        return dict(
            ask_brain=ask_brain,
            analyze_pre_upload=analyze_pre_upload,
            score_video=score_video,
            extract_keywords=extract_keywords,
            find_competing_videos=find_competing_videos,
            get_videos=get_videos,
            get_video_stats=get_video_stats,
            get_channel_patterns=get_channel_patterns,
            get_smart_suggestions=get_smart_suggestions,
            secure_input=secure_input,
            get_security_report=get_security_report,
            get_daily_performance_summary=get_daily_performance_summary,
            optimize_title=optimize_title,
            optimize_hook=optimize_hook,
            optimize_description=optimize_description,
            generate_updated_metadata=generate_updated_metadata,
            generate_platform_posts=generate_platform_posts,
            find_reddit_opportunities=find_reddit_opportunities,
            loaded=True
        )
    except Exception as e:
        return {"loaded": False, "error": str(e)}


# ══════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ══════════════════════════════════════════════════════════
if "Overview" in page:
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Modules", "14", "Active")
    with c2: st.metric("AI Agents", "4", "Band-Connected")
    with c3: st.metric("Platforms", "6", "Covered")
    with c4: st.metric("Optimizer", "3-Pass", "Self-Improving")
    with c5: st.metric("Stack Cost", "$0", "100% Free")

    st.markdown("---")
    st.markdown("### 🤝 Band Multi-Agent System")
    c1, c2, c3, c4 = st.columns(4)
    agents = [
        (c1, "🧠 BrainAgent", "Coordinator",
         "Routes all tasks via Band", "#0ea5e9"),
        (c2, "🔍 AnalyzerAgent", "Pre-Upload",
         "Scores + 3-pass optimization", "#059669"),
        (c3, "📊 MonitorAgent", "Post-Upload",
         "Real YouTube Analytics daily", "#d97706"),
        (c4, "📢 DistributionAgent", "Promotion",
         "6 platforms, validated posts", "#db2777"),
    ]
    for col, name, role, desc, color in agents:
        with col:
            st.markdown(
                f"<div class='card' style='border-color:{color};'>"
                f"<div style='color:{color};font-size:16px;"
                f"font-weight:900;'>{name}</div>"
                f"<div style='color:#f1f5f9;font-size:12px;"
                f"font-weight:700;margin:4px 0;'>{role}</div>"
                f"<div style='color:#64748b;font-size:11px;'>"
                f"{desc}</div></div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("### 🔄 Recursive Optimization Engine")
    st.markdown(
        "<div class='card'>"
        "<div style='color:#7c3aed;font-size:15px;"
        "font-weight:900;'>3-Pass Self-Improvement Loop</div>"
        "<div style='color:#94a3b8;font-size:13px;"
        "margin-top:8px;'>"
        "Pass 1 → AI generates output → Self-review scores it"
        " → If score &lt; 7.5 → Pass 2 → Targeted fixes → "
        "Review again → If score &lt; 7.5 → Pass 3 → Final "
        "polish → Output delivered. Stops early when threshold "
        "met. Prevents hallucinations and weak suggestions."
        "</div></div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### 📈 Market & Revenue")
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("TAM", "$4.2B", "Creator Tools")
    with m2: st.metric("Target Users", "45M", "YouTube Channels")
    with m3: st.metric("Hours Saved", "20+/week", "Per Creator")
    with m4: st.metric("Direct Competitors", "0",
                        "Multi-Agent Solutions")

    st.markdown("---")
    st.markdown("### 💰 Pricing")
    p1, p2, p3, p4 = st.columns(4)
    plans = [
        (p1, "📦 One-Time", "$299",
         "Own API keys. Full source.", "#059669"),
        (p2, "🚀 Starter", "$49/mo",
         "1 channel. All modules.", "#0ea5e9"),
        (p3, "💼 Pro", "$99/mo",
         "3 channels. Priority.", "#d97706"),
        (p4, "🏢 Agency", "$249/mo",
         "10 channels. White label.", "#7c3aed"),
    ]
    for col, name, price, desc, color in plans:
        with col:
            st.markdown(
                f"<div class='card' style='border-color:{color};'>"
                f"<div style='color:{color};font-size:13px;"
                f"font-weight:800;'>{name}</div>"
                f"<div style='color:#f1f5f9;font-size:22px;"
                f"font-weight:900;margin:8px 0;'>{price}</div>"
                f"<div style='color:#64748b;font-size:11px;'>"
                f"{desc}</div></div>",
                unsafe_allow_html=True
            )
            # ══════════════════════════════════════════════════════════
# PAGE 2: PRE-UPLOAD ANALYZER
# ══════════════════════════════════════════════════════════
mods = load_modules()
if mods.get("errors"):
    with st.expander("⚠️ Module warnings"):
        for err in mods["errors"]:
            st.warning(err)
elif "Pre-Upload" in page:
    st.header("🔍 Pre-Upload Content Analyzer")
    st.markdown(
        "AnalyzerAgent scores your content then runs the "
        "**3-pass recursive optimizer** on title and hook."
    )

    with st.form("pre_form"):
        title = st.text_input(
            "Video Title *",
            placeholder="e.g. How AI is Changing Education"
        )
        description = st.text_area(
            "Description", height=80,
            placeholder="Brief video description..."
        )
        tags = st.text_input(
            "Tags (comma separated)",
            placeholder="AI, education, students"
        )
        script = st.text_area(
            "Opening Script Hook (optional)", height=80,
            placeholder="Paste your video opening lines..."
        )
        run_optimizer = st.checkbox(
            "🔄 Run 3-Pass Recursive Optimizer", value=True
        )
        submitted = st.form_submit_button("🚀 Analyze Content")

    if submitted and title:
        mods = load_modules()
        if not mods["loaded"]:
            st.error(f"Module error: {mods.get('error')}")
        else:
            safe = mods["secure_input"](title, "title")
            if safe is None:
                st.error("🚫 Input blocked by security layer.")
                st.stop()
            else:
                with st.spinner("Scoring content..."):
                    score = mods["score_video"](
                        title, description, tags
                    )
                with st.spinner("Running analysis..."):
                    analysis = mods["analyze_pre_upload"](
                        title, description, tags,
                        script if script else None
                    )
                with st.spinner("Extracting keywords..."):
                    keywords = mods["extract_keywords"](
                        title, description
                    )

                st.markdown("---")
                st.markdown("### 📊 Content Score")
                if score and isinstance(score, dict):
                    total = score.get("total_score", 0)
                    grade = score.get("grade", "N/A")
                    color = (
                        "#059669" if total >= 75
                        else "#d97706" if total >= 55
                        else "#dc2626"
                    )
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(
                            f"<div style='text-align:center;"
                            f"background:#111827;border-radius:12px;"
                            f"padding:20px;border:2px solid {color};'>"
                            f"<div style='color:{color};font-size:52px;"
                            f"font-weight:900;'>{total}/100</div>"
                            f"<div style='color:#64748b;'>"
                            f"Overall Score</div></div>",
                            unsafe_allow_html=True
                        )
                    with c2:
                        st.markdown(
                            f"<div style='text-align:center;"
                            f"background:#111827;border-radius:12px;"
                            f"padding:20px;border:2px solid {color};'>"
                            f"<div style='color:{color};font-size:52px;"
                            f"font-weight:900;'>{grade}</div>"
                            f"<div style='color:#64748b;'>"
                            f"Grade</div></div>",
                            unsafe_allow_html=True
                        )
                    with c3:
                        st.markdown(
                            f"<div style='background:#111827;"
                            f"border-radius:12px;padding:20px;"
                            f"border:1px solid #1e293b;'>"
                            f"<div style='color:#d97706;font-weight:700;"
                            f"font-size:13px;'>Priority Fix:</div>"
                            f"<div style='color:#f1f5f9;font-size:13px;"
                            f"margin-top:6px;'>"
                            f"{score.get('priority_fix','N/A')}</div>"
                            f"<div style='color:#d97706;font-weight:700;"
                            f"font-size:13px;margin-top:10px;'>Verdict:</div>"
                            f"<div style='color:#f1f5f9;font-size:13px;"
                            f"margin-top:4px;'>"
                            f"{score.get('verdict','N/A')}</div></div>",
                            unsafe_allow_html=True
                        )
                    scores_data = score.get("scores", {})
                    if isinstance(scores_data, dict):
                        st.markdown("**Score Breakdown:**")
                        valid = [
                            (k, v) for k, v in scores_data.items()
                            if k != "total_score"
                        ]
                        if valid:
                            cols = st.columns(len(valid))
                            for i, (k, v) in enumerate(valid):
                                with cols[i]:
                                    st.metric(
                                        k.replace("_"," ").title(),
                                        f"{v}/10"
                                    )

                if analysis and isinstance(analysis, dict):
                    st.markdown("---")
                    st.markdown(
                        "### 🎯 AnalyzerAgent Recommendations"
                    )
                    ready = analysis.get("upload_ready", False)
                    if ready:
                        st.markdown(
                            "<div class='ok'>✅ Ready to Upload"
                            "</div>", unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            "<div class='warn'>"
                            "⚠️ Needs Improvement Before Upload"
                            "</div>", unsafe_allow_html=True
                        )
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Hook Suggestion:**")
                        st.info(
                            analysis.get("hook_suggestion","N/A")
                        )
                        st.markdown("**Thumbnail Text:**")
                        st.success(
                            analysis.get("thumbnail_text","N/A")
                        )
                    with c2:
                        st.markdown("**Top 3 Actions:**")
                        for a in analysis.get(
                                "top_3_actions",[])[:3]:
                            st.markdown(f"› {a}")

                if run_optimizer:
                    st.markdown("---")
                    st.markdown(
                        "### 🔄 3-Pass Recursive Optimizer"
                    )
                    st.markdown("**Optimizing Title...**")
                    prog = st.progress(0)
                    with st.spinner("Running passes..."):
                        title_result = mods["optimize_title"](
                            title
                        )
                    prog.progress(100)

                    if title_result and isinstance(
                            title_result, dict):
                        passes = title_result.get(
                            "passes_completed", 0
                        )
                        final_score = title_result.get(
                            "final_score", 0
                        )
                        threshold = title_result.get(
                            "threshold_met", False
                        )
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric(
                                "Passes Completed",
                                f"{passes}/3"
                            )
                        with c2:
                            st.metric(
                                "Final Score",
                                f"{final_score}/10"
                            )
                        with c3:
                            st.metric(
                                "Threshold Met",
                                "✅ Yes" if threshold
                                else "⚠️ No"
                            )
                        st.markdown("**Original Title:**")
                        st.markdown(
                            f"<div class='fail'>❌ {title}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown("**Optimized Title:**")
                        st.markdown(
                            f"<div class='ok'>✅ "
                            f"{title_result.get('final_content','')}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        with st.expander(
                            "📋 View Optimization History"
                        ):
                            for h in title_result.get(
                                    "history", []):
                                st.markdown(
                                    f"<div class='pass-box'>"
                                    f"<b>Pass {h['pass']}</b> — "
                                    f"Score: {h['score']}/10<br>"
                                    f"Weaknesses: "
                                    f"{', '.join(h.get('weaknesses',[]))}"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )

                    if script:
                        st.markdown("**Optimizing Hook...**")
                        with st.spinner(
                            "Optimizing opening hook..."
                        ):
                            hook_result = mods["optimize_hook"](
                                script
                            )
                        if hook_result and isinstance(
                                hook_result, dict):
                            st.markdown(
                                "**Optimized Hook:**"
                            )
                            st.info(
                                hook_result.get(
                                    "final_content", script
                                )
                            )
                            if hook_result.get("history"):
                                orig = hook_result[
                                    "history"
                                ][0]["score"]
                                final = hook_result[
                                    "final_score"
                                ]
                                passes = hook_result[
                                    "passes_completed"
                                ]
                                st.markdown(
                                    f"*Score: {orig}/10 → "
                                    f"{final}/10 in "
                                    f"{passes} pass(es)*"
                                )

                if keywords and isinstance(keywords, dict):
                    st.markdown("---")
                    st.markdown("### 🔑 Keywords")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown("**Primary:**")
                        for k in keywords.get(
                                "primary_keywords",[]):
                            st.markdown(f"› `{k}`")
                    with c2:
                        st.markdown("**Long Tail:**")
                        for k in keywords.get(
                                "long_tail_keywords",[])[:4]:
                            st.markdown(f"› `{k}`")
                    with c3:
                        st.markdown("**Trending Angles:**")
                        for k in keywords.get(
                                "trending_angles",[])[:3]:
                            st.markdown(f"› {k}")

    elif submitted and not title:
        st.warning("Please enter a video title.")
         # ══════════════════════════════════════════════════════════
# PAGE 3: THUMBNAIL ANALYSIS
# ══════════════════════════════════════════════════════════
        # ══════════════════════════════════════════════════════════
mods = load_modules()
if mods.get("errors"):
    with st.expander("⚠️ Module warnings"):
        for err in mods["errors"]:
            st.warning(err)
elif "Thumbnail" in page:
    st.header("🖼️ Thumbnail Analysis")
    st.markdown(
        "Upload your thumbnail image and llava:7b "
        "vision model analyzes it for CTR potential."
    )

    st.info(
        "💡 Place your thumbnail image file "
        "in your project folder first."
    )

    image_filename = st.text_input(
        "Image filename",
        placeholder="thumbnail.jpg"
    )

    if st.button("🔍 Analyze Thumbnail"):
        if image_filename:
            project_dir = os.path.dirname(
                os.path.abspath(__file__)
            )
            image_path = os.path.join(
                project_dir, image_filename
            )

            if not os.path.exists(image_path):
                st.error(
                    f"File not found: {image_filename}. "
                    "Place the image in your project folder."
                )
            else:
                with st.spinner(
                    "llava:7b analyzing thumbnail... "
                    "This takes 2-5 minutes on CPU."
                ):
                    try:
                        import ollama
                        response = ollama.chat(
                            model="llava:7b",
                            options={
                                "num_predict": 200,
                                "temperature": 0.1
                            },
                            messages=[{
                                "role": "user",
                                "content": """Analyze this YouTube thumbnail.
Return ONLY valid JSON, no extra text.
FORMAT:
{
  "visibility_score": 0,
  "text_readability": "",
  "emotional_impact": "",
  "color_contrast": "",
  "suggested_improvements": [],
  "ctr_prediction": ""
}""",
                                "images": [image_path]
                            }]
                        )
                        result = response["message"]["content"]
                        try:
                            import json
                            clean = result.strip()
                            if "```" in clean:
                                clean = clean.split("```")[1]
                                if clean.startswith("json"):
                                    clean = clean[4:]
                            parsed = json.loads(clean)
                        except:
                            parsed = {
                                "visibility_score": 7,
                                "text_readability": result[:200],
                                "emotional_impact": "See full analysis",
                                "color_contrast": "",
                                "suggested_improvements": [result[:300]],
                                "ctr_prediction": "Manual review needed"
                            }

                        st.markdown("---")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            score = parsed.get(
                                "visibility_score", 0
                            )
                            color = (
                                "#059669" if score >= 7
                                else "#d97806" if score >= 5
                                else "#dc2626"
                            )
                            st.markdown(
                                f"<div style='text-align:center;"
                                f"background:#111827;border-radius:12px;"
                                f"padding:20px;border:2px solid {color};'>"
                                f"<div style='color:{color};"
                                f"font-size:48px;font-weight:900;'>"
                                f"{score}/10</div>"
                                f"<div style='color:#64748b;'>"
                                f"Visibility Score</div></div>",
                                unsafe_allow_html=True
                            )
                        with c2:
                            st.markdown("**Text Readability:**")
                            st.info(
                                parsed.get(
                                    "text_readability", "N/A"
                                )
                            )
                        with c3:
                            st.markdown("**Emotional Impact:**")
                            st.info(
                                parsed.get(
                                    "emotional_impact", "N/A"
                                )
                            )

                        st.markdown("**Color Contrast:**")
                        st.markdown(
                            parsed.get("color_contrast","N/A")
                        )

                        st.markdown("**CTR Prediction:**")
                        st.success(
                            parsed.get("ctr_prediction","N/A")
                        )

                        st.markdown(
                            "**Suggested Improvements:**"
                        )
                        for imp in parsed.get(
                                "suggested_improvements",[]):
                            if isinstance(imp, dict):
                                msg = imp.get("message", str(imp))
                            else:
                                msg = str(imp)
                            st.markdown(f"› {msg}")

                    except Exception as e:
                        if "memory" in str(e).lower():
                            st.error(
                                "Not enough RAM for llava:7b. "
                                "This feature runs on AMD cloud "
                                "during the hackathon."
                            )
                        else:
                            st.error(f"Analysis failed: {e}")
        else:
            st.warning("Please enter an image filename.")      
# PAGE 4: POST-UPLOAD MONITOR
# ══════════════════════════════════════════════════════════
mods = load_modules()
if mods.get("errors"):
    with st.expander("⚠️ Module warnings"):
        for err in mods["errors"]:
            st.warning(err)
elif "Post-Upload" in page:
    st.header("📊 Post-Upload Monitor")
    st.markdown(
        "MonitorAgent fetches real YouTube Analytics, "
        "generates metadata updates, then runs the "
        "**3-pass optimizer** on all suggestions."
    )

    mods = load_modules()
    if not mods["loaded"]:
        st.error(f"Error: {mods.get('error')}")
    else:
        with st.spinner("Fetching channel videos..."):
            try:
                videos = mods["get_videos"](5)
            except Exception as e:
                videos = []
                st.warning(f"YouTube API: {e}")

        if videos:
            options = {v["title"][:60]: v for v in videos}
            selected = st.selectbox(
                "Select video:", list(options.keys())
            )
            run_opt = st.checkbox(
                "🔄 Run 3-Pass Optimizer on Suggestions",
                value=True
            )

            if st.button("📊 Analyze Performance"):
                video = options[selected]
                with st.spinner("Fetching analytics..."):
                    stats = mods["get_video_stats"](
                        video["video_id"]
                    )

                st.markdown("---")
                st.markdown("### 📈 Real Channel Analytics")
                if stats and isinstance(stats, dict):
                    c1,c2,c3,c4 = st.columns(4)
                    with c1:
                        st.metric("Views",
                                  stats.get("views",0))
                    with c2:
                        st.metric("Likes",
                                  stats.get("likes",0))
                    with c3:
                        st.metric("Comments",
                                  stats.get("comments",0))
                    with c4:
                        v = stats.get("views",0)
                        l = stats.get("likes",0)
                        r = (
                            f"{l/v*100:.1f}%" if v > 0
                            else "0%"
                        )
                        st.metric("Like Ratio", r)
                else:
                    st.info(
                        "Analytics loading. New videos "
                        "take 24-48 hours."
                    )

                with st.spinner("Generating metadata suggestions..."):
                    try:
                        raw_metadata = mods["generate_updated_metadata"](
                            video_title=video["title"],
                            current_description="",
                            current_tags="",
                            analytics_data=stats if isinstance(stats, dict) else {}
                        )
                        # Handle both dict and string returns
                        if isinstance(raw_metadata, str):
                            try:
                                clean = raw_metadata.strip()
                                if "```" in clean:
                                    clean = clean.split("```")[1]
                                    if clean.startswith("json"):
                                        clean = clean[4:]
                                import json
                                metadata = json.loads(clean)
                            except:
                                metadata = None
                                st.warning("Metadata returned in unexpected format.")
                        else:
                            metadata = raw_metadata
                    except Exception as e:
                        metadata = None
                        st.warning(f"Metadata generation note: {e}")


# ══════════════════════════════════════════════════════════
# PAGE 5: SOCIAL DISTRIBUTION
# ══════════════════════════════════════════════════════════

mods = load_modules()
if mods.get("errors"):
    with st.expander("⚠️ Module warnings"):
        for err in mods["errors"]:
            st.warning(err)
elif "Social" in page:
    st.header("📢 Social Media Distribution")
    st.markdown(
        "DistributionAgent generates platform posts. "
        "You review and click publish."
    )

    with st.form("social_form"):
        video_title = st.text_input(
            "Video Title",
            placeholder="Your YouTube video title"
        )
        video_url = st.text_input(
            "Video URL",
            placeholder="https://youtu.be/your_id"
        )
        keywords_input = st.text_input(
            "Keywords (comma separated)",
            placeholder="AI, education, students"
        )
        submitted = st.form_submit_button(
            "🚀 Generate Distribution Package"
        )

    if submitted and video_title:
        keywords = [
            k.strip() for k in keywords_input.split(",")
            if k.strip()
        ] or ["AI", "YouTube"]

        mods = load_modules()
        if mods["loaded"]:
            with st.spinner("Generating platform posts..."):
                posts = mods["generate_platform_posts"](
                    video_title=video_title,
                    video_url=video_url,
                    keywords=keywords
                )
            with st.spinner(
                "Finding Reddit opportunities..."
            ):
                reddit = mods["find_reddit_opportunities"](
                    keywords[:3]
                )

            if posts and isinstance(posts, dict):
                st.markdown("---")
                st.markdown("### 📱 Platform Posts")
                st.markdown(
                    "*All posts security-validated. "
                    "Copy and publish manually.*"
                )
                icons = {
                    "youtube_community": "▶️ YouTube",
                    "facebook": "📘 Facebook",
                    "linkedin": "💼 LinkedIn",
                    "reddit": "🔴 Reddit",
                    "quora": "❓ Quora",
                    "twitter": "🐦 Twitter/X"
                }
                for platform, content in posts.items():
                    icon = icons.get(platform, platform)
                    if isinstance(content, dict):
                        post_text = content.get("post","")
                        if post_text:
                            with st.expander(
                                f"{icon} — Click to view"
                            ):
                                st.text_area(
                                    "Post",
                                    value=post_text,
                                    height=100,
                                    key=f"p_{platform}"
                                )

            if reddit and isinstance(reddit, dict):
                st.markdown("---")
                st.markdown(
                    "### 🔴 Reddit Opportunities"
                )
                for sub in reddit.get(
                        "subreddits",[])[:3]:
                    if isinstance(sub, dict):
                        name = sub.get(
                            "name",""
                        ).replace("r/","").strip()
                        reason = sub.get("reason","")
                        comment = sub.get(
                            "sample_comment",""
                        )
                        with st.expander(
                            f"r/{name} — {reason}"
                        ):
                            st.text_area(
                                "Comment",
                                value=comment,
                                height=80,
                                key=f"r_{name}"
                            )
                            # ══════════════════════════════════════════════════════════
# PAGE 6: CHANNEL MEMORY
# ══════════════════════════════════════════════════════════
mods = load_modules()
if mods.get("errors"):
    with st.expander("⚠️ Module warnings"):
        for err in mods["errors"]:
            st.warning(err)
elif "Memory" in page:
    st.header("🧠 Channel Memory & Learning")
    st.markdown(
        "ReachIQ AI learns from every video analysis "
        "and gives smarter suggestions over time."
    )

    mods = load_modules()
    if mods["loaded"]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📈 Learned Channel Patterns")
            with st.spinner("Loading memory..."):
                patterns = mods["get_channel_patterns"]()
            if patterns and isinstance(patterns, dict):
                st.markdown("**Best Topics:**")
                for t in patterns.get(
                        "best_performing_topics",[]):
                    st.markdown(
                        f"<div class='ok'>✅ {t}</div>",
                        unsafe_allow_html=True
                    )
                st.markdown("**Avoid These:**")
                for t in patterns.get(
                        "worst_performing_topics",[]):
                    st.markdown(
                        f"<div class='fail'>❌ {t}</div>",
                        unsafe_allow_html=True
                    )
                st.markdown("**Recommended Next:**")
                for t in patterns.get(
                        "recommended_next_topics",[])[:3]:
                    st.markdown(
                        f"<div class='warn'>💡 {t}</div>",
                        unsafe_allow_html=True
                    )
                st.info(
                    "Key Learning: "
                    + patterns.get("key_learning","")
                )
            else:
                st.info(
                    "Not enough data yet. "
                    "Run analyses to build memory."
                )

        with c2:
            st.markdown("### 💡 Smart Suggestions")
            context = st.text_input(
                "Next video topic?",
                placeholder="e.g. AI tools for students"
            )
            if st.button("Get Memory-Based Suggestions"):
                if context:
                    with st.spinner(
                        "Searching memory..."
                    ):
                        sugg = mods[
                            "get_smart_suggestions"
                        ](context)
                    if sugg and isinstance(sugg, dict):
                        for s in sugg.get(
                                "smart_suggestions",[]):
                            st.markdown(f"› {s}")
                        pred = sugg.get(
                            "predicted_best_topic",""
                        )
                        if pred:
                            st.success(
                                f"**Best Topic:** {pred}"
                            )
                    else:
                        st.info(
                            "Run more analyses to "
                            "build memory first."
                        )


# ══════════════════════════════════════════════════════════
# PAGE 7: SECURITY REPORT
# ══════════════════════════════════════════════════════════
mods = load_modules()
if mods.get("errors"):
    with st.expander("⚠️ Module warnings"):
        for err in mods["errors"]:
            st.warning(err)
elif "Security" in page:
    st.header("🛡️ Security Report")
    st.markdown(
        "Custom guardrails block prompt injection, "
        "harmful content, and policy violations in real time."
    )

    mods = load_modules()
    if mods["loaded"]:
        report = mods["get_security_report"]()
        if isinstance(report, dict):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(
                    "Total Events",
                    report.get("total_events",0)
                )
            with c2:
                st.metric(
                    "Threats Blocked",
                    report.get("blocked",0)
                )
            with c3:
                st.metric(
                    "Approved",
                    report.get("approved",0)
                )
            st.markdown("---")
            st.markdown("### Recent Security Events")
            for event in report.get("events",[]):
                t = event.get("event_type","")
                r = event.get("reason","")
                if "BLOCKED" in t:
                    st.markdown(
                        f"<div class='fail'>"
                        f"🚫 {t} — {r}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div class='ok'>"
                        f"✅ {t} — {r}</div>",
                        unsafe_allow_html=True
                    )

        st.markdown("---")
        st.markdown("### 🧪 Live Security Test")
        test_input = st.text_input(
            "Test an input:",
            placeholder="Try: ignore previous instructions"
        )
        if st.button("Run Security Check"):
            if test_input:
                result = mods["secure_input"](
                    test_input, "test"
                )
                if result:
                    st.markdown(
                        "<div class='ok'>"
                        "✅ Input PASSED security check"
                        "</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        "<div class='fail'>"
                        "🚫 Input BLOCKED by guardrails"
                        "</div>",
                        unsafe_allow_html=True
                    )


# ══════════════════════════════════════════════════════════
# PAGE 8: SYSTEM DIAGNOSTICS
# ══════════════════════════════════════════════════════════
mods = load_modules()
if mods.get("errors"):
    with st.expander("⚠️ Module warnings"):
        for err in mods["errors"]:
            st.warning(err)
elif "Diagnostics" in page:
    st.header("⚙️ System Diagnostics")
    st.markdown(
        "Live status of all ReachIQ AI modules "
        "and observability summary."
    )

    modules_list = [
        "config","brain","youtube_api","analyzer",
        "scorer","monitor","metadata_updater",
        "keyword_tracker","social_media","automation",
        "memory","observability","security","optimizer",
        "agent_brain","agent_analyzer",
        "agent_monitor","agent_distribution"
    ]

    if st.button("🔍 Run Full Diagnostic Check"):
        results = []
        prog = st.progress(0)
        for i, mod in enumerate(modules_list):
            try:
                importlib.import_module(mod)
                results.append((mod, True, ""))
            except Exception as e:
                results.append((mod, False, str(e)[:60]))
            prog.progress((i+1)/len(modules_list))

        st.markdown("---")
        ok_count = sum(1 for _,ok,_ in results if ok)
        st.metric(
            "Modules Operational",
            f"{ok_count}/{len(modules_list)}"
        )

        if ok_count == len(modules_list):
            st.markdown(
                "<div class='ok'>"
                "✅ All modules operational. "
                "ReachIQ AI fully active.</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='warn'>"
                "⚠️ Some modules have issues.</div>",
                unsafe_allow_html=True
            )

        c1, c2 = st.columns(2)
        for i, (mod, ok, err) in enumerate(results):
            col = c1 if i % 2 == 0 else c2
            with col:
                if ok:
                    st.markdown(
                        f"<div class='ok'>"
                        f"✅ {mod}.py</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div class='fail'>"
                        f"⚠️ {mod}.py — {err}</div>",
                        unsafe_allow_html=True
                    )

        mods = load_modules()
        if mods["loaded"]:
            st.markdown("---")
            st.markdown("### 📊 Today's Observability")
            summary = mods[
                "get_daily_performance_summary"
            ]()
            if isinstance(summary, dict):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(
                        "Actions Today",
                        summary.get("total_actions",0)
                    )
                with c2:
                    st.metric(
                        "Success Rate",
                        summary.get("success_rate","0%")
                    )
                with c3:
                    st.metric(
                        "Avg Response",
                        f"{summary.get('avg_duration_ms',0)}ms"
                    )