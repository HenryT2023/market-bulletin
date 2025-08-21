"""
工具模块 - 日期处理、格式化、日志等通用功能
"""
import logging
from datetime import date, datetime, timedelta
from typing import Optional


def setup_logger(name: str = "market_bulletin", level: str = "INFO") -> logging.Logger:
    """设置日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def parse_date(date_str: str) -> Optional[date]:
    """解析日期字符串"""
    if date_str == "auto":
        return date.today()
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def format_date(dt: date, fmt: str = "%Y-%m-%d") -> str:
    """格式化日期"""
    return dt.strftime(fmt)


def get_business_date(dt: date, offset_days: int = 0) -> date:
    """获取工作日（简化版，不考虑节假日）"""
    target_date = dt + timedelta(days=offset_days)
    
    # 如果是周末，调整到最近的工作日
    if target_date.weekday() == 5:  # 周六
        target_date += timedelta(days=2)
    elif target_date.weekday() == 6:  # 周日
        target_date += timedelta(days=1)
    
    return target_date


def calculate_ref_date(anchor_date: date, ref_code: str) -> Optional[date]:
    """计算参考日期"""
    if ref_code == "D-1":
        return get_business_date(anchor_date, -1)
    elif ref_code == "W-1":
        return anchor_date - timedelta(weeks=1)
    elif ref_code == "M-1":
        # 简化处理，实际可能需要更精确的月份计算
        return anchor_date - timedelta(days=30)
    else:
        return None


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """安全除法"""
    if denominator == 0:
        return default
    return numerator / denominator


def truncate_text(text: str, max_length: int = 140) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def validate_config(config: dict) -> bool:
    """验证配置文件"""
    required_keys = ["commodities", "scope", "price_type", "unit", "publisher"]
    
    for key in required_keys:
        if key not in config:
            print(f"❌ 配置缺少必需字段: {key}")
            return False
    
    if not config["commodities"]:
        print("❌ 商品列表不能为空")
        return False
    
    return True