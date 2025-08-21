"""
主入口 - 市场价格快报生成器
"""
import yaml
from datetime import date
from typing import List

from schemas import DataRecord
from repo_adapter import fetch_price, fetch_ref_price
from derive import derive_metrics
from render import render_output
from publisher import publish_stdout, publish_file, publish_wecom
from utils import setup_logger, parse_date, validate_config


def load_config(config_path: str = "app.cfg.yaml") -> dict:
    """加载配置文件"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ 配置文件未找到: {config_path}")
        raise
    except yaml.YAMLError as e:
        print(f"❌ 配置文件格式错误: {e}")
        raise


def process_commodity(commodity: str, run_date: str, cfg: dict, logger) -> DataRecord:
    """处理单个商品的价格数据"""
    logger.info(f"处理商品: {commodity}")
    
    # 获取当日价格
    price_cur = fetch_price(run_date, commodity, cfg["scope"], cfg["price_type"], cfg["unit"])
    
    if price_cur is None:
        logger.warning(f"未找到 {commodity} 在 {run_date} 的价格数据")
        return None
    
    # 获取参考期价格
    refs = {}
    for ref_code in cfg["references"]:
        ref_price = fetch_ref_price(run_date, commodity, cfg["scope"], 
                                  cfg["price_type"], cfg["unit"], ref_code)
        refs[ref_code] = ref_price
        if ref_price is None:
            logger.warning(f"{commodity} 缺少 {ref_code} 参考价格")
    
    # 构建数据记录
    rec = DataRecord(
        commodity=commodity,
        scope=cfg["scope"],
        price_type=cfg["price_type"],
        unit=cfg["unit"],
        asof_date=run_date,
        price_cur=price_cur,
        refs=refs,
        source_name="农业农村部监测",  # 可配置化
        source_url="",
        notes=""
    )
    
    return rec


def run():
    """主运行函数"""
    # 设置日志
    logger = setup_logger()
    logger.info("启动市场价格快报生成器")
    
    try:
        # 加载配置
        cfg = load_config()
        if not validate_config(cfg):
            return
        
        # 解析运行日期
        run_date_obj = parse_date(cfg.get("run_date", "auto"))
        if run_date_obj is None:
            logger.error("无效的运行日期")
            return
        
        run_date = run_date_obj.isoformat()
        logger.info(f"生成日期: {run_date}")
        
        # 处理所有商品
        outputs = []
        for commodity in cfg["commodities"]:
            try:
                rec = process_commodity(commodity, run_date, cfg, logger)
                if rec is None:
                    continue
                
                # 计算派生指标
                met = derive_metrics(rec, cfg["rules"])
                
                # 异常检查
                if met.anomaly:
                    logger.warning(f"{commodity} 价格异常波动，建议人工审核")
                
                # 渲染输出
                out = render_output(rec, met, cfg["style"], cfg["rules"])
                outputs.append(out)
                
                logger.info(f"✅ {commodity} 快报生成完成")
                
            except Exception as e:
                logger.error(f"处理 {commodity} 时出错: {e}")
                continue
        
        if not outputs:
            logger.warning("没有生成任何快报")
            return
        
        # 发布快报
        texts = [o.one_line for o in outputs]  # 默认使用一句话版本
        
        publisher_cfg = cfg["publisher"]
        mode = publisher_cfg["mode"]
        
        if mode == "stdout":
            publish_stdout(texts)
        elif mode == "file":
            path = publisher_cfg["file_path"].replace("{{date}}", run_date)
            publish_file(path, texts)
        elif mode == "wecom":
            webhook = publisher_cfg.get("wecom_webhook")
            if webhook:
                publish_wecom(webhook, texts)
            else:
                logger.error("企业微信webhook未配置")
        else:
            logger.error(f"不支持的发布模式: {mode}")
        
        logger.info(f"✅ 快报生成完成，共 {len(outputs)} 条")
        
    except Exception as e:
        logger.error(f"运行失败: {e}")
        raise


if __name__ == "__main__":
    run()