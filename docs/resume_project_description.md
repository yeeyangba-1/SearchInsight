# 简历项目描述

## 版本 A：AI应用开发实习生

**项目名称：SearchInsight：基于 Multi-Agent 工作流的 AI搜索效果诊断与优化平台**

**技术栈：Python、Streamlit、Pandas、Matplotlib、LangGraph、DeepSeek API**

- 基于 LangGraph 设计 8 个职责清晰的 Agent 工作流节点，覆盖搜索日志字段检查、清洗、统计分析、回答质量评估、洞察生成和报告输出。
- 实现 Query 分类和 Bad Case 识别，支持识别回答过短、检索为空、用户不满意、知识库未利用、疑似答非所问等 AI 搜索质量问题。
- 设计规则初筛 + LLM Judge 的评估方式，仅对疑似低质量样本调用大模型，判断回答是否命中 query、是否利用 retrieved_docs，并支持 API 失败 fallback。
- 使用 Streamlit 构建可演示页面，支持上传 CSV/Excel 搜索日志，展示核心指标、Agent 执行结果、诊断图表和 Markdown 报告。
- 将诊断结果转化为知识库补充建议、Prompt 优化建议和检索规则优化建议，形成 AI 搜索质量优化闭环。

## 版本 B：AI搜索优化 / AI产品技术助理

**项目名称：SearchInsight：AI搜索效果诊断与优化平台**

**技术栈：Python、Pandas、Streamlit、Matplotlib、LangGraph、LLM Judge**

- 面向 AI 搜索 / RAG 场景设计搜索日志诊断流程，分析 query、answer、retrieved_docs、user_feedback 等字段，定位用户不满意和回答质量问题。
- 构建 Bad Case 识别规则，覆盖检索为空、知识库未利用、答非所问、回答过短等常见搜索效果问题，并输出可解释原因。
- 对低质量样本引入 LLM Judge 语义复核，判断回答是否回答问题、是否利用知识库片段、是否遗漏关键信息。
- 输出 Query 类型分布、Bad Case 类型分布、高风险问题类型和典型 Bad Case，帮助判断优先优化知识库、Prompt 还是检索规则。
- 生成可视化图表和 Markdown 诊断报告，沉淀知识库补充建议、Prompt 优化建议和后续优化计划。
