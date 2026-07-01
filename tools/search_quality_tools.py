"""
Minimal rule-based AI search diagnosis tools.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd


KEYWORDS = [
    "退货",
    "退款",
    "售后",
    "密码",
    "账号",
    "企业微信",
    "通知",
    "企业版",
    "价格",
    "费用",
    "上传",
    "文件",
    "200MB",
    "API",
    "限流",
    "429",
    "子账号",
    "权限",
    "发票",
    "知识库",
    "索引",
    "续费",
]


INTENT_RULES = {
    "售后问题": ["退款", "退货", "售后", "换货"],
    "价格费用": ["价格", "费用", "多少钱", "套餐", "企业版", "续费"],
    "账号权限": ["登录", "账号", "密码", "权限", "子账号", "管理员"],
    "技术问题": ["报错", "接口", "API", "部署", "无法运行", "限流", "429", "索引"],
    "产品功能": ["功能", "怎么用", "支持什么", "上传", "知识库", "发票", "通知"],
    "知识咨询": ["是什么", "为什么", "区别"],
}


def classify_query_intent(query: Any) -> str:
    """Classify a user query into a simple business intent category."""
    text = "" if pd.isna(query) else str(query)
    for category, keywords in INTENT_RULES.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return category
    return "其他"


def detect_bad_case(row: pd.Series | dict[str, Any]) -> tuple[str, str, str]:
    """
    Diagnose one AI search log.

    Returns:
        bad_case_type, reason, optimization_suggestion
    """
    query = _get_text(row, "query")
    answer = _get_text(row, "answer")
    retrieved_docs = _get_text(row, "retrieved_docs")
    user_feedback = _get_text(row, "user_feedback")

    if len(answer.strip()) < 8:
        return (
            "回答过短",
            "answer 太短，用户很难从中得到明确结论或操作步骤。",
            "要求回答至少包含结论和关键步骤，避免只回答“可以”“能”。",
        )

    if not retrieved_docs.strip():
        return (
            "检索结果为空",
            "retrieved_docs 为空，说明没有召回可参考的知识库内容。",
            "检查知识库是否覆盖该问题，并确认文档已完成索引。",
        )

    if "不满意" in user_feedback:
        return (
            "用户不满意",
            "用户反馈为不满意，这是直接的质量负反馈。",
            "优先人工复盘该问题，检查召回文档和回答是否真正解决需求。",
        )

    if _is_question_answer_mismatch(query, answer):
        return (
            "疑似答非所问",
            "query 和 answer 的核心关键词没有明显交集，回答可能偏离问题。",
            "增加回答前校验，要求回答覆盖用户问题中的核心对象和动作。",
        )

    if _has_docs_but_answer_misses_key_info(retrieved_docs, answer):
        return (
            "知识库未利用",
            "retrieved_docs 里有明确关键信息，但 answer 没有体现出来。",
            "优化提示词，要求回答优先引用检索片段中的关键事实。",
        )

    return (
        "正常",
        "没有触发回答过短、检索为空、用户不满意、未利用知识库或答非所问规则。",
        "保留为正常样本，后续可用于对比 Bad Case。",
    )


def analyze_search_logs(file_path: str | Path) -> dict[str, Any]:
    """Analyze a batch of search logs and return summary statistics."""
    df = pd.read_csv(file_path)

    df["intent_category"] = df["query"].apply(classify_query_intent)
    diagnosis = df.apply(detect_bad_case, axis=1, result_type="expand")
    diagnosis.columns = ["bad_case_type", "bad_case_reason", "optimization_suggestion"]
    analyzed_df = pd.concat([df, diagnosis], axis=1)

    output_path = Path("outputs") / "analyzed_search_logs.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    analyzed_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    total_queries = len(analyzed_df)
    bad_cases = analyzed_df[analyzed_df["bad_case_type"] != "正常"]
    bad_case_count = len(bad_cases)

    return {
        "total_queries": total_queries,
        "bad_case_count": bad_case_count,
        "bad_case_rate": round(bad_case_count / total_queries, 4) if total_queries else 0,
        "intent_distribution": analyzed_df["intent_category"].value_counts().to_dict(),
        "bad_case_distribution": analyzed_df["bad_case_type"].value_counts().to_dict(),
        "high_risk_intents": _get_high_risk_intents(analyzed_df),
        "top_bad_cases": (
            bad_cases[["query", "intent_category", "bad_case_type", "bad_case_reason", "optimization_suggestion"]]
            .head(5)
            .to_dict(orient="records")
        ),
    }


def generate_diagnosis_report(
    summary: dict[str, Any],
    output_path: str | Path = "outputs/search_diagnosis_report.md",
    llm_judge_result: dict[str, Any] | None = None,
) -> str:
    """Generate a business-readable Markdown diagnosis report."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    bad_case_distribution = summary.get("bad_case_distribution", {})
    intent_distribution = summary.get("intent_distribution", {})
    high_risk_intents = summary.get("high_risk_intents", [])
    top_bad_cases = summary.get("top_bad_cases", [])
    top_bad_type = next((name for name in bad_case_distribution if name != "正常"), "暂无明显 Bad Case")
    top_intent = next(iter(intent_distribution.keys()), "暂无 Query 类型")

    lines = [
        "# AI搜索效果诊断与优化报告",
        "",
        "## 1. 数据概览",
        f"- 总 Query 数：{summary['total_queries']}",
        f"- Bad Case 数量：{summary['bad_case_count']}",
        f"- Bad Case 占比：{summary['bad_case_rate']:.2%}",
        "",
        (
            f"本次日志中，Query 主要集中在「{top_intent}」等类型；"
            f"当前最需要关注的质量问题是「{top_bad_type}」。"
            "如果 Bad Case 占比较高，说明搜索系统需要同时检查知识库覆盖、召回质量和回答生成约束。"
        ),
        "",
        "## 2. Query 类型分布",
    ]

    lines.extend(_format_count_items(intent_distribution))
    if high_risk_intents:
        risk_names = "、".join(item["intent_category"] for item in high_risk_intents[:3])
        lines.append(f"\n高风险 Query 类型主要包括：{risk_names}。这些类型建议优先进入人工复盘。")
    else:
        lines.append("\n暂未发现 Bad Case 占比较高的 Query 类型。")

    lines.extend(["", "## 3. Bad Case 类型分布"])
    lines.extend(_format_count_items(bad_case_distribution))
    lines.append(
        "\nBad Case 类型分布可以帮助判断问题发生在检索阶段、知识库建设阶段，还是回答生成阶段。"
    )

    lines.extend(["", "## 4. 典型 Bad Case 分析"])
    if top_bad_cases:
        for index, case in enumerate(top_bad_cases[:5], start=1):
            lines.extend(
                [
                    f"### 案例 {index}",
                    f"- query：{case['query']}",
                    f"- Query 类型：{case.get('intent_category', '')}",
                    f"- Bad Case 类型：{case['bad_case_type']}",
                    f"- 判断原因：{case['bad_case_reason']}",
                    f"- 建议动作：{case['optimization_suggestion']}",
                    "",
                ]
            )
    else:
        lines.append("- 暂无典型 Bad Case。")

    lines.extend(["## 5. LLM Judge 语义评估摘要"])
    if llm_judge_result:
        mode = llm_judge_result.get("mode", "unknown")
        judge_items = llm_judge_result.get("results", [])
        lines.append(f"- 评估模式：{mode}")
        lines.append(f"- 复核样本数：{llm_judge_result.get('candidate_count', 0)}")
        if mode != "llm":
            lines.append("- 说明：LLM Judge 未完整运行，本次使用规则评估 fallback，报告仍可用于定位主要问题。")
        if llm_judge_result.get("fallback_reason"):
            lines.append(f"- fallback 原因：{llm_judge_result['fallback_reason']}")

        if judge_items:
            not_answered = sum(1 for item in judge_items if item.get("answered_query") is False)
            not_used_docs = sum(1 for item in judge_items if item.get("used_retrieved_docs") is False)
            missed_info = sum(1 for item in judge_items if item.get("missed_key_info") is True)
            lines.append(
                f"- 语义复核发现：{not_answered} 条可能未回答问题，"
                f"{not_used_docs} 条可能未充分利用检索片段，{missed_info} 条可能遗漏关键信息。"
            )
            for index, item in enumerate(judge_items[:5], start=1):
                lines.extend(
                    [
                        f"### Judge 案例 {index}",
                        f"- query：{item.get('query', '')}",
                        f"- 主要问题：{item.get('main_problem', '')}",
                        f"- 是否回答问题：{item.get('answered_query', '')}",
                        f"- 是否利用 retrieved_docs：{item.get('used_retrieved_docs', '')}",
                        f"- 优化建议：{item.get('suggestion', '')}",
                        "",
                    ]
                )
        else:
            lines.append("- 暂无 LLM Judge 复核结果。")
    else:
        lines.append("- LLM Judge 未运行，本报告基于规则评估结果生成。")

    lines.extend(["## 6. 知识库补充建议"])
    if bad_case_distribution.get("检索结果为空", 0) > 0:
        lines.append("- 存在检索结果为空，建议补充高频问题对应的知识库文档，并检查文档是否完成解析和索引。")
    if bad_case_distribution.get("用户不满意", 0) > 0:
        lines.append("- 对用户不满意的问题建立标准答案，补充到知识库或 FAQ 中，减少重复 Bad Case。")
    if bad_case_distribution.get("检索结果为空", 0) == 0 and bad_case_distribution.get("用户不满意", 0) == 0:
        lines.append("- 当前知识库覆盖问题不突出，建议继续积累真实 query 观察长尾问题。")

    lines.extend(["", "## 7. Prompt 优化建议"])
    if bad_case_distribution.get("回答过短", 0) > 0:
        lines.append("- 对回答生成 Prompt 增加约束：必须包含结论、步骤、条件和注意事项，避免只回答“可以”“能”。")
    if bad_case_distribution.get("知识库未利用", 0) > 0:
        lines.append("- 要求模型优先基于 retrieved_docs 回答，并在回答中保留检索片段里的关键事实。")
    if bad_case_distribution.get("疑似答非所问", 0) > 0:
        lines.append("- 在生成前增加意图确认，要求 answer 必须覆盖 query 中的核心实体和动作。")

    lines.extend(["", "## 8. 检索规则优化建议"])
    if bad_case_distribution.get("检索结果为空", 0) > 0:
        lines.append("- 降低过严的召回阈值，增加 query 改写和同义词扩展，减少无结果搜索。")
    if bad_case_distribution.get("知识库未利用", 0) > 0:
        lines.append("- 检查召回排序和上下文拼接，确保关键片段进入模型可见上下文。")
    lines.append("- 对高风险 Query 类型建立单独监控，看优化后 Bad Case 占比是否下降。")

    lines.extend(["", "## 9. 下一步优化计划"])
    lines.extend(
        [
            "1. 先人工复盘高风险 Query 类型下的典型 Bad Case，确认规则判断是否准确。",
            "2. 补充缺失知识库内容和标准答案，优先覆盖检索为空、用户不满意样本。",
            "3. 调整 Prompt 约束，让回答必须基于 retrieved_docs 并输出完整步骤。",
            "4. 持续积累日志，把 Bad Case 占比作为搜索质量优化的核心指标。",
        ]
    )

    lines.extend(["", "## 附录：高风险问题类型"])

    if high_risk_intents:
        for item in high_risk_intents:
            lines.append(
                f"- {item['intent_category']}："
                f"{item['bad_case_count']}/{item['total_queries']}，"
                f"Bad Case 占比 {item['bad_case_rate']:.2%}"
            )
    else:
        lines.append("- 暂无高风险问题类型")

    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def generate_search_charts(
    analyzed_csv_path: str | Path = "outputs/analyzed_search_logs.csv",
    output_dir: str | Path = "outputs/charts",
) -> dict[str, str]:
    """Generate simple PNG charts from analyzed search logs."""
    analyzed_path = Path(analyzed_csv_path)
    if not analyzed_path.exists():
        raise FileNotFoundError(f"分析结果文件不存在：{analyzed_path}")

    df = pd.read_csv(analyzed_path)
    required_columns = {"intent_category", "bad_case_type"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"分析结果缺少字段：{', '.join(sorted(missing_columns))}")
    if df.empty:
        raise ValueError("分析结果为空，无法生成图表。")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    chart_dir = Path(output_dir)
    chart_dir.mkdir(parents=True, exist_ok=True)

    chart_paths = {
        "intent_chart": str(chart_dir / "query_intent_distribution.png"),
        "bad_case_chart": str(chart_dir / "bad_case_distribution.png"),
        "bad_case_rate_chart": str(chart_dir / "bad_case_rate.png"),
    }

    _save_bar_chart(
        df["intent_category"].value_counts(),
        "Query 类型分布",
        "Query 类型",
        "数量",
        chart_paths["intent_chart"],
        plt,
    )
    _save_bar_chart(
        df["bad_case_type"].value_counts(),
        "Bad Case 类型分布",
        "Bad Case 类型",
        "数量",
        chart_paths["bad_case_chart"],
        plt,
    )

    bad_case_count = int((df["bad_case_type"] != "正常").sum())
    normal_count = int((df["bad_case_type"] == "正常").sum())
    _save_pie_chart(
        {"正常": normal_count, "Bad Case": bad_case_count},
        "正常 / Bad Case 占比",
        chart_paths["bad_case_rate_chart"],
        plt,
    )

    return chart_paths


def select_low_quality_samples(analyzed_df: pd.DataFrame, max_samples: int = 5) -> pd.DataFrame:
    """Select likely low-quality rows for LLM Judge to control cost."""
    if analyzed_df.empty:
        return analyzed_df

    bad_case_mask = analyzed_df["bad_case_type"] != "正常"
    feedback_mask = analyzed_df["user_feedback"].astype(str).str.contains("不满意", na=False)
    empty_retrieval_mask = analyzed_df["retrieved_docs"].fillna("").astype(str).str.strip() == ""
    specific_bad_case_mask = analyzed_df["bad_case_type"].isin(["疑似答非所问", "知识库未利用"])

    candidates = analyzed_df[
        bad_case_mask | feedback_mask | empty_retrieval_mask | specific_bad_case_mask
    ].copy()
    return candidates.head(max_samples)


def judge_low_quality_samples(
    analyzed_csv_path: str | Path = "outputs/analyzed_search_logs.csv",
    max_samples: int = 5,
) -> dict[str, Any]:
    """
    Use LLM Judge only for likely low-quality samples.

    If API key is missing or the call fails, return rule-based fallback results.
    """
    analyzed_df = pd.read_csv(analyzed_csv_path)
    candidates = select_low_quality_samples(analyzed_df, max_samples=max_samples)

    results = []
    mode = "llm"
    fallback_reason = ""

    for _, row in candidates.iterrows():
        try:
            results.append(_call_llm_judge(row))
        except Exception as exc:
            mode = "fallback"
            fallback_reason = str(exc)
            results.append(_fallback_judge(row, fallback_reason))

    return {
        "mode": mode,
        "candidate_count": len(candidates),
        "fallback_reason": fallback_reason,
        "results": results,
    }


def _get_text(row: pd.Series | dict[str, Any], column: str) -> str:
    value = row[column] if isinstance(row, dict) else row.get(column, "")
    if pd.isna(value):
        return ""
    return str(value)


def _extract_keywords(text: str) -> set[str]:
    return {keyword for keyword in KEYWORDS if keyword.lower() in text.lower()}


def _is_question_answer_mismatch(query: str, answer: str) -> bool:
    query_keywords = _extract_keywords(query)
    answer_keywords = _extract_keywords(answer)
    if not query_keywords:
        return False
    return query_keywords.isdisjoint(answer_keywords)


def _has_docs_but_answer_misses_key_info(retrieved_docs: str, answer: str) -> bool:
    doc_keywords = _extract_keywords(retrieved_docs)
    answer_keywords = _extract_keywords(answer)
    important_doc_keywords = {keyword for keyword in doc_keywords if keyword in {"200MB", "429"}}
    if important_doc_keywords:
        return important_doc_keywords.isdisjoint(answer_keywords)
    return len(doc_keywords) >= 2 and len(doc_keywords & answer_keywords) == 0


def _get_high_risk_intents(analyzed_df: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for intent, group in analyzed_df.groupby("intent_category"):
        total = len(group)
        bad_count = int((group["bad_case_type"] != "正常").sum())
        bad_rate = round(bad_count / total, 4) if total else 0
        if bad_count > 0 and bad_rate >= 0.5:
            rows.append(
                {
                    "intent_category": intent,
                    "total_queries": total,
                    "bad_case_count": bad_count,
                    "bad_case_rate": bad_rate,
                }
            )
    return sorted(rows, key=lambda item: item["bad_case_rate"], reverse=True)


def _format_count_items(distribution: dict[str, int]) -> list[str]:
    if not distribution:
        return ["- 暂无数据"]
    return [f"- {name}：{count}" for name, count in distribution.items()]


def _build_optimization_advice(bad_case_distribution: dict[str, int]) -> list[str]:
    advice = []
    if bad_case_distribution.get("检索结果为空", 0) > 0:
        advice.append("- 如果检索结果为空较多，建议补充知识库内容，或优化召回规则和索引同步。")
    if bad_case_distribution.get("回答过短", 0) > 0:
        advice.append("- 如果回答过短较多，建议优化 Prompt，要求回答包含步骤、条件和注意事项。")
    if bad_case_distribution.get("知识库未利用", 0) > 0:
        advice.append("- 如果知识库未利用较多，建议约束模型必须优先基于 retrieved_docs 回答。")
    if bad_case_distribution.get("用户不满意", 0) > 0:
        advice.append("- 如果用户不满意较多，建议人工复查高频问题并补充标准答案。")
    if bad_case_distribution.get("疑似答非所问", 0) > 0:
        advice.append("- 如果疑似答非所问较多，建议加强 Query 意图识别和回答前关键词校验。")
    if not advice:
        advice.append("- 当前 Bad Case 较少，建议继续积累真实日志，观察长期趋势。")
    return advice


def _save_bar_chart(series: pd.Series, title: str, xlabel: str, ylabel: str, output_path: str, plt: Any) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    series.plot(kind="bar", ax=ax, color="#3b82f6")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def _save_pie_chart(data: dict[str, int], title: str, output_path: str, plt: Any) -> None:
    labels = list(data.keys())
    values = list(data.values())
    fig, ax = plt.subplots(figsize=(6, 4.5))
    if sum(values) == 0:
        values = [1]
        labels = ["暂无数据"]
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, colors=["#22c55e", "#ef4444"])
    ax.set_title(title)
    ax.axis("equal")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def _call_llm_judge(row: pd.Series) -> dict[str, Any]:
    from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

    api_key = DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY 未配置")

    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model=DEEPSEEK_MODEL,
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0,
        max_tokens=800,
    )

    prompt = f"""
你是 AI 搜索质量评估员。请只输出 JSON，不要输出多余解释。

请评估这一条 AI 搜索日志：

query: {row.get('query', '')}
answer: {row.get('answer', '')}
retrieved_docs: {row.get('retrieved_docs', '')}
user_feedback: {row.get('user_feedback', '')}
rule_bad_case_type: {row.get('bad_case_type', '')}
rule_reason: {row.get('bad_case_reason', '')}

判断维度：
1. answer 是否回答了 query
2. answer 是否利用 retrieved_docs
3. answer 是否遗漏关键信息
4. 问题主要出在：检索、知识库、生成、Prompt约束
5. 给出一句具体优化建议

JSON 格式：
{{
  "query": "...",
  "judge_source": "llm",
  "answered_query": true,
  "used_retrieved_docs": true,
  "missed_key_info": false,
  "main_problem": "检索/知识库/生成/Prompt约束",
  "suggestion": "一句具体建议"
}}
"""
    response = llm.invoke(prompt)
    parsed = _extract_json_object(response.content)
    parsed.setdefault("query", row.get("query", ""))
    parsed["judge_source"] = "llm"
    return parsed


def _fallback_judge(row: pd.Series, reason: str) -> dict[str, Any]:
    bad_case_type = str(row.get("bad_case_type", ""))
    retrieved_docs = str(row.get("retrieved_docs", "") if not pd.isna(row.get("retrieved_docs", "")) else "")

    answered_query = bad_case_type not in {"疑似答非所问", "回答过短"}
    used_retrieved_docs = bool(retrieved_docs.strip()) and bad_case_type != "知识库未利用"
    missed_key_info = bad_case_type in {"知识库未利用", "回答过短"}

    if bad_case_type == "检索结果为空":
        main_problem = "检索"
    elif bad_case_type == "知识库未利用":
        main_problem = "Prompt约束"
    elif bad_case_type == "疑似答非所问":
        main_problem = "生成"
    elif bad_case_type == "用户不满意":
        main_problem = "知识库"
    else:
        main_problem = "生成"

    return {
        "query": row.get("query", ""),
        "judge_source": "fallback_rule",
        "fallback_reason": reason,
        "answered_query": answered_query,
        "used_retrieved_docs": used_retrieved_docs,
        "missed_key_info": missed_key_info,
        "main_problem": main_problem,
        "suggestion": row.get("optimization_suggestion", "建议人工复核该样本并补充标准答案。"),
    }


def _extract_json_object(text: str) -> dict[str, Any]:
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("LLM Judge 未返回 JSON")
    return json.loads(match.group(0))
