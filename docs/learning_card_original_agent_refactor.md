# 原 8 Agent 改造成 SearchInsight 学习卡片

## 1. 这次不是新增脚本，而是如何复用原 8 Agent

这次没有新建旁路 workflow，而是保留原来的 LangGraph 8 Agent 节点和执行顺序，只把每个 Agent 的内部业务逻辑从通用数据分析改成 AI 搜索效果诊断。

## 2. 每个 Agent 的职责如何变化？

- TASK：从解析通用分析需求，改成解析 AI 搜索诊断目标
- QUALITY：从检查通用数据质量，改成检查搜索日志必要字段
- CLEAN：从通用清洗，改成清洗 query、answer、retrieved_docs、feedback
- EDA：从描述统计，改成统计 Query 类型和 Bad Case 分布
- VIZ：从通用图表，改成搜索诊断三张图
- MODEL：从训练模型，改成规则型回答质量评估
- INSIGHT：从业务洞察，改成搜索优化建议
- REPORT：从通用报告，改成 AI 搜索诊断报告

## 3. 这样为什么比单独写脚本更像业务项目？

单独脚本只能证明某个函数能跑；复用原 8 Agent 流程说明我能把已有系统迁移到新业务场景，保留工程结构，同时替换业务逻辑，更接近真实项目改造。

## 4. 面试时一句话怎么讲？

这个模块主要解决的是把通用 Multi-Agent 工作流业务化的问题，我保留原 LangGraph 8 Agent 架构，只替换每个 Agent 的职责，让项目聚焦 SearchInsight AI 搜索效果诊断平台。
