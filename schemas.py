"""
数据模型定义 - 市场价格快报系统
"""
from pydantic import BaseModel, Field
from typing import Dict, Optional, List


class MarketTrendQuery(BaseModel):
    """市场趋势查询请求"""
    date: str
    commodities: List[str]
    scope: str
    price_type: str
    unit: str
    references: List[str]
    language: str = "zh-CN"
    tone: str = "business_concise"


class DataRecord(BaseModel):
    """单品价格数据记录"""
    commodity: str
    scope: str
    price_type: str
    unit: str
    asof_date: str
    price_cur: float
    refs: Dict[str, float] = Field(default_factory=dict)  # {"D-1": 20.95, "W-1": 21.10, ...}
    source_name: str
    source_url: Optional[str] = None
    notes: Optional[str] = ""


class DerivedMetrics(BaseModel):
    """派生指标"""
    delta_abs: Dict[str, float] = Field(default_factory=dict)      # {"D-1": Δ, "W-1": Δ, ...}
    delta_pct: Dict[str, float] = Field(default_factory=dict)      # {"D-1": δ(%), ...}
    trend: str                                                     # up/down/flat（按 D-1 判定）
    anomaly: bool = False                                          # 是否异常跳点
    missing_refs: List[str] = Field(default_factory=list)         # 缺失的参考期


class BulletinOutput(BaseModel):
    """快报输出"""
    one_line: str
    three_lines: str
    audit: Dict[str, str] = Field(default_factory=dict)           # 来源、口径、版本等