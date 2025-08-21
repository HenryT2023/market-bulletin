"""
基础测试样例
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import DataRecord, DerivedMetrics
from derive import derive_metrics
from render import render_output


def test_basic_flow():
    """测试基本流程"""
    # 模拟数据记录
    rec = DataRecord(
        commodity="猪肉",
        scope="全国批发市场",
        price_type="wholesale",
        unit="元/公斤",
        asof_date="2025-08-21",
        price_cur=20.80,
        refs={"D-1": 20.95, "W-1": 21.10, "M-1": 20.10},
        source_name="农业农村部监测"
    )
    
    # 配置规则
    rules = {
        "flat_threshold_pct": 0.3,
        "hint_trigger_pct": 1.0,
        "anomaly_pct": 8.0
    }
    
    style = {
        "include_source": True,
        "include_hint": "auto"
    }
    
    # 计算指标
    met = derive_metrics(rec, rules)
    
    # 渲染输出
    out = render_output(rec, met, style, rules)
    
    print("=== 测试结果 ===")
    print(f"趋势: {met.trend}")
    print(f"异常: {met.anomaly}")
    print(f"一句话: {out.one_line}")
    print(f"三句话:\n{out.three_lines}")
    
    return True


if __name__ == "__main__":
    test_basic_flow()