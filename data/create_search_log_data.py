"""
Create demo AI search logs for SearchInsight.

Run from project root:
    python data/create_search_log_data.py
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


def build_demo_logs() -> pd.DataFrame:
    base_time = datetime(2026, 6, 1, 9, 0, 0)
    rows = [
        {
            "query": "订单超过7天还能退货吗",
            "answer": "超过7天一般不能无理由退货，但如果存在质量问题，可以提交售后凭证申请审核。",
            "retrieved_docs": "退货政策：签收后7天内支持无理由退货；超过7天仅质量问题可走售后审核。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "退款多久到账",
            "answer": "退款审核通过后通常3到5个工作日原路返回，对公付款退款可能需要人工处理。",
            "retrieved_docs": "售后政策：退款审核通过后3-5个工作日原路返回；对公付款需人工处理。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "换货需要重新支付运费吗",
            "answer": "看情况。",
            "retrieved_docs": "换货政策：商品质量问题换货由平台承担运费；非质量问题换货由用户承担寄回运费。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "售后电话是多少",
            "answer": "售后客服电话是400-800-1234，服务时间为工作日9:00到18:00。",
            "retrieved_docs": "售后服务：客服电话400-800-1234，工作日9:00-18:00提供人工服务。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "企业版多少钱一个月",
            "answer": "企业版基础包每月299元起，包含10个账号，额外账号按阶梯价格计费。",
            "retrieved_docs": "价格说明：企业版基础包299元/月，包含10个账号；额外账号按阶梯价格计费。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "套餐可以按年购买吗",
            "answer": "年付套餐支持购买，并且通常会有折扣，具体价格以费用中心显示为准。",
            "retrieved_docs": "价格说明：专业版和企业版支持月付、年付；年付可享受折扣。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "试用版能用多久",
            "answer": "试用版可以使用14天，包含基础搜索和知识库功能。",
            "retrieved_docs": "价格费用：新用户试用期14天，开放基础搜索、知识库和少量分析能力。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "怎么关闭自动续费",
            "answer": "请联系销售。",
            "retrieved_docs": "订阅管理：自动续费可在费用中心-订阅管理关闭，不影响当前已购买周期。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "忘记密码怎么重置",
            "answer": "可以。",
            "retrieved_docs": "账号帮助：在登录页点击忘记密码，通过手机号或邮箱验证码重置密码。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "登录验证码一直收不到",
            "answer": "建议先检查手机号是否正确、短信是否被拦截。如果多次失败，可以改用邮箱验证码或联系管理员重置绑定方式。",
            "retrieved_docs": "账号登录：验证码可能受手机号错误、短信拦截、发送频率限制影响；可使用邮箱验证替代。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "如何开通子账号权限",
            "answer": "管理员可以在成员管理中创建子账号，并在角色权限里分配查看、导出和审批权限。",
            "retrieved_docs": "权限管理：管理员进入成员管理，创建子账号后绑定角色并分配权限。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "管理员离职了怎么转移权限",
            "answer": "可以。",
            "retrieved_docs": "账号权限：超级管理员离职时，可由企业认证主体提交工单，完成管理员身份转移。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "API限流规则是什么",
            "answer": "退款会在3到5个工作日原路返回，请耐心等待。",
            "retrieved_docs": "技术文档：API默认每分钟600次请求，超过限制返回429；企业版可申请更高配额。",
            "user_feedback": "满意",
            "clicked": 0,
        },
        {
            "query": "接口返回500应该怎么排查",
            "answer": "请联系管理员。",
            "retrieved_docs": "技术排查：接口返回500时先查看服务日志、请求参数、鉴权状态和最近发布记录。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "部署后无法运行怎么办",
            "answer": "可先检查环境变量、依赖版本、服务端口和启动日志，再根据错误堆栈定位。",
            "retrieved_docs": "部署排查：无法运行通常与环境变量缺失、依赖版本冲突、端口占用和启动命令错误有关。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "数据同步失败怎么办",
            "answer": "可先查看同步任务日志，确认数据源连接、字段映射和权限是否正常，再手动重试任务。",
            "retrieved_docs": "技术排查：同步失败常见原因包括数据源连接异常、字段映射错误、权限不足。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "上传文件大小限制是多少",
            "answer": "系统支持上传文件，请在知识库页面选择文件后提交。",
            "retrieved_docs": "产品功能：单个文件最大支持200MB，批量上传最多100个文件。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "知识库能否导入PDF",
            "answer": "能。",
            "retrieved_docs": "产品功能：知识库支持PDF、Word、Markdown、网页链接等格式导入。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "搜索支持多语言吗",
            "answer": "价格请咨询销售。",
            "retrieved_docs": "产品功能：搜索支持中文、英文和部分日文内容，跨语言检索需要开启多语言索引。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "怎么绑定企业微信通知",
            "answer": "在系统设置里配置回调地址。",
            "retrieved_docs": "",
            "user_feedback": "满意",
            "clicked": 0,
        },
        {
            "query": "发票在哪里申请",
            "answer": "可以在费用中心的发票管理页面填写抬头、税号和邮箱，审核通过后发送电子发票。",
            "retrieved_docs": "发票说明：用户可在费用中心-发票管理中申请发票，需要填写抬头、税号和邮箱。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "报表导出失败是什么原因",
            "answer": "导出失败通常和数据量过大、浏览器拦截下载、账号无导出权限有关，可以缩小时间范围后重试。",
            "retrieved_docs": "报表导出：常见失败原因包括数据量过大、浏览器拦截、账号缺少导出权限。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "为什么检索不到企业微信通知文档",
            "answer": "可能是知识库还没有配置相关内容，建议检查文档是否已上传并完成索引。",
            "retrieved_docs": "",
            "user_feedback": "满意",
            "clicked": 0,
        },
        {
            "query": "为什么回答引用了旧政策",
            "answer": "可能是模型理解偏差导致。",
            "retrieved_docs": "搜索诊断：回答引用旧政策通常与索引未更新、召回文档版本过旧或排序权重异常有关。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "AI搜索准确率怎么提升",
            "answer": "可以从三方面优化搜索：补齐知识库内容、提升召回排序质量、对Bad Case做持续归因和规则迭代。",
            "retrieved_docs": "知识咨询：搜索准确率优化通常包括知识库治理、召回排序优化、回答生成约束和Bad Case分析。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "什么是向量检索",
            "answer": "向量检索是把文本转换成向量后，根据语义相似度查找相关内容，适合处理同义表达和自然语言问题。",
            "retrieved_docs": "知识咨询：向量检索通过 embedding 表示文本语义，并用相似度搜索召回相关文档。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "RAG和普通问答有什么区别",
            "answer": "RAG会先检索外部知识，再基于检索结果生成回答；普通问答更多依赖模型已有参数知识。",
            "retrieved_docs": "知识咨询：RAG包含检索和生成两个阶段，可降低知识过期和幻觉风险。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "为什么同一个问题每次答案不一样",
            "answer": "因为模型生成具有随机性，也可能受到召回文档、排序结果和提示词约束变化影响。",
            "retrieved_docs": "知识咨询：回答不稳定可能来自模型采样、召回结果变化、Prompt约束不足和知识版本差异。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "会员到期后数据还在吗",
            "answer": "在。",
            "retrieved_docs": "账号权益：会员到期后数据保留90天，期间可续费恢复高级功能。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "为什么搜索结果为空",
            "answer": "可能没有配置知识库。",
            "retrieved_docs": "",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "如何删除知识库文档",
            "answer": "可以在知识库列表选择目标文档，点击删除。删除后会同步移除对应索引，通常几分钟内生效。",
            "retrieved_docs": "知识库管理：删除文档后系统会删除文件记录，并异步清理搜索索引。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "能不能限制成员只能看某个项目",
            "answer": "可以通过项目级角色实现。管理员在项目设置中添加成员，并分配只读、编辑或管理员权限。",
            "retrieved_docs": "权限管理：项目级权限支持只读、编辑、管理员三类角色，可限制成员访问范围。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "知识库文档上传后为什么搜不到",
            "answer": "上传后通常需要5到10分钟完成解析和索引同步，如果仍搜不到，需要检查文档状态和权限范围。",
            "retrieved_docs": "知识库索引：上传后需等待5-10分钟完成解析和索引；权限范围会影响可搜索内容。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "你们支持哪些支付方式",
            "answer": "请查看帮助中心。",
            "retrieved_docs": "价格费用：平台支持支付宝、微信支付、银行转账；企业客户可申请对公付款。",
            "user_feedback": "不满意",
            "clicked": 0,
        },
        {
            "query": "如何查看团队成员操作日志",
            "answer": "管理员可以在安全中心查看操作日志，支持按成员、时间、操作类型筛选。",
            "retrieved_docs": "账号权限：安全中心提供成员操作日志，可按账号、时间范围、操作类型查询。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "知识库覆盖率是什么意思",
            "answer": "知识库覆盖率可以理解为用户问题能否在知识库中找到足够支撑材料的比例。",
            "retrieved_docs": "知识咨询：知识库覆盖率用于衡量用户问题和知识库内容之间的匹配程度。",
            "user_feedback": "满意",
            "clicked": 1,
        },
        {
            "query": "API鉴权失败怎么处理",
            "answer": "建议检查 Access Token 是否过期、签名算法是否正确、请求时间戳是否超出允许范围。",
            "retrieved_docs": "技术文档：鉴权失败常见原因包括 token 过期、签名错误、时间戳过期和权限不足。",
            "user_feedback": "满意",
            "clicked": 1,
        },
    ]

    for index, row in enumerate(rows):
        row["created_at"] = (base_time + timedelta(minutes=index * 12)).strftime("%Y-%m-%d %H:%M:%S")

    return pd.DataFrame(rows)


def main() -> None:
    output_path = Path(__file__).resolve().parent / "search_logs.csv"
    df = build_demo_logs()
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Created demo search logs: {output_path}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
