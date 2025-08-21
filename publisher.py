"""
推送模块 - 支持终端输出、文件保存、企业微信机器人
"""
import json
import requests
import os
from typing import List


def publish_stdout(texts: List[str]) -> None:
    """输出到终端"""
    print("\n" + "="*50)
    print("📊 市场价格快报")
    print("="*50)
    for i, text in enumerate(texts, 1):
        print(f"\n【{i}】 {text}")
    print("\n" + "="*50)


def publish_file(path: str, texts: List[str]) -> None:
    """保存到文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("市场价格快报\n")
        f.write("="*30 + "\n\n")
        for i, text in enumerate(texts, 1):
            f.write(f"【{i}】 {text}\n\n")
    
    print(f"✅ 快报已保存到: {path}")


def publish_wecom(webhook: str, texts: List[str]) -> None:
    """推送到企业微信群"""
    if not webhook:
        print("❌ 企业微信webhook未配置")
        return
    
    try:
        # 组装消息内容
        content = "📊 市场价格快报\n" + "\n".join(f"• {text}" for text in texts)
        
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        response = requests.post(
            webhook, 
            data=json.dumps(data, ensure_ascii=False),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("errcode") == 0:
                print("✅ 企业微信推送成功")
            else:
                print(f"❌ 企业微信推送失败: {result.get('errmsg')}")
        else:
            print(f"❌ 企业微信推送失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 企业微信推送异常: {e}")


def publish_markdown(texts: List[str], title: str = "市场价格快报") -> str:
    """生成Markdown格式（用于公众号等）"""
    md_content = f"# {title}\n\n"
    md_content += f"*生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    for i, text in enumerate(texts, 1):
        md_content += f"## {i}. {text.split('，')[1].split('均价')[0] if '，' in text else f'商品{i}'}\n\n"
        md_content += f"{text}\n\n"
    
    md_content += "---\n\n"
    md_content += "*免责声明：本快报仅供参考，不构成投资建议。价格数据来源于公开市场信息，请以实际交易为准。*\n"
    
    return md_content


def publish_json(texts: List[str], metadata: dict = None) -> dict:
    """生成JSON格式（用于API接口）"""
    return {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "bulletins": [
            {
                "id": i,
                "content": text,
                "commodity": text.split('，')[1].split('均价')[0] if '，' in text else f"商品{i}"
            }
            for i, text in enumerate(texts, 1)
        ],
        "metadata": metadata or {},
        "version": "1.0.0"
    }