# 市场价格快报生成器

一个专业的"当日市场价格走势 → 一句话/三句快报"系统，支持企业微信机器人推送。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据源

编辑 `repo_adapter.py` 中的 `fetch_price` 和 `fetch_ref_price` 函数，接入你的数据源：

```python
def fetch_price(date_str: str, commodity: str, scope: str, price_type: str, unit: str):
    # TODO: 替换为你的数据查询逻辑
    # 例如：SQL查询、HTTP API、CSV文件等
    pass
```

### 3. 运行测试

```bash
python tests/test_basic.py
```

### 4. 生成快报

```bash
python main.py
```

## 📁 项目结构

```
market-bulletin/
├── app.cfg.yaml          # 运行配置
├── main.py               # 主入口
├── schemas.py            # 数据模型
├── repo_adapter.py       # 数据适配层（需要你填充）
├── derive.py             # 指标计算
├── render.py             # 文案渲染
├── publisher.py          # 推送模块
├── utils.py              # 工具函数
├── requirements.txt      # 依赖包
└── tests/                # 测试用例
```

## ⚙️ 配置说明

### 基础配置 (app.cfg.yaml)

```yaml
run_date: "auto"                 # "auto"=今天，或指定 yyyy-mm-dd
scope: "全国批发市场"
price_type: "wholesale"
unit: "元/公斤"

commodities:                     # 要发布的品类
  - 猪肉
  - 大米
  - 黑胡椒

references: ["D-1", "W-1", "M-1"]  # 对比口径

publisher:
  mode: "stdout"                 # stdout/file/wecom
  wecom_webhook: ""              # 企业微信机器人webhook
```

### 推送模式

- **stdout**: 终端输出
- **file**: 保存到文件
- **wecom**: 企业微信群推送

## 🔌 数据源适配

### CSV文件示例

```python
def fetch_price(date_str, commodity, scope, price_type, unit):
    import pandas as pd
    df = pd.read_csv("data/prices.csv")
    result = df.query(f"date=='{date_str}' and commodity=='{commodity}'")
    return float(result.iloc[0]['price']) if not result.empty else None
```

### 数据库示例

```python
def fetch_price(date_str, commodity, scope, price_type, unit):
    import psycopg2
    conn = psycopg2.connect(host="localhost", database="market", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM prices WHERE date=%s AND commodity=%s", (date_str, commodity))
    result = cursor.fetchone()
    conn.close()
    return float(result[0]) if result else None
```

### HTTP API示例

```python
def fetch_price(date_str, commodity, scope, price_type, unit):
    import requests
    response = requests.get(f"https://api.example.com/price/{commodity}/{date_str}")
    return response.json().get('price') if response.status_code == 200 else None
```

## 📊 输出示例

### 一句话快报
```
2025-08-21，全国批发市场猪肉均价20.80元/公斤，较昨日下降0.7%（-0.15元/公斤）。（来源：农业农村部监测）
```

### 三句话快报
```
2025-08-21，全国批发市场猪肉均价20.80元/公斤，较昨日下降0.7%（-0.15元/公斤）。
较上周下降1.4%；较上月上涨3.5%。
暂无明显驱动。（来源：农业农村部监测）
```

## 🤖 企业微信机器人配置

1. 在企业微信群中添加机器人
2. 获取webhook地址
3. 在 `app.cfg.yaml` 中配置：

```yaml
publisher:
  mode: "wecom"
  wecom_webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
```

## ⏰ 定时任务

使用cron设置每日定时推送：

```bash
# 每天上午9点执行
0 9 * * * cd /path/to/market-bulletin && python main.py
```

## 🔧 高级功能

### 异常检测
- 当日变动 ≥8% 自动标记异常
- 支持基于历史波动率的3σ检测

### 质量控制
- 口径透明：周价承载日更时自动标注
- 可溯源：audit字段记录完整元数据
- 缺失处理：参考期缺失时降级生成

### 扩展接口
- JSON格式输出（API接口）
- Markdown格式（公众号）
- 自定义文案模板

## 📝 开发指南

### 添加新的推送渠道

在 `publisher.py` 中添加新函数：

```python
def publish_custom(texts: List[str], config: dict):
    # 你的推送逻辑
    pass
```

### 自定义指标计算

在 `derive.py` 中扩展 `derive_metrics` 函数：

```python
def derive_metrics(rec: DataRecord, cfg_rules: Dict) -> DerivedMetrics:
    # 添加你的自定义指标
    pass
```

## 🚨 注意事项

1. **数据源配置**：必须实现 `repo_adapter.py` 中的两个函数
2. **异常处理**：建议对异常波动进行人工审核
3. **口径一致**：确保所有价格数据使用统一单位
4. **定时任务**：建议在交易时间后运行，确保数据完整性

## 📞 技术支持

如有问题，请检查：
1. 配置文件格式是否正确
2. 数据源连接是否正常
3. 依赖包是否完整安装
4. 日志输出中的错误信息