# Streamlit 接入学习卡片

## 1. 这个模块做什么？

这个模块把 AI 搜索诊断能力接入 Streamlit 页面，让用户可以在网页上上传日志并查看诊断结果。

## 2. 输入是什么？

输入是用户上传的 CSV/Excel 文件，字段包括 query、answer、retrieved_docs、user_feedback、clicked、created_at。

## 3. 输出是什么？

页面输出统计指标、Query 类型分布、Bad Case 类型分布、典型 Bad Case 示例和 Markdown 诊断报告。

## 4. 网页流程是什么？

选择 SearchInsight 模式，上传搜索日志，点击开始诊断，系统保存文件、运行分析、生成报告并展示结果。

## 5. 为什么接入 Streamlit 对项目展示有用？

Streamlit 页面能把命令行能力变成可演示产品，让面试官直观看到输入、处理过程和输出结果。

## 6. 面试时一句话怎么讲？

这个模块主要解决的是 AI 搜索诊断能力缺少可视化入口的问题，我把日志上传、规则诊断、统计汇总和 Markdown 报告接入 Streamlit，让项目从脚本能力变成一个可演示的小产品。
