"""
LangGraph 工作流定义
====================

核心技术讲解：LangGraph StateGraph

LangGraph 是一个有向图（DAG），其中：
- 每个"节点"（Node）是一个 Python 函数（这里就是 8 个 Agent 函数）
- 每个"边"（Edge）定义了节点之间的执行顺序
- State 是一个共享的字典，在节点间传递和更新

工作流图：
    task_agent
        │
        ▼
    quality_agent
        │
        ▼
    cleaning_agent
        │
        ▼
    eda_agent
        │
        ▼
    viz_agent ──────┐
        │            │
        ▼            │
    model_agent      │
        │            │
        ▼            │
    insight_agent ◄──┘ (insight 可以看到 viz 和 model 的结果)
        │
        ▼
    report_agent → END
"""
import os
import sys
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.pipeline import (
    task_agent_node,
    quality_agent_node,
    cleaning_agent_node,
    eda_agent_node,
    viz_agent_node,
    model_agent_node,
    insight_agent_node,
    report_agent_node,
)


# ============================================================
# 状态定义（State Schema）
# ============================================================
class AnalysisState(TypedDict):
    """
    在 8 个 Agent 之间传递的共享状态

    每个 Agent 节点：
    1. 读取自己需要的字段
    2. 处理数据
    3. 写入新的字段
    4. 返回更新后的状态（LangGraph 自动合并到全局状态）

    这就是 LangGraph 的核心机制：State Management
    """
    # 输入
    file_path: str
    user_query: str
    data_info: str

    # Agent 1 输出
    task: dict

    # Agent 2 输出
    quality_report: dict

    # Agent 3 输出
    cleaning_report: dict
    cleaned_data_path: str

    # Agent 4 输出
    eda_result: dict

    # Agent 5 输出
    viz_result: dict
    chart_paths: list

    # Agent 6 输出
    model_result: dict

    # Agent 7 输出
    insight_result: dict

    # Agent 8 输出
    report_md_path: str
    report_pdf_path: Optional[str]
    report_content: str


# ============================================================
# 构建工作流图
# ============================================================
def build_analysis_graph() -> StateGraph:
    """
    构建并返回 LangGraph 工作流

    工作流结构：
    START → task → quality → cleaning → eda → viz → model → insight → report → END

    这是一种 DAG（有向无环图），数据按固定顺序流过每个 Agent
    """
    # 创建状态图
    workflow = StateGraph(AnalysisState)

    # 添加节点：每个 Agent 函数是一个节点
    workflow.add_node("task_agent", task_agent_node)
    workflow.add_node("quality_agent", quality_agent_node)
    workflow.add_node("cleaning_agent", cleaning_agent_node)
    workflow.add_node("eda_agent", eda_agent_node)
    workflow.add_node("viz_agent", viz_agent_node)
    workflow.add_node("model_agent", model_agent_node)
    workflow.add_node("insight_agent", insight_agent_node)
    workflow.add_node("report_agent", report_agent_node)

    # 添加边：定义执行顺序（串联结构）
    workflow.add_edge("task_agent", "quality_agent")
    workflow.add_edge("quality_agent", "cleaning_agent")
    workflow.add_edge("cleaning_agent", "eda_agent")
    workflow.add_edge("eda_agent", "viz_agent")
    workflow.add_edge("viz_agent", "model_agent")
    workflow.add_edge("model_agent", "insight_agent")
    workflow.add_edge("insight_agent", "report_agent")
    workflow.add_edge("report_agent", END)

    # 设置入口点
    workflow.set_entry_point("task_agent")

    return workflow


# ============================================================
# 运行分析
# ============================================================
def run_analysis(file_path: str, user_query: str) -> dict:
    """
    运行完整的 8 Agent 分析流程

    参数：
        file_path: 用户上传的数据文件路径
        user_query: 用户的分析需求（自然语言）

    返回：
        最终的 AnalysisState（包含所有 Agent 的输出）
    """
    print("=" * 60)
    print("[SearchInsight] Multi-Agent AI Search Diagnosis Platform Starting")
    print("=" * 60)
    print(f"[Data] File: {file_path}")
    print(f"[Query] {user_query}")
    print(f"{'-' * 60}")

    # 构建图
    workflow = build_analysis_graph()

    # 编译图（compile 会将图转化为可执行的 Runnable）
    app = workflow.compile()

    # 初始状态
    initial_state = {
        "file_path": file_path,
        "user_query": user_query,
    }

    # 执行工作流
    # LangGraph 会自动按边定义的顺序执行每个节点
    # 每个节点的返回值会合并到全局状态中
    final_state = app.invoke(initial_state)

    print(f"{'-' * 60}")
    print("[OK] Analysis complete!")
    print(f"[Report] Markdown: {final_state.get('report_md_path', 'N/A')}")
    print(f"[Report] PDF: {final_state.get('report_pdf_path', 'N/A')}")
    print(f"[Charts] Count: {len(final_state.get('chart_paths', []))}")

    return final_state
