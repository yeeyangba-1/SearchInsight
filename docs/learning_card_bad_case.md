# AI搜索 Bad Case 判断学习卡片

## 1. 这个模块做什么？

这个模块用简单规则判断一条 AI 搜索日志是不是 Bad Case，并给出问题类型、判断原因和优化建议。

## 2. 输入是什么？

输入是一条搜索日志，包含：

- query：用户问题
- answer：AI 回答
- retrieved_docs：检索到的知识库片段
- user_feedback：用户反馈
- clicked：是否点击
- created_at：日志时间

## 3. 输出是什么？

输出三个字段：

- bad_case_type：Bad Case 类型
- reason：判断原因
- optimization_suggestion：优化建议

## 4. 判断规则是什么？

- answer 太短：回答过短
- retrieved_docs 为空：检索结果为空
- user_feedback 是不满意：用户不满意
- query 和 answer 关键词不匹配：疑似答非所问
- retrieved_docs 有关键信息但 answer 没体现：知识库未利用
- 以上都没触发：正常

## 5. 面试时一句话怎么讲？

这个模块主要解决的是 AI 搜索结果不好定位原因的问题，我用可解释的规则把搜索日志标记成不同 Bad Case 类型，方便后续分析是召回问题、生成问题，还是用户体验问题。
