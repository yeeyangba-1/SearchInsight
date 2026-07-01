"""
Run the search log summary, report, and chart demo.

Run from project root:
    python scripts/run_search_quality_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.create_search_log_data import main as create_search_log_data  # noqa: E402
from tools.search_quality_tools import (  # noqa: E402
    analyze_search_logs,
    generate_diagnosis_report,
    generate_search_charts,
)


def main() -> None:
    data_path = PROJECT_ROOT / "data" / "search_logs.csv"
    if not data_path.exists():
        create_search_log_data()

    summary = analyze_search_logs(data_path)
    report_path = generate_diagnosis_report(summary)
    chart_paths = generate_search_charts()

    print("=== AI搜索日志统计汇总 ===")
    print(f"总 Query 数: {summary['total_queries']}")
    print(f"Bad Case 数量: {summary['bad_case_count']}")
    print(f"Bad Case 占比: {summary['bad_case_rate']:.2%}")

    print("\nQuery 类型分布:")
    for intent, count in summary["intent_distribution"].items():
        print(f"- {intent}: {count}")

    print("\nBad Case 类型分布:")
    for case_type, count in summary["bad_case_distribution"].items():
        print(f"- {case_type}: {count}")

    print("\n高风险 Query 类型:")
    if summary["high_risk_intents"]:
        for item in summary["high_risk_intents"]:
            print(
                f"- {item['intent_category']}: "
                f"{item['bad_case_count']}/{item['total_queries']} "
                f"({item['bad_case_rate']:.2%})"
            )
    else:
        print("- 暂无高风险类型")

    print("\n5 条典型 Bad Case 示例:")
    if summary["top_bad_cases"]:
        for index, case in enumerate(summary["top_bad_cases"], start=1):
            print(f"\n{index}. query: {case['query']}")
            print(f"   intent_category: {case['intent_category']}")
            print(f"   bad_case_type: {case['bad_case_type']}")
            print(f"   reason: {case['bad_case_reason']}")
            print(f"   optimization_suggestion: {case['optimization_suggestion']}")
    else:
        print("- 暂无 Bad Case")

    print("\n分析明细已保存: outputs/analyzed_search_logs.csv")
    print(f"诊断报告已生成: {report_path}")
    print("图表已生成:")
    for name, path in chart_paths.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
