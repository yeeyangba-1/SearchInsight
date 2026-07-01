# 搜索日志统计汇总学习卡片

## 1. 这个模块做什么？

这个模块对整批 AI 搜索日志做汇总分析，帮助快速看到整体搜索质量问题。

## 2. 输入是什么？

输入是 `data/search_logs.csv`，里面包含 query、answer、retrieved_docs、user_feedback、clicked、created_at。

## 3. 输出是什么？

输出两部分：

- `outputs/analyzed_search_logs.csv`：每条日志的分类和 Bad Case 明细
- summary 字典：整批日志的统计结果

## 4. 统计了哪些指标？

- 总 Query 数
- Bad Case 数量
- Bad Case 占比
- Query 类型分布
- Bad Case 类型分布
- 高风险 Query 类型
- 典型 Bad Case 示例

## 5. 为什么统计汇总对 AI 搜索优化有用？

单条 Bad Case 只能看一个问题，统计汇总可以看整体趋势，帮助判断主要问题集中在哪类 query、哪种 Bad Case，从而决定优先优化知识库、召回还是回答生成。

## 6. 面试时一句话怎么讲？

这个模块主要解决的是 AI 搜索质量缺少全局视角的问题，我把每条日志的 Query 分类和 Bad Case 结果汇总成指标，帮助团队快速定位高风险问题类型和主要优化方向。
