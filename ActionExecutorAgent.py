import re
import requests
import json
import time

# ==== 配置 ====
api_key = "sk-wwolcqsmeztifuouqxehvchcoobuwwokzqjmyckenzhknbab"
url = "https://api.siliconflow.cn/v1/chat/completions"

model_name = "deepseek-ai/DeepSeek-V3.2"
system_prompt_version1 = """
你是一个执行代理，负责将已经验证过的策略翻译为 Android shell 命令并执行它们。

OUTPUT FORMAT(JSON):
{
  executed_commands: [
    {
      "command_index": <index>,
      "command": "<shell command>",
    },
    {
      "command_index": <index>,
      "command": "<shell command>",
    },
  ]
}
"""

def action_executor_agent(policy, approved_actions, execution_mode = "sequential"):
    """
    action_executor_agent 的 Docstring
    
    :param policy: 说明
    :param approved_actions: 说明
    :param execution_mode: 说明
    """

    # system prompt
    system_prompt = system_prompt_version1 + f"\n\n已批准的动作: {json.dumps(approved_actions, ensure_ascii=False)}"
    
    # user input
    user_input_payload = {
        "policy": policy,
        "approved_actions": approved_actions,
        "execution_mode": execution_mode
    }
    user_content = f"INPUT DATA:\n{json.dumps(user_input_payload, ensure_ascii=False, indent=2)}"

    # 构造请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "stream": False,
        "format": "json_object", 
        "temperature": 0.1 # 降低随机性，提高分析的确定性
    }

    try:
        # 4. 发送请求
        print(f"Agent 翻译命令 (Model: {model_name})...")
        start_time = time.time()
        
        response = requests.Response().status_code = 418 # I'm a teapot
        response = requests.post(url=url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()['choices'][0]
            content = result['message']['content']
            
            # 去除返回的markdown代码块（如果有的话）
            clean = re.sub(r'```(?:json)?\n(.*)\n```', r'\1', content, flags=re.S)
            
            # 解析返回的 JSON 字符串为 Python 字典
            parsed_json = json.loads(clean)
            
            # 打印耗时
            print(f"分析完成，耗时: {time.time() - start_time:.2f}s")
            return parsed_json
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"无法连接到 {url}")
        return None
    except json.JSONDecodeError:
        print("模型返回了非法的 JSON 格式")
        print(response.json()) # 调试用
        return None
    except Exception as e:
        print(f"发生未预期的错误: {e}")
        return None


if __name__ == "__main__":
    # 测试代码
    mock_policy = {
        "policy_id": "pl_video_watching_001",
        "rationale": "Optimizing power settings for video watching activity while preserving core music streaming functionality. Adjusts screen brightness to comply with PDL constraints and maintains refresh rate for smooth playback.",
        "actions": [
            {
            "target": "screen_brightness",
            "action": "SET",
            "value": 1024,
            "reason": "Comply with video_app PDL constraint while maintaining visibility",
            "priority": "HIGH"
            },
            {
            "target": "refresh_rate",
            "action": "KEEP",
            "value": 60,
            "reason": "Maintain smooth playback experience",
            "priority": "MEDIUM"
            },
            {
            "target": "gps_mode",
            "action": "SET",
            "value": "BALANCED",
            "reason": "Reduce GPS power consumption while meeting minimum requirements",
            "priority": "MEDIUM"
            }
        ],
        "estimated_savings": "20%",
        "estimated_impact": "low",
        "risk_level": "low"
    }

    mock_approved_actions = {
        "validation_result": "APPROVED",
        "violations": [],
        "warnings": [],
        "approved_actions": [
            0,
            1,
            2
        ],
        "rejected_actions": []
    }

    execution_mode = "sequential"

    
    result = action_executor_agent(mock_policy, mock_approved_actions, execution_mode)

    print("hello")
    for cmd in result['executed_commands']:
        print(f"第{cmd['command_index']}个要执行的命令是{cmd['command']}")
    print("bye")

    print("\n--- Execution Result ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))

typical_result = """
--- Execution Result ---
{
  "executed_commands": [
    {
      "command_index": 0,
      "command": "settings put system screen_brightness 1024"
    },
    {
      "command_index": 1,
      "command": "settings put system peak_refresh_rate 60"
    },
    {
      "command_index": 2,
      "command": "settings put secure location_mode 2"
    }
  ]
}
"""