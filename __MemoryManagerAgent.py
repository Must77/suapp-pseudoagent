import requests
import json
import time

from myutils import OLLAMA_URL, MODEL_NAME, TIMEOUT

system_prompt = """
You are a Memory Manager Agent for a mobile power management system.

TASK:
Analyze user behavior and infer user intent based on the provided Input Data.

OUTPUT FORMAT (JSON):
{
    "inference": {
        "user_intent_detected": <true|false>,
        "intent_type": "<intent_description>",
        "confidence": <0.0-1.0>,
        "recommendation": "<action_recommendation>"
    }
}

INTENT TYPES:
- increase_brightness_for_reading
- decrease_brightness_for_battery
- enable_feature_for_task
- reject_system_suggestion

RULES:
1. If user manually adjusted a setting (e.g., brightness) recently, infer intent based on direction (increase/decrease).
2. If user overrode a system action, record as negative feedback.
3. Recommend "LOCK" for user-adjusted settings to prevent system override.
4. Keep recommendation actionable.
"""


# TODO: 如何实现记忆存取, 要存多长时间的记忆, 存取记忆的频率

# TODO: input['query']['type'] 字段的来源
# TODO: output['long_term_memory']['user_preferences'] 字段的来源

# TODO: MemManager 是一个 Trigger 吗? 是 db Manager 吗?

def memory_manager_agent(input_event, current_memory_state):
    """
    Memory Manager Agent
    Args:
        input_event (dict): 当前发生的事件或查询
        current_memory_state (dict): 当前数据库中的记忆状态 (模拟从数据库读取)
    Returns:
        dict: 完整的输出接口 JSON
    """
    
    # --- 步骤 1: Python 数据处理 (模拟记忆检索与更新) ---
    # 在实际系统中，这里会连接 SQLite/Redis
    
    # 提取短期记忆和长期记忆用于构建 Prompt
    short_term_memory = current_memory_state.get("short_term_memory", {})
    long_term_memory = current_memory_state.get("long_term_memory", {})
    
    # --- 步骤 2: 构建 LLM Prompt 进行推理 ---
    

    # 构建发送给模型的数据，清晰区分“当前事件”和“记忆背景”
    llm_input_data = {
        "CURRENT_EVENT": input_event,
        "BACKGROUND_MEMORY": {
            "recent_actions": short_term_memory.get("recent_user_actions", []),
            "system_actions": short_term_memory.get("recent_system_actions", []),
            "preferences": long_term_memory.get("user_preferences", {})
        }
    }
    
    user_content = f"INPUT DATA:\n{json.dumps(llm_input_data, indent=2)}"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1} # 低温以保证逻辑严密
    }

    inference_result = {}

    try:
        print(f"Memory Agent 正在推理意图 (Model: {MODEL_NAME})...")
        start_time = time.time()
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            content = result['message']['content']
            parsed_llm_output = json.loads(content)
            
            # 提取 inference 块
            inference_result = parsed_llm_output.get("inference", parsed_llm_output)
            
            print(f"推理完成，耗时: {time.time() - start_time:.2f}s")
        else:
            print(f"Error: {response.status_code}")
            inference_result = {"error": "LLM request failed"}

    except Exception as e:
        print(f"推理异常: {e}")
        inference_result = {"error": str(e)}

    # --- 步骤 3: 组装最终输出 ---
    # 将 Python 管理的记忆数据与 LLM 生成的推理数据合并
    final_output = {
        "short_term_memory": short_term_memory,
        "long_term_memory": long_term_memory,
        "inference": inference_result
    }
    
    return final_output

# --- 测试代码 ---
if __name__ == "__main__":
    # 1. 模拟输入事件 (用户手动把亮度从 50 调到了 80)
    mock_input_event = {
        "event_type": "user_action",
        "event_data": {
            "action": "manual_brightness_change",
            "from_value": 50,
            "to_value": 80,
            "timestamp": 1234567890
        }
    }

    # 2. 模拟当前系统内已有的记忆状态 (这里手动构造，实际中应从数据库取)
    mock_current_memory_state = {
        "short_term_memory": {
            "recent_user_actions": [
                # 假设这是刚刚发生的动作，已经被写入了 DB
                {
                    "action": "manual_brightness_change",
                    "from": 50,
                    "to": 80,
                    "timestamp": 1234567890,
                    "time_ago_seconds": 0
                }
            ],
            "recent_system_actions": [
                {
                    "policy_id": "nav_low_battery_001",
                    "executed_at": 1234567800,
                    "user_override": False
                }
            ]
        },
        "long_term_memory": {
            "user_preferences": {
                "grayscale_mode": "REJECTED",
                "visual_quality_priority": "HIGH"
            }
        }
    }

    # 运行 Agent
    output = memory_manager_agent(mock_input_event, mock_current_memory_state)
    
    print("\n--- Memory Manager Output ---")
    print(json.dumps(output, ensure_ascii=False, indent=2))

typical_result = """
--- Memory Manager Output ---
{
  "short_term_memory": {
    "recent_user_actions": [
      {
        "action": "manual_brightness_change",
        "from": 50,
        "to": 80,
        "timestamp": 1234567890,
        "time_ago_seconds": 0
      }
    ],
    "recent_system_actions": [
      {
        "policy_id": "nav_low_battery_001",
        "executed_at": 1234567800,
        "user_override": false
      }
    ]
  },
  "long_term_memory": {
    "user_preferences": {
      "grayscale_mode": "REJECTED",
      "visual_quality_priority": "HIGH"
    }
  },
  "inference": {
    "user_intent_detected": true,
    "intent_type": "increase_brightness_for_reading",
    "confidence": 1.0,
    "recommendation": "LOCK"
  }
}
"""