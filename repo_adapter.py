"""
数据适配层 - 你需要在这里填入你的数据查询逻辑
"""
from typing import Optional
from datetime import date, datetime, timedelta


def fetch_price(date_str: str, commodity: str, scope: str,
                price_type: str, unit: str) -> Optional[float]:
    """
    返回当日（或最近一期）价格（统一到 unit）。
    TODO: 在这里写上你的查询语句/HTTP调用/CSV读取逻辑。
    若无日频、但有周频，可按配置回退到最新周价。
    
    Args:
        date_str: 查询日期 "YYYY-MM-DD"
        commodity: 商品名称，如"猪肉"
        scope: 市场范围，如"全国批发市场"
        price_type: 价格类型，如"wholesale"
        unit: 单位，如"元/公斤"
    
    Returns:
        价格浮点数，若无数据返回None
    """
    # 示例占位数据（请替换为你的真实查询逻辑）
    sample_data = {
        "猪肉": 20.80,
        "大米": 4.50,
        "黑胡椒": 85.20
    }
    
    # TODO: 替换为你的数据源查询
    # 例如：
    # - SQL查询: SELECT price FROM market_data WHERE date=? AND commodity=?
    # - HTTP API: requests.get(f"https://api.example.com/price/{commodity}/{date_str}")
    # - CSV文件: pd.read_csv("data.csv").query(f"date=='{date_str}' and commodity=='{commodity}'")
    
    return sample_data.get(commodity)


def fetch_ref_price(anchor_date: str, commodity: str, scope: str,
                    price_type: str, unit: str, ref_code: str) -> Optional[float]:
    """
    返回参考期（D-1/W-1/M-1）价格。若缺，返回None。
    你可以在内部计算 ref_date 并查询。
    
    Args:
        anchor_date: 锚点日期 "YYYY-MM-DD"
        commodity: 商品名称
        scope: 市场范围
        price_type: 价格类型
        unit: 单位
        ref_code: 参考期代码，如"D-1"(昨日)、"W-1"(上周)、"M-1"(上月)
    
    Returns:
        参考期价格，若无数据返回None
    """
    # 计算参考日期
    anchor = datetime.strptime(anchor_date, "%Y-%m-%d").date()
    
    if ref_code == "D-1":
        ref_date = anchor - timedelta(days=1)
    elif ref_code == "W-1":
        ref_date = anchor - timedelta(weeks=1)
    elif ref_code == "M-1":
        # 简化处理，实际可能需要更精确的月份计算
        ref_date = anchor - timedelta(days=30)
    else:
        return None
    
    ref_date_str = ref_date.strftime("%Y-%m-%d")
    
    # 示例占位数据（请替换为你的真实查询逻辑）
    sample_refs = {
        "猪肉": {"D-1": 20.95, "W-1": 21.10, "M-1": 20.10},
        "大米": {"D-1": 4.48, "W-1": 4.52, "M-1": 4.35},
        "黑胡椒": {"D-1": 84.50, "W-1": 83.80, "M-1": 82.10}
    }
    
    # TODO: 替换为你的数据源查询
    # 使用计算出的 ref_date_str 查询对应日期的价格
    
    return sample_refs.get(commodity, {}).get(ref_code)


# 以下是三种常见数据源的参考实现，你可以根据需要选择并修改

def fetch_price_from_csv(date_str: str, commodity: str, csv_path: str = "data/prices.csv") -> Optional[float]:
    """从CSV文件查询价格的参考实现"""
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        result = df.query(f"date=='{date_str}' and commodity=='{commodity}'")
        if not result.empty:
            return float(result.iloc[0]['price'])
    except Exception as e:
        print(f"CSV查询错误: {e}")
    return None


def fetch_price_from_db(date_str: str, commodity: str, db_config: dict) -> Optional[float]:
    """从PostgreSQL数据库查询价格的参考实现"""
    try:
        import psycopg2
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        query = """
        SELECT price FROM market_prices 
        WHERE date = %s AND commodity = %s AND scope = %s AND price_type = %s
        ORDER BY updated_at DESC LIMIT 1
        """
        cursor.execute(query, (date_str, commodity, "全国批发市场", "wholesale"))
        result = cursor.fetchone()
        
        conn.close()
        return float(result[0]) if result else None
    except Exception as e:
        print(f"数据库查询错误: {e}")
    return None


def fetch_price_from_api(date_str: str, commodity: str, api_config: dict) -> Optional[float]:
    """从HTTP API查询价格的参考实现"""
    try:
        import requests
        
        url = f"{api_config['base_url']}/price"
        params = {
            'date': date_str,
            'commodity': commodity,
            'scope': api_config.get('scope', '全国批发市场'),
            'type': api_config.get('price_type', 'wholesale')
        }
        headers = {'Authorization': f"Bearer {api_config.get('token', '')}"}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data.get('price'))
    except Exception as e:
        print(f"API查询错误: {e}")
    return None