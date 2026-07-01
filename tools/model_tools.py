"""
机器学习建模工具
Agent 通过这些工具自动训练和评估模型
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score, silhouette_score,
    classification_report
)
import json

from tools.data_tools import _load_data


def train_classifier(file_path: str, target_col: str) -> str:
    """
    训练分类模型
    自动选择 Logistic Regression（小数据）或 Random Forest（大数据）

    参数:
        file_path: 数据文件路径
        target_col: 目标列名（分类标签列）

    返回:
        JSON 格式的模型评估结果
    """
    df = _load_data(file_path)

    if target_col not in df.columns:
        return json.dumps({"error": f"目标列 '{target_col}' 不存在"})

    # 准备数据
    y = df[target_col]
    X = df.drop(columns=[target_col])

    # 处理分类变量
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = LabelEncoder().fit_transform(X[col].astype(str))

    # 处理缺失值
    X = X.fillna(X.median())

    # 编码目标变量
    if y.dtype == 'object':
        y = LabelEncoder().fit_transform(y)

    # 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 选择模型
    if len(df) < 1000:
        model = LogisticRegression(max_iter=1000)
        model_name = "Logistic Regression"
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model_name = "Random Forest"

    # 训练
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # 评估
    result = {
        "model": model_name,
        "task": "分类",
        "metrics": {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, average='weighted', zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, average='weighted', zero_division=0), 4),
            "f1": round(f1_score(y_test, y_pred, average='weighted', zero_division=0), 4)
        }
    }

    # 特征重要性（仅 Random Forest）
    if hasattr(model, 'feature_importances_'):
        importance = dict(zip(X.columns, model.feature_importances_))
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10])
        result["feature_importance"] = {k: round(v, 4) for k, v in importance.items()}

    return json.dumps(result, ensure_ascii=False, indent=2)


def train_regressor(file_path: str, target_col: str) -> str:
    """
    训练回归模型

    参数:
        file_path: 数据文件路径
        target_col: 目标列名（连续值列）

    返回:
        JSON 格式的模型评估结果
    """
    df = _load_data(file_path)

    if target_col not in df.columns:
        return json.dumps({"error": f"目标列 '{target_col}' 不存在"})

    # 准备数据
    y = df[target_col]
    X = df.drop(columns=[target_col])

    # 处理分类变量
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = LabelEncoder().fit_transform(X[col].astype(str))

    # 处理缺失值
    X = X.fillna(X.median())

    # 划分
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 选择模型
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model_name = "Random Forest Regressor"

    # 训练
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # 评估
    result = {
        "model": model_name,
        "task": "回归",
        "metrics": {
            "R²": round(r2_score(y_test, y_pred), 4),
            "RMSE": round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
            "MAE": round(np.mean(np.abs(y_test - y_pred)), 4)
        },
        "feature_importance": dict(
            sorted(
                zip(X.columns, model.feature_importances_),
                key=lambda x: x[1], reverse=True
            )[:10]
        )
    }
    result["feature_importance"] = {k: round(v, 4) for k, v in result["feature_importance"].items()}

    return json.dumps(result, ensure_ascii=False, indent=2)


def train_cluster(file_path: str, n_clusters: int = None) -> str:
    """
    训练 KMeans 聚类模型
    如果不指定 n_clusters，自动用肘部法则确定

    参数:
        file_path: 数据文件路径
        n_clusters: 聚类数（可选，不指定则自动选择）

    返回:
        JSON 格式的聚类结果
    """
    df = _load_data(file_path)

    # 只使用数值列
    X = df.select_dtypes(include=['number']).fillna(df.median())

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 自动确定 K（肘部法则简化版）
    if n_clusters is None:
        inertias = []
        k_range = range(2, min(11, len(df)))
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X_scaled)
            inertias.append(km.inertia_)

        # 简单的肘部检测：找拐点
        deltas = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
        delta_changes = [deltas[i] - deltas[i+1] for i in range(len(deltas)-1)]
        if delta_changes:
            best_k = delta_changes.index(max(delta_changes)) + 2
            best_k = max(2, min(best_k, 6))
        else:
            best_k = 3
        n_clusters = best_k

    # 最终聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # 计算轮廓系数
    sil_score = silhouette_score(X_scaled, labels) if len(set(labels)) > 1 else -1

    # 每个簇的统计
    df['_cluster'] = labels
    cluster_stats = {}
    for c in range(n_clusters):
        cluster_data = df[df['_cluster'] == c]
        cluster_stats[f"簇{c+1}"] = {
            "样本数": len(cluster_data),
            "占比": f"{len(cluster_data)/len(df)*100:.1f}%",
            "均值": cluster_data.drop(columns=['_cluster']).mean().to_dict()
        }

    result = {
        "model": f"KMeans (K={n_clusters})",
        "task": "聚类",
        "metrics": {
            "silhouette_score": round(sil_score, 4),
            "n_clusters": n_clusters,
            "inertia": round(kmeans.inertia_, 2)
        },
        "cluster_sizes": {f"簇{c+1}": int((labels == c).sum()) for c in range(n_clusters)},
        "cluster_stats": cluster_stats
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
