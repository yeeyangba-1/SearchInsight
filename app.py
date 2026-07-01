"""
SearchInsight: 基于 Multi-Agent 工作流的 AI搜索效果诊断与优化平台
==============================================
运行方式:
    streamlit run app.py
"""
import streamlit as st
import pandas as pd
import os
import sys

st.set_page_config(
    page_title="SearchInsight",
    page_icon="//",
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, os.path.dirname(__file__))

from config import CHART_DIR, REPORT_DIR, DATA_DIR
os.makedirs(CHART_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================================
# 全局 CSS
# ============================================================
st.markdown("""
<style>
/* === 基础 === */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&display=swap');

* { font-family: 'JetBrains Mono', 'Consolas', monospace !important; }

.stApp {
    background: #08080e;
}

/* === 顶部栏 === */
header[data-testid="stHeader"] {
    background: #08080e;
    border-bottom: 1px solid #1a1a2e;
}

/* === 侧边栏 === */
[data-testid="stSidebar"] {
    background: #0c0c14;
    border-right: 1px solid #1a1a2e;
}
[data-testid="stSidebar"] * {
    color: #a0a0b8 !important;
}
[data-testid="stSidebar"] h2 {
    color: #00e5ff !important;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-size: 14px;
}
[data-testid="stSidebar"] h3 {
    color: #00ff88 !important;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* === 按钮 === */
.stButton > button {
    background: transparent !important;
    color: #00e5ff !important;
    border: 1px solid #00e5ff !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-size: 13px !important;
    padding: 12px 24px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #00e5ff !important;
    color: #08080e !important;
    box-shadow: 0 0 20px rgba(0,229,255,0.3) !important;
}
.stButton > button:disabled {
    border-color: #2a2a3a !important;
    color: #3a3a4a !important;
}

/* === 文件上传 === */
[data-testid="stFileUploader"] {
    border: 1px dashed #2a2a3e !important;
    background: #0c0c16 !important;
    padding: 24px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #00e5ff !important;
    background: #0e0e1c !important;
}

/* === 文本输入 === */
textarea, input {
    background: #0c0c16 !important;
    border: 1px solid #2a2a3e !important;
    color: #e0e0f0 !important;
    font-size: 13px !important;
}
textarea:focus, input:focus {
    border-color: #00e5ff !important;
    box-shadow: 0 0 10px rgba(0,229,255,0.1) !important;
}

/* === 进度条 === */
.stProgress > div > div {
    background: #00e5ff !important;
    box-shadow: 0 0 12px rgba(0,229,255,0.4) !important;
}

/* === 展开面板 === */
[data-testid="stExpander"] {
    border: 1px solid #1a1a2e !important;
    background: #0c0c16 !important;
}

/* === Tab === */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #1a1a2e;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #606080 !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    color: #00e5ff !important;
    border-bottom: 2px solid #00e5ff !important;
}

/* === Dataframe === */
[data-testid="stDataFrame"] {
    border: 1px solid #1a1a2e !important;
}

/* === Success/Warning/Error === */
.stSuccess { background: #0a1a14 !important; border: 1px solid #00ff88 !important; color: #00ff88 !important; }
.stWarning { background: #1a180a !important; border: 1px solid #ffaa00 !important; color: #ffaa00 !important; }
.stError   { background: #1a0a0a !important; border: 1px solid #ff4466 !important; color: #ff4466 !important; }

/* === 下载按钮 === */
.stDownloadButton > button {
    background: transparent !important;
    color: #00ff88 !important;
    border: 1px solid #00ff88 !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    font-size: 11px !important;
}
.stDownloadButton > button:hover {
    background: #00ff88 !important;
    color: #08080e !important;
    box-shadow: 0 0 16px rgba(0,255,136,0.3) !important;
}

/* === Spinner === */
.stSpinner > div {
    border-color: #00e5ff !important;
}

/* === 标题 === */
h1 {
    color: #e8e8f8 !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
}
h2 {
    color: #c8c8d8 !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
}
h3 {
    color: #00e5ff !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    font-size: 14px !important;
    text-transform: uppercase !important;
}

/* === 分隔线 === */
hr {
    border-color: #1a1a2e !important;
}

/* === 卡片容器 === */
.card-cyan {
    border: 1px solid #00e5ff;
    background: rgba(0,229,255,0.03);
    padding: 20px;
    margin: 12px 0;
    border-left: 3px solid #00e5ff;
    position: relative;
}
.card-green {
    border: 1px solid #00ff88;
    background: rgba(0,255,136,0.03);
    padding: 20px;
    margin: 12px 0;
    border-left: 3px solid #00ff88;
    position: relative;
}
.card-purple {
    border: 1px solid #7c4dff;
    background: rgba(124,77,255,0.03);
    padding: 20px;
    margin: 12px 0;
    border-left: 3px solid #7c4dff;
    position: relative;
}

/* === Agent 状态指示 === */
.agent-line {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    font-size: 12px;
    letter-spacing: 1px;
}
.agent-active {
    color: #00e5ff;
    animation: pulse 1.5s infinite;
}
.agent-done {
    color: #00ff88;
}
.agent-pending {
    color: #3a3a4a;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* === 滚动条 === */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0c0c14; }
::-webkit-scrollbar-thumb { background: #1a1a2e; }
::-webkit-scrollbar-thumb:hover { background: #2a2a4e; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 侧边栏
# ============================================================
def render_searchinsight_page():
    """Render the minimal SearchInsight diagnosis page."""
    st.title("SearchInsight：基于 Multi-Agent 工作流的 AI搜索效果诊断与优化平台")
    st.write(
        "上传 AI 搜索日志后，系统会通过 8 Agent 流程完成字段校验、日志清洗、Query 分类、"
        "Bad Case 识别、图表生成、LLM Judge 复核和 Markdown 诊断报告。"
    )

    required_columns = {"query", "answer", "retrieved_docs", "user_feedback", "clicked", "created_at"}
    st.info("上传文件需要包含字段：query、answer、retrieved_docs、user_feedback、clicked、created_at")

    uploaded_file = st.file_uploader(
        "上传 AI 搜索日志 CSV/Excel",
        type=["csv", "xlsx", "xls"],
        key="searchinsight_uploader",
    )

    if uploaded_file is None:
        st.info("请上传 data/search_logs.csv 或同结构的 CSV/Excel 文件。")
        return

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"文件读取失败：{e}")
        return

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        st.error(f"上传文件缺少字段：{', '.join(sorted(missing_columns))}")
        st.write("当前文件字段：", list(df.columns))
        return

    st.subheader("上传数据预览")
    st.dataframe(df.head(10), use_container_width=True)

    user_query = st.text_area(
        "诊断需求",
        value="请分析这批AI搜索日志，找出 Query 类型分布、Bad Case 原因、知识库未利用问题，并生成优化建议。",
        height=90,
    )

    if not st.button("开始诊断", type="primary"):
        return

    try:
        from workflow.graph import run_analysis

        os.makedirs("outputs", exist_ok=True)
        saved_path = os.path.join(UPLOAD_DIR, "search_logs_uploaded.csv")
        df.to_csv(saved_path, index=False, encoding="utf-8-sig")

        with st.spinner("8 Agent 正在诊断搜索日志..."):
            final_state = run_analysis(saved_path, user_query)

        summary = final_state.get("eda_result", {})
        chart_paths = final_state.get("chart_paths", [])
        report_path = final_state.get("report_md_path")
        model_result = final_state.get("model_result", {})
        llm_judge = model_result.get("llm_judge", {})

        st.success("诊断完成")
        st.subheader("核心指标")
        c1, c2, c3 = st.columns(3)
        c1.metric("总 Query 数", summary.get("total_queries", 0))
        c2.metric("Bad Case 数量", summary.get("bad_case_count", 0))
        c3.metric("Bad Case 占比", f"{summary.get('bad_case_rate', 0):.2%}")

        st.subheader("8 Agent 执行流程")
        agent_rows = [
            ("01 TASK", "解析 AI 搜索诊断目标", final_state.get("task", {})),
            ("02 QUALITY", "检查搜索日志字段完整性", final_state.get("quality_report", {})),
            ("03 CLEAN", "清洗空值、反馈字段和重复 query", final_state.get("cleaning_report", {})),
            ("04 EDA", "统计 Query 类型和 Bad Case 分布", final_state.get("eda_result", {})),
            ("05 VIZ", "生成诊断图表", final_state.get("viz_result", {})),
            ("06 EVAL", "规则评估 + LLM Judge 语义复核", model_result),
            ("07 INSIGHT", "生成搜索优化洞察", final_state.get("insight_result", {})),
            ("08 REPORT", "生成 Markdown 诊断报告", {"report_path": report_path}),
        ]
        st.dataframe(
            pd.DataFrame(
                [{"agent": name, "role": role, "status": "完成"} for name, role, _ in agent_rows]
            ),
            use_container_width=True,
        )
        with st.expander("查看 8 Agent 详细输出"):
            for name, role, payload in agent_rows:
                st.markdown(f"**{name}：{role}**")
                st.json(payload)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Query 类型分布")
            st.dataframe(
                pd.DataFrame(summary.get("intent_distribution", {}).items(), columns=["intent_category", "count"]),
                use_container_width=True,
            )
        with col2:
            st.subheader("Bad Case 类型分布")
            st.dataframe(
                pd.DataFrame(summary.get("bad_case_distribution", {}).items(), columns=["bad_case_type", "count"]),
                use_container_width=True,
            )

        st.subheader("LLM Judge 结果")
        if llm_judge:
            judge_summary_cols = st.columns(3)
            judge_summary_cols[0].metric("Judge 模式", llm_judge.get("mode", "unknown"))
            judge_summary_cols[1].metric("复核样本数", llm_judge.get("candidate_count", 0))
            judge_summary_cols[2].metric("输出条数", len(llm_judge.get("results", [])))
            if llm_judge.get("fallback_reason"):
                st.warning(f"LLM Judge fallback：{llm_judge['fallback_reason']}")
            if llm_judge.get("results"):
                st.dataframe(pd.DataFrame(llm_judge["results"]), use_container_width=True)
        else:
            st.info("本次未返回 LLM Judge 结果，将以规则评估结果为准。")

        st.subheader("典型 Bad Case 示例")
        if summary.get("top_bad_cases"):
            st.dataframe(pd.DataFrame(summary["top_bad_cases"]), use_container_width=True)
        else:
            st.info("暂无 Bad Case 示例。")

        if chart_paths:
            st.subheader("诊断图表")
            cols = st.columns(3)
            captions = ["Query 类型分布", "Bad Case 类型分布", "正常 / Bad Case 占比"]
            for index, path in enumerate(chart_paths[:3]):
                if os.path.exists(path):
                    with cols[index]:
                        st.image(path, caption=captions[index], use_column_width=True)
                else:
                    st.warning(f"图表不存在：{path}")
        else:
            st.warning("本次未生成图表，请检查 outputs/charts 目录或图表生成日志。")

        st.subheader("Markdown 诊断报告")
        report_content = final_state.get("report_content", "")
        if report_content:
            st.markdown(report_content)
        if report_path:
            st.caption(f"报告已生成：{report_path}")
    except Exception as e:
        st.error(f"诊断失败：{e}")


with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 24px 0;">
        <div style="font-size:26px; font-weight:700; color:#00e5ff; letter-spacing:4px; margin-bottom:4px;">SEARCH</div>
        <div style="font-size:26px; font-weight:300; color:#e0e0f0; letter-spacing:4px;">INSIGHT</div>
        <div style="font-size:10px; color:#4a4a6a; letter-spacing:3px; margin-top:8px;">AI SEARCH DIAGNOSIS</div>
    </div>
    """, unsafe_allow_html=True)

    app_mode = st.selectbox(
        "模式选择",
        ["SearchInsight AI搜索诊断"],
    )

    st.markdown("<hr style='border-color:#1a1a2e;'>", unsafe_allow_html=True)

    st.markdown('<div style="font-size:11px; color:#00ff88; letter-spacing:2px; margin-bottom:8px;">// AGENT PIPELINE</div>', unsafe_allow_html=True)

    agents_info = [
        ("01", "TASK", "任务理解"),
        ("02", "QUALITY", "日志字段检查"),
        ("03", "CLEAN", "日志清洗"),
        ("04", "SEARCH EDA", "搜索统计分析"),
        ("05", "VIZ", "诊断图表"),
        ("06", "EVAL", "回答质量评估"),
        ("07", "INSIGHT", "优化洞察"),
        ("08", "REPORT", "诊断报告"),
    ]
    for num, abbr, name in agents_info:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding:4px 0; font-size:11px;">
            <span style="color:#00e5ff; font-weight:700; min-width:20px;">{num}</span>
            <span style="color:#a0a0b8; font-weight:600; min-width:86px;">{abbr}</span>
            <span style="color:#5a5a6a; font-size:10px;">{name}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1a1a2e;'>", unsafe_allow_html=True)

    st.markdown('<div style="font-size:11px; color:#7c4dff; letter-spacing:2px; margin-bottom:8px;">// TECH STACK</div>', unsafe_allow_html=True)
    for tech in ["LangGraph", "DeepSeek API", "Pandas", "Matplotlib", "Streamlit", "LLM Judge"]:
        st.markdown(f'<div style="color:#5a5a6a; font-size:10px; padding:2px 0;">&gt; {tech}</div>', unsafe_allow_html=True)

# ============================================================
# 主页面
# ============================================================
if "SearchInsight" in app_mode:
    render_searchinsight_page()
    st.stop()

st.markdown("""
<div style="margin-bottom: 24px;">
    <div style="font-size:36px; font-weight:700; color:#e8e8f8; letter-spacing:6px;">
        SEARCH<span style="color:#00e5ff;">INSIGHT</span>
    </div>
    <div style="font-size:12px; color:#4a4a6a; letter-spacing:3px; margin-top:4px;">
        AI SEARCH QUALITY DIAGNOSIS PLATFORM // LANGGRAPH + LLM JUDGE
    </div>
</div>
""", unsafe_allow_html=True)

# ---- 上传 + 输入 ----
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div style="font-size:11px; color:#00e5ff; letter-spacing:2px; margin-bottom:8px;">01 // UPLOAD DATA</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "CSV or Excel",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )

    file_path = None
    if uploaded_file is not None:
        file_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            st.markdown(f"""
            <div class="card-green">
                <span style="color:#00ff88; font-weight:600;">LOADED</span>
                &nbsp;{len(df)} rows &times; {len(df.columns)} cols
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(df.head(8), use_container_width=True)

            with st.expander("DATA DETAILS"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<span style="color:#7c4dff; font-size:11px;">COLUMNS</span>', unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame({'dtype': df.dtypes}).astype(str), use_container_width=True)
                with c2:
                    st.markdown('<span style="color:#7c4dff; font-size:11px;">STATISTICS</span>', unsafe_allow_html=True)
                    st.dataframe(df.describe(include='all'), use_container_width=True)
        except Exception as e:
            st.error(f"Read error: {e}")
            file_path = None

with col2:
    st.markdown('<div style="font-size:11px; color:#00e5ff; letter-spacing:2px; margin-bottom:8px;">02 // ANALYSIS QUERY</div>', unsafe_allow_html=True)
    user_query = st.text_area(
        "query",
        placeholder="> 请分析这批 AI 搜索日志，找出 Query 类型分布、Bad Case 原因和知识库未利用问题\n> 请重点关注用户不满意、检索为空、疑似答非所问的样本\n> 请生成知识库补充、Prompt 优化和检索规则优化建议",
        height=130,
        label_visibility="collapsed"
    )

    st.markdown('<div style="font-size:11px; color:#00e5ff; letter-spacing:2px; margin:16px 0 8px;">03 // EXECUTE</div>', unsafe_allow_html=True)

    run_analysis = False
    if st.button("Run Analysis", type="primary",
                 disabled=(uploaded_file is None or not user_query.strip())):
        run_analysis = True

# ============================================================
# 执行分析
# ============================================================
if run_analysis:
    st.markdown("<hr style='border-color:#1a1a2e;'>", unsafe_allow_html=True)

    st.markdown('<div style="font-size:13px; color:#00ff88; letter-spacing:2px; margin-bottom:16px;">// EXECUTION LOG</div>', unsafe_allow_html=True)

    progress_bar = st.progress(0)
    status_container = st.container()

    with status_container:
        slots = {}
        for i in range(8):
            slots[i] = st.empty()

    import io
    old_stdout = sys.stdout

    agent_map = {
        "Agent 1:": (0, 12, "01 TASK"),
        "Agent 2:": (1, 25, "02 QUALITY"),
        "Agent 3:": (2, 37, "03 CLEAN"),
        "Agent 4:": (3, 50, "04 EDA"),
        "Agent 5:": (4, 62, "05 VIZ"),
        "Agent 6:": (5, 75, "06 EVAL"),
        "Agent 7:": (6, 87, "07 INSIGHT"),
        "Agent 8:": (7, 100, "08 REPORT"),
    }

    class ProgressTracker:
        def __init__(self):
            self.current = -1
        def write(self, s):
            old_stdout.write(s)
            for marker, (idx, prog, label) in agent_map.items():
                if marker in s:
                    progress_bar.progress(prog)
                    for j in range(8):
                        if j < idx:
                            slots[j].markdown(f'<div class="agent-line"><span class="agent-done">&#10003;</span> <span style="color:#00ff88;">{list(agent_map.values())[j][2]}</span></div>', unsafe_allow_html=True)
                        elif j == idx:
                            slots[j].markdown(f'<div class="agent-line"><span class="agent-active">&#9679;</span> <span style="color:#00e5ff;">{label}</span></div>', unsafe_allow_html=True)
                        else:
                            slots[j].markdown(f'<div class="agent-line"><span class="agent-pending">&#9675;</span> <span style="color:#3a3a4a;">{list(agent_map.values())[j][2]}</span></div>', unsafe_allow_html=True)
                    self.current = idx
                    break
        def flush(self):
            old_stdout.flush()

    sys.stdout = ProgressTracker()

    try:
        from workflow.graph import run_analysis
        with st.spinner("..."):
            final_state = run_analysis(file_path, user_query)

        sys.stdout = old_stdout

        # 全部完成
        for j in range(8):
            slots[j].markdown(f'<div class="agent-line"><span class="agent-done">&#10003;</span> <span style="color:#00ff88;">{list(agent_map.values())[j][2]}</span></div>', unsafe_allow_html=True)
        progress_bar.progress(100)

        # === 结果展示 ===
        st.markdown("<hr style='border-color:#1a1a2e; margin-top:32px;'>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px; color:#00e5ff; letter-spacing:2px; margin-bottom:16px;">// RESULTS</div>', unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["REPORT", "INSIGHTS", "CHARTS", "DEBUG"])

        with tab1:
            report_content = final_state.get("report_content", "")
            if report_content:
                st.markdown(report_content)

            c1, c2 = st.columns(2)
            report_md_path = final_state.get("report_md_path")
            if report_md_path and os.path.exists(report_md_path):
                with open(report_md_path, 'r', encoding='utf-8') as f:
                    with c1:
                        st.download_button("Download MD", f.read(), "report.md", "text/markdown")
            report_pdf_path = final_state.get("report_pdf_path")
            if report_pdf_path and os.path.exists(report_pdf_path):
                with open(report_pdf_path, 'rb') as f:
                    with c2:
                        st.download_button("Download PDF", f.read(), "report.pdf", "application/pdf")

        with tab2:
            insight_result = final_state.get("insight_result", {})
            key_insights = insight_result.get("key_insights", [])
            colors = ["#00e5ff", "#00ff88", "#7c4dff", "#ff6b6b", "#ffd93d"]
            if key_insights:
                for i, item in enumerate(key_insights, 1):
                    c = colors[(i-1) % len(colors)]
                    st.markdown(f"""
                    <div class="card-cyan" style="border-left-color:{c}; border-left-width:3px; border:1px solid {c}20; background:{c}05;">
                        <div style="font-size:10px; color:{c}; letter-spacing:2px; margin-bottom:8px;">INSIGHT {i:02d}</div>
                        <div style="color:#c8c8d8; font-size:13px; line-height:1.6; margin-bottom:8px;">{item.get('insight', '')}</div>
                        <div style="display:flex; gap:16px; font-size:10px; color:{c}80;">
                            <span>EVIDENCE: {item.get('evidence', '')}</span>
                        </div>
                        <div style="margin-top:8px; padding:8px 12px; background:{c}10; border-left:2px solid {c}; font-size:10px; color:{c};">
                            ACTION: {item.get('suggestion', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with tab3:
            chart_paths = final_state.get("chart_paths", [])
            if chart_paths:
                cols = st.columns(2)
                for i, path in enumerate(chart_paths):
                    if os.path.exists(path):
                        with cols[i % 2]:
                            st.image(path, use_column_width=True)

        with tab4:
            sections = [
                ("01 TASK UNDERSTANDING", final_state.get("task", {})),
                ("02 DATA QUALITY", final_state.get("quality_report", {})),
                ("03 DATA CLEANING", final_state.get("cleaning_report", {})),
                ("04 EDA RESULT", final_state.get("eda_result", {})),
                ("05 EVAL RESULT", final_state.get("model_result", {})),
            ]
            for title, data in sections:
                with st.expander(title):
                    st.json(data)

    except Exception as e:
        sys.stdout = old_stdout
        st.error(f"Analysis error: {str(e)}")
        import traceback
        with st.expander("TRACE"):
            st.code(traceback.format_exc())

# ============================================================
# 页脚
# ============================================================
st.markdown("<hr style='border-color:#1a1a2e; margin-top:48px;'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding:12px 0;">
    <span style="color:#2a2a3a; font-size:10px; letter-spacing:2px;">
        SEARCHINSIGHT // LANGGRAPH WORKFLOW // AI SEARCH DIAGNOSIS
    </span>
</div>
""", unsafe_allow_html=True)
