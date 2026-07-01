"""
全局配置模块
"""
import os
import sys
from dotenv import load_dotenv

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

load_dotenv()

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 输出路径
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
CHART_DIR = os.path.join(OUTPUT_DIR, "charts")
REPORT_DIR = os.path.join(OUTPUT_DIR, "reports")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# LLM 参数
LLM_TEMPERATURE = 0.1  # 数据分析任务保持低温，输出更稳定
LLM_MAX_TOKENS = 4096
