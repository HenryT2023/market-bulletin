"""
指标计算模块 - 派生指标与判定规则
"""
from typing import Dict, List
from schemas import DataRecord, DerivedMetrics


def _pct(cur: float, ref: float) -> float:
    """计算百分比变动"""
    if ref == 0:
        return 0.0
    return (cur - ref) / ref * 100.0


def derive_metrics(rec: DataRecord, cfg_rules: Dict) -> DerivedMetrics:
    """
    计算派生指标
    
    Args:
        rec: 数据记录
        cfg_rules: 规则配置
    
    Returns:
        派生指标对象
    """
    delta_abs, delta_pct, missing = {}, {}, []
    
    # 计算各参考期的绝对变动和百分比变动
    for code, ref in rec.refs.items():
        if ref is None:
            missing.append(code)
            continue
        delta_abs[code] = round(rec.price_cur - ref, 4)
        delta_pct[code] = round(_pct(rec.price_cur, ref), 3)

    # 趋势判定（按 D-1 判定）
    flat_th = cfg_rules.get("flat_threshold_pct", 0.3)
    d1 = delta_pct.get("D-1", 0.0)
    
    if abs(d1) < flat_th:
        trend = "flat"
    else:
        trend = "up" if d1 > 0 else "down"

    # 异常判定（也可引入σ、回归斜率等更复杂规则）
    anomaly = abs(d1) >= cfg_rules.get("anomaly_pct", 8.0)

    return DerivedMetrics(
        delta_abs=delta_abs,
        delta_pct=delta_pct,
        trend=trend,
        anomaly=anomaly,
        missing_refs=missing
    )


def calculate_volatility(prices: List[float]) -> float:
    """
    计算价格波动率（标准差）
    
    Args:
        prices: 价格序列
    
    Returns:
        标准差
    """
    if len(prices) < 2:
        return 0.0
    
    mean_price = sum(prices) / len(prices)
    variance = sum((p - mean_price) ** 2 for p in prices) / (len(prices) - 1)
    return variance ** 0.5


def detect_anomaly_advanced(rec: DataRecord, historical_prices: List[float], cfg_rules: Dict) -> bool:
    """
    高级异常检测（基于历史波动率）
    
    Args:
        rec: 当前数据记录
        historical_prices: 历史价格序列
        cfg_rules: 规则配置
    
    Returns:
        是否异常
    """
    if len(historical_prices) < 7:
        # 历史数据不足，使用简单规则
        d1 = abs((rec.price_cur - rec.refs.get("D-1", rec.price_cur)) / rec.refs.get("D-1", 1) * 100)
        return d1 >= cfg_rules.get("anomaly_pct", 8.0)
    
    # 计算3σ规则
    volatility = calculate_volatility(historical_prices)
    mean_price = sum(historical_prices) / len(historical_prices)
    
    # 当前价格偏离均值超过3个标准差视为异常
    deviation = abs(rec.price_cur - mean_price)
    return deviation > 3 * volatility