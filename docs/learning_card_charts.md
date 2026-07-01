# AI搜索诊断图表学习卡片

## 1. 这个模块做什么？

这个模块把 AI 搜索诊断结果生成 PNG 图表，让统计结果更直观。

## 2. 输入是什么？

输入是 `outputs/analyzed_search_logs.csv`，里面包含 intent_category 和 bad_case_type 等分析字段。

## 3. 输出是什么？

输出是 `outputs/charts` 目录下的 PNG 图片。

## 4. 生成了哪些图？

- Query 类型分布图
- Bad Case 类型分布图
- 正常 / Bad Case 占比图

## 5. 为什么图表对 AI搜索优化有用？

图表能快速展示问题集中在哪类 query、哪类 Bad Case 上，方便判断优化优先级。

## 6. 面试时一句话怎么讲？

这个模块主要解决的是 AI 搜索诊断结果不够直观的问题，我把日志分析结果转成三张基础图表，让团队能快速看到 Query 分布、Bad Case 分布和整体问题占比。
