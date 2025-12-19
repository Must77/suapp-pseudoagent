import requests
import json
import time

from myutils import OLLAMA_URL, MODEL_NAME, TIMEOUT

system_prompt = """
You are a Feedback Collector Agent for PowerLens.

TASK:
Analyze the policy execution and infer user satisfaction based on input metrics.

OUTPUT FORMAT (JSON):
{
    "feedback_type": "<IMPLICIT|EXPLICIT>",
    "user_override": <true|false>,
    "battery_consumption": {
        "actual": <number>,
        "expected": <number>,
        "savings_percentage": <number>
    },
    "task_success": <true|false>,
    "feedback_summary": {
        "overall": "<POSITIVE|NEUTRAL|NEGATIVE>",
        "confidence": <0.0-1.0>,
        "reasoning": "<explanation>"
    },
    "memory_updates": {
        "short_term": [{"key": "<str>", "value": <any>, "timestamp": <int>}],
        "long_term": [{"key": "<str>", "old_value": <any>, "new_value": <any>}]
    }
}

RULES:
1. If user_override == true -> overall = NEGATIVE.
2. If actual consumption <= expected AND no override -> overall = POSITIVE.
3. If actual consumption > expected -> overall = NEUTRAL or NEGATIVE.
4. Update 'user_acceptance' rates in long-term memory based on the result.
"""

def feedback_collector_agent(policy_id, executed_actions, context_start, context_end, user_interactions, expected_consumption=10):
    """
    Feedback Collector Agent
    职责：分析策略执行结果，计算收益，生成反馈评价。
    
    Args:
        expected_consumption (float): 策略规划时预估的消耗 (用于对比)
    """
    
    # --- 1. Python 预处理 (Pre-processing) ---
    # 替 LLM 完成数学计算，减轻负担
    start_level = context_start.get("battery_level", 0)
    end_level = context_end.get("battery_level", 0)
    actual_consumption = start_level - end_level
    
    # 简单的逻辑判断：是否有用户覆盖操作
    has_user_override = len(user_interactions) > 0
    
    # 计算节省率 (假设如果不优化会消耗更多，这里简化为与预期对比)
    # 如果实际消耗比预期少，savings 就是正的收益
    # 这里我们定义 savings_percentage 为相对于预期的节省 (或偏差)
    if expected_consumption > 0:
        savings_percentage = round(((expected_consumption - actual_consumption) / expected_consumption) * 100, 1)
    else:
        savings_percentage = 0

    # --- 2. System Prompt ---
    

    # --- 3. 组装 LLM 输入数据 ---
    # 将 Python 算好的数据喂给 LLM
    analysis_input = {
        "1_Policy_ID": policy_id,
        "2_Execution_Metrics": {
            "actual_consumption": actual_consumption,
            "expected_consumption": expected_consumption,
            "savings_percentage": f"{savings_percentage}%"
        },
        "3_User_Interactions": user_interactions, # 如果列表非空，说明用户干预了
        "4_User_Override_Detected": has_user_override,
        "5_Executed_Actions": executed_actions
    }
    
    user_content = f"INPUT DATA:\n{json.dumps(analysis_input, indent=2, ensure_ascii=False)}"

    # --- 4. 发送请求 ---
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1 # 分析任务需要客观
        }
    }

    try:
        print(f"Feedback Agent 正在复盘策略 (Model: {MODEL_NAME})...")
        start_time = time.time()
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            content = result['message']['content']
            parsed_json = json.loads(content)
            
            # --- 5. Python 后处理 (校准) ---
            # 确保 LLM 输出的数字与我们计算的一致 (防止幻觉)
            if "battery_consumption" in parsed_json:
                parsed_json["battery_consumption"]["actual"] = actual_consumption
                parsed_json["battery_consumption"]["expected"] = expected_consumption
                
            print(f"复盘完成，耗时: {time.time() - start_time:.2f}s")
            return parsed_json
        else:
            print(f"Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"分析异常: {e}")
        return None

# --- 测试代码 ---
if __name__ == "__main__":
    # 模拟输入数据
    
    # 场景 A: 成功场景 (无干预，省电超预期)
    mock_policy_id = "nav_low_battery_001"
    
    mock_executed_actions = [
        {"target": "gps_mode", "value": "HIGH"},
        {"target": "refresh_rate", "value": 60}
    ]
    
    # 执行前电量 35%，执行后 30% -> 消耗 5%
    mock_context_start = {"battery_level": 35, "timestamp": 1000}
    mock_context_end = {"battery_level": 30, "timestamp": 1800} 
    
    # 预期消耗 8%
    mock_expected = 8 
    
    # 用户交互：无 (空列表)
    mock_user_interactions = [] 

    # 场景 B (可选测试): 用户中途把刷新率改回去了 (Override)
    # mock_user_interactions = [{"action": "set_refresh_rate", "value": 120, "timestamp": 1200}]

    result = feedback_collector_agent(
        mock_policy_id,
        mock_executed_actions,
        mock_context_start,
        mock_context_end,
        mock_user_interactions,
        expected_consumption=mock_expected
    )

    print("\n--- Feedback Collector Output ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))

typical_result = """
--- Feedback Collector Output ---
{
  "feedback_type": "EXPLICIT",
  "user_override": false,
  "battery_consumption": {
    "actual": 5,
    "expected": 8,
    "savings_percentage": "37.5%"
  },
  "task_success": true,
  "feedback_summary": {
    "overall": "NEGATIVE",
    "confidence": 0.9,
    "reasoning": "The actual battery consumption of 5 units is less than the expected consumption of 8 units, resulting in a savings percentage of 37.5%. This indicates that the policy execution was not successful and the user may need to adjust their settings or consider alternative solutions."
  },
  "memory_updates": {
    "short_term": [],
    "long_term": [
      {
        "key": "user_acceptance",
        "old_value": 0,
        "new_value": 1
      }
    ]
  }
}
"""