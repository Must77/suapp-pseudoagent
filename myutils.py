import requests
import json
import traceback

# OLLAMA_URL = "http://raspberrypi.local:11434/api/generate" 
OLLAMA_URL = "http://raspberrypi.local:11434/api/chat" 

MODEL_NAME = "qwen2.5-coder:1.5b"
# MODEL_NAME = "gemma3:4b"

TIMEOUT = 240

def test_ask(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False  # 一次性拿到结果，无需处理流式数据
    }
    
    try:
        print(f"正在发送请求给 {payload['model']}...")
        response = requests.post(OLLAMA_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("-" * 20)
            print(result['response'])
            print("-" * 20)
        else:
            print(f"请求失败: {response.status_code}, {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"无法连接到 {OLLAMA_URL}，请检查树莓派IP或防火墙设置。")
    except Exception as e:
        print(f"发生错误: {e.__class__.__name__}: {e}")
        traceback.print_exc()  # 添加详细的异常堆栈跟踪


def ask_llm_json(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"  # 强制返回 JSON 格式
    }
    
    try:
        print(f"正在发送请求给 {payload['model']}...")
        response = requests.post(OLLAMA_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            content = result['response']
            # 解析返回的 JSON 字符串为 Python 字典
            parsed_json = json.loads(content)
            return parsed_json
        else:
            print(f"请求失败: {response.status_code}, {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"无法连接到 {OLLAMA_URL}，请检查树莓派IP或防火墙设置。")
        return None
    except json.JSONDecodeError:
        print("模型返回了非法的 JSON 格式")
        print("Raw content:", content)
        return None
    except Exception as e:
        print(f"发生错误: {e.__class__.__name__}: {e}")
        traceback.print_exc()  # 添加详细的异常堆栈跟踪
        return None

def ask_llm_real(prompt):
    api_key = "sk-wwolcqsmeztifuouqxehvchcoobuwwokzqjmyckenzhknbab"
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",   # 也可换 DeepSeek-R1、qwen 等
        "messages": [{"role": "user", "content": "用一句话介绍 Python"}],
        "max_tokens": 500,
        "temperature": 0.7
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    print(resp.json())

if __name__ == "__main__":
    test_prompt = "使用Python编写一个HelloWorld, 只要纯代码, 不要解释"
    ask_llm_real(test_prompt)