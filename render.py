"""
文案渲染模块 - 一句话/三句话快报生成
"""
from schemas import DataRecord, DerivedMetrics, BulletinOutput


def _fmt_pct(x: float, fmt="0.0%") -> str:
    """格式化百分比"""
    return f"{x:.1f}%"


def _fmt_num(x: float, fmt="0.00") -> str:
    """格式化数字"""
    return f"{x:.2f}"


def _direction(trend: str) -> str:
    """趋势方向中文描述"""
    return {"up": "上涨", "down": "下降", "flat": "持平"}.get(trend, "持平")


def render_one_line(rec: DataRecord, met: DerivedMetrics, style: dict, rules: dict) -> str:
    """
    渲染一句话快报
    
    Args:
        rec: 数据记录
        met: 派生指标
        style: 样式配置
        rules: 规则配置
    
    Returns:
        一句话快报文本
    """
    d1 = met.delta_pct.get("D-1", 0.0)
    d1_abs = met.delta_abs.get("D-1", 0.0)
    dir_word = _direction(met.trend)
    date_str = rec.asof_date
    src = f"（来源：{rec.source_name}）" if style.get("include_source", True) else ""

    # 平稳 ⇒ 不显示括号
    if met.trend == "flat":
        return f"{date_str}，{rec.scope}{rec.commodity}均价{_fmt_num(rec.price_cur)}{rec.unit}，较昨日{dir_word}。{src}"

    return (f"{date_str}，{rec.scope}{rec.commodity}均价{_fmt_num(rec.price_cur)}{rec.unit}，"
            f"较昨日{dir_word}{_fmt_pct(abs(d1))}（{_fmt_num(d1_abs)}{rec.unit}）。{src}")


def render_three_lines(rec: DataRecord, met: DerivedMetrics, style: dict, rules: dict) -> str:
    """
    渲染三句话快报
    
    Args:
        rec: 数据记录
        met: 派生指标
        style: 样式配置
        rules: 规则配置
    
    Returns:
        三句话快报文本
    """
    src = f"（来源：{rec.source_name}）" if style.get("include_source", True) else ""
    
    # 行1：当日 vs 昨日
    line1 = render_one_line(rec, met, style, rules).replace(src, "")  # 先移除来源，最后统一加

    # 行2：上周、上月（缺失时跳过）
    parts = []
    if "W-1" in met.delta_pct:
        w = met.delta_pct["W-1"]
        dw = "上涨" if w > 0 else ("下降" if w < 0 else "持平")
        parts.append(f"较上周{dw}{_fmt_pct(abs(w))}")
    if "M-1" in met.delta_pct:
        m = met.delta_pct["M-1"]
        dm = "上涨" if m > 0 else ("下降" if m < 0 else "持平")
        parts.append(f"较上月{dm}{_fmt_pct(abs(m))}")
    
    line2 = "；".join(parts) + "。" if parts else ""

    # 行3：提示（规则触发，≤20字；这里先用 notes，后续可接小模型生成）
    hint = ""
    trigger = (style.get("include_hint", "auto") != "never" and 
               abs(met.delta_pct.get("D-1", 0.0)) >= rules.get("hint_trigger_pct", 1.0))
    
    if trigger:
        hint = (rec.notes or "暂无明显驱动") + "。"

    # 组装三行
    lines = [line1.strip(), line2.strip(), (hint + src).strip()]
    return "\n".join([line for line in lines if line]).strip()


def render_output(rec: DataRecord, met: DerivedMetrics, style: dict, rules: dict) -> BulletinOutput:
    """
    渲染完整输出
    
    Args:
        rec: 数据记录
        met: 派生指标
        style: 样式配置
        rules: 规则配置
    
    Returns:
        快报输出对象
    """
    return BulletinOutput(
        one_line=render_one_line(rec, met, style, rules),
        three_lines=render_three_lines(rec, met, style, rules),
        audit={
            "asof_date": rec.asof_date,
            "scope": rec.scope,
            "price_type": rec.price_type,
            "unit": rec.unit,
            "source": rec.source_name,
            "spec_version": "1.0.0",
            "anomaly": str(met.anomaly),
            "trend": met.trend
        }
    )