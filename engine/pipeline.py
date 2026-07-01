"""
SearchInsight LangGraph pipeline.

The original project already has an 8-node LangGraph workflow. This file keeps
the same node function names, but changes each node's internal business logic
from generic data analysis to AI search quality diagnosis.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd

from tools.search_quality_tools import (
    analyze_search_logs,
    classify_query_intent,
    detect_bad_case,
    generate_diagnosis_report,
    generate_search_charts,
    judge_low_quality_samples,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
REQUIRED_COLUMNS = ["query", "answer", "retrieved_docs", "user_feedback", "clicked", "created_at"]


def _read_search_logs(file_path: str | Path) -> pd.DataFrame:
    path = Path(file_path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("只支持 CSV/XLSX/XLS 格式的 AI 搜索日志。")


def _save_search_logs(df: pd.DataFrame, filename: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)


def _load_analyzed_logs() -> pd.DataFrame:
    return pd.read_csv(OUTPUT_DIR / "analyzed_search_logs.csv")


def task_agent_node(state: dict) -> dict:
    """Agent 1: parse the AI search diagnosis task."""
    print(">>> Agent 1: Search Diagnosis Task Understanding...")

    user_query = state.get("user_query", "")
    task = {
        "task_type": "AI搜索效果诊断",
        "goal": "分析 AI 搜索日志中的 Query 类型、Bad Case 原因、知识库未利用问题和优化建议。",
        "user_query": user_query,
        "key_metrics": ["Bad Case 占比", "Query 类型分布", "Bad Case 类型分布", "高风险 Query 类型"],
        "analysis_steps": [
            "检查搜索日志字段",
            "清洗搜索日志",
            "识别 Query 意图",
            "判断 Bad Case",
            "生成图表和诊断报告",
        ],
    }

    print(f"   [OK] Task type: {task['task_type']}")
    return {"task": task}


def quality_agent_node(state: dict) -> dict:
    """Agent 2: check required AI search log fields and basic data quality."""
    print(">>> Agent 2: Search Log Quality Check...")

    df = _read_search_logs(state["file_path"])
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    missing_values = {
        col: int(df[col].isna().sum())
        for col in REQUIRED_COLUMNS
        if col in df.columns and int(df[col].isna().sum()) > 0
    }
    duplicate_query_count = int(df.duplicated(subset=["query"]).sum()) if "query" in df.columns else 0

    quality_report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "required_columns": REQUIRED_COLUMNS,
        "missing_columns": missing_columns,
        "missing_values": missing_values,
        "duplicate_query_count": duplicate_query_count,
        "is_ready": len(missing_columns) == 0,
    }

    if missing_columns:
        print(f"   [WARN] Missing columns: {missing_columns}")
    else:
        print("   [OK] Required search log fields are complete")

    return {"quality_report": quality_report}


def cleaning_agent_node(state: dict) -> dict:
    """Agent 3: clean search logs for diagnosis."""
    print(">>> Agent 3: Search Log Cleaning...")

    quality_report = state.get("quality_report", {})
    if quality_report.get("missing_columns"):
        raise ValueError(f"搜索日志缺少必要字段：{quality_report['missing_columns']}")

    df = _read_search_logs(state["file_path"])
    original_rows = len(df)
    operations = []

    for col in ["query", "answer", "retrieved_docs", "user_feedback"]:
        missing_count = int(df[col].isna().sum())
        if missing_count:
            df[col] = df[col].fillna("")
            operations.append({"action": "fill_empty_text", "column": col, "count": missing_count})

    if "clicked" in df.columns:
        df["clicked"] = pd.to_numeric(df["clicked"], errors="coerce").fillna(0).astype(int)

    df["user_feedback"] = df["user_feedback"].astype(str).str.strip()
    df["user_feedback"] = df["user_feedback"].replace(
        {
            "satisfied": "满意",
            "unsatisfied": "不满意",
            "bad": "不满意",
            "good": "满意",
            "0": "不满意",
            "1": "满意",
        }
    )

    empty_query_count = int((df["query"].astype(str).str.strip() == "").sum())
    if empty_query_count:
        df = df[df["query"].astype(str).str.strip() != ""]
        operations.append({"action": "drop_empty_query", "count": empty_query_count})

    duplicate_query_count = int(df.duplicated(subset=["query"]).sum())
    if duplicate_query_count:
        df = df.drop_duplicates(subset=["query"], keep="first")
        operations.append({"action": "drop_duplicate_query", "count": duplicate_query_count})

    cleaned_path = _save_search_logs(df, "cleaned_search_logs.csv")
    cleaning_report = {
        "original_rows": original_rows,
        "cleaned_rows": len(df),
        "operations": operations,
        "cleaned_file": cleaned_path,
    }

    print(f"   [OK] Cleaning complete: {original_rows} -> {len(df)} rows")
    return {"cleaning_report": cleaning_report, "cleaned_data_path": cleaned_path}


def eda_agent_node(state: dict) -> dict:
    """Agent 4: compute search quality statistics."""
    print(">>> Agent 4: Search Quality EDA...")

    summary = analyze_search_logs(state.get("cleaned_data_path", state["file_path"]))
    eda_result = {
        "total_queries": summary["total_queries"],
        "bad_case_count": summary["bad_case_count"],
        "bad_case_rate": summary["bad_case_rate"],
        "intent_distribution": summary["intent_distribution"],
        "bad_case_distribution": summary["bad_case_distribution"],
        "high_risk_intents": summary["high_risk_intents"],
        "top_bad_cases": summary["top_bad_cases"],
    }

    print(f"   [OK] Bad Case rate: {summary['bad_case_rate']:.2%}")
    return {"eda_result": eda_result}


def viz_agent_node(state: dict) -> dict:
    """Agent 5: generate SearchInsight charts."""
    print(">>> Agent 5: Search Diagnosis Visualization...")

    chart_paths_dict = generate_search_charts()
    chart_paths = list(chart_paths_dict.values())
    viz_result = {
        "charts": chart_paths_dict,
        "summary": "已生成 Query 类型分布、Bad Case 类型分布、正常/Bad Case 占比图。",
    }

    print(f"   [OK] Visualization complete, generated {len(chart_paths)} charts")
    return {"viz_result": viz_result, "chart_paths": chart_paths}


def model_agent_node(state: dict) -> dict:
    """Agent 6: evaluate answer quality with rules plus optional LLM Judge."""
    print(">>> Agent 6: Answer Quality Evaluation...")

    df = _load_analyzed_logs()
    bad_cases = df[df["bad_case_type"] != "正常"]
    failure_counts = bad_cases["bad_case_type"].value_counts().to_dict()
    llm_judge = judge_low_quality_samples(max_samples=5)

    model_result = {
        "agent_role": "EVAL Agent",
        "model_type": "规则评估 + 小样本 LLM Judge",
        "trained_model": False,
        "low_quality_answer_count": len(bad_cases),
        "major_failure_types": failure_counts,
        "typical_bad_cases": bad_cases[
            ["query", "intent_category", "bad_case_type", "bad_case_reason", "optimization_suggestion"]
        ]
        .head(5)
        .to_dict(orient="records"),
        "llm_judge": llm_judge,
        "summary": "本节点不训练传统模型，只对疑似低质量样本进行规则评估，并在可用时调用 LLM Judge 做语义复核。",
    }

    print(f"   [OK] Low quality answers: {len(bad_cases)}")
    print(f"   [OK] LLM Judge mode: {llm_judge.get('mode')}")
    return {"model_result": model_result}


def insight_agent_node(state: dict) -> dict:
    """Agent 7: generate search optimization insights."""
    print(">>> Agent 7: Search Optimization Insights...")

    eda_result = state.get("eda_result", {})
    bad_case_distribution = eda_result.get("bad_case_distribution", {})
    high_risk_intents = eda_result.get("high_risk_intents", [])

    insights = []
    if bad_case_distribution.get("检索结果为空", 0) > 0:
        insights.append(
            {
                "insight": "存在检索结果为空的问题，说明部分 query 没有召回可用知识。",
                "evidence": f"检索结果为空数量：{bad_case_distribution.get('检索结果为空', 0)}",
                "suggestion": "补充知识库内容，检查文档解析、索引同步和召回阈值。",
            }
        )
    if bad_case_distribution.get("知识库未利用", 0) > 0:
        insights.append(
            {
                "insight": "存在知识库未利用问题，说明召回结果和回答生成之间没有充分对齐。",
                "evidence": f"知识库未利用数量：{bad_case_distribution.get('知识库未利用', 0)}",
                "suggestion": "优化 Prompt，要求回答优先基于 retrieved_docs 中的关键事实。",
            }
        )
    if bad_case_distribution.get("回答过短", 0) > 0:
        insights.append(
            {
                "insight": "部分回答过短，用户很难获得完整操作路径。",
                "evidence": f"回答过短数量：{bad_case_distribution.get('回答过短', 0)}",
                "suggestion": "要求回答包含结论、步骤、条件和注意事项。",
            }
        )
    if bad_case_distribution.get("疑似答非所问", 0) > 0:
        insights.append(
            {
                "insight": "存在答非所问风险，说明意图识别或回答约束需要增强。",
                "evidence": f"疑似答非所问数量：{bad_case_distribution.get('疑似答非所问', 0)}",
                "suggestion": "增加 Query 意图识别和回答前关键词覆盖校验。",
            }
        )
    if high_risk_intents:
        top_intent = high_risk_intents[0]
        insights.append(
            {
                "insight": f"{top_intent['intent_category']} 是当前最高风险问题类型。",
                "evidence": f"Bad Case 占比 {top_intent['bad_case_rate']:.2%}",
                "suggestion": "优先复盘该类型下的高频 query，并补充标准答案和知识库内容。",
            }
        )
    if not insights:
        insights.append(
            {
                "insight": "当前样本未发现明显集中风险。",
                "evidence": "Bad Case 规则未出现高频异常。",
                "suggestion": "继续积累真实日志，扩大样本后再观察趋势。",
            }
        )

    insight_result = {
        "key_insights": insights[:5],
        "summary": "搜索优化应优先围绕高风险 Query 类型、检索覆盖和回答生成约束展开。",
    }

    print(f"   [OK] Insights generated: {len(insights[:5])}")
    return {"insight_result": insight_result}


def report_agent_node(state: dict) -> dict:
    """Agent 8: generate the AI search diagnosis and optimization report."""
    print(">>> Agent 8: Search Diagnosis Report Generation...")

    summary = state.get("eda_result", {})
    llm_judge_result = state.get("model_result", {}).get("llm_judge")
    report_path = generate_diagnosis_report(summary, llm_judge_result=llm_judge_result)
    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()

    print(f"   [OK] Markdown report saved: {report_path}")
    return {
        "report_md_path": report_path,
        "report_pdf_path": None,
        "report_content": report_content,
    }
