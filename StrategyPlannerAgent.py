import re
import requests
import json
import time
import uuid

# ==== 配置 ====
api_key = "sk-wwolcqsmeztifuouqxehvchcoobuwwokzqjmyckenzhknbab"
url = "https://api.siliconflow.cn/v1/chat/completions"

model_name = "deepseek-ai/DeepSeek-V3"
system_prompt_version1 = """
You are a Strategy Planner Agent for PowerLens, a context-aware mobile power management system.

TASK:
Generate a power management policy that:
- Maximizes battery life
- Preserves user experience and core functionality
- Respects user intent and manual adjustments
- Complies with all constraints

OUTPUT FORMAT (JSON):
{
"policy_id": "<unique_id>",
"rationale": "<brief_explanation>",
"actions": [
    {
    "target": "<parameter_name>",
    "action": "<KEEP|SET|DEFER|KILL|ENABLE|DISABLE|LOCK>",
    "value": <value>,
    "reason": "<brief_reason>",
    "priority": "<CRITICAL|HIGH|MEDIUM|LOW>"
    }
],
"estimated_savings": "<percentage>",
"estimated_impact": "<minimal|low|medium|high>",
"risk_level": "<low|medium|high>"
}

AVAILABLE TARGETS:
- gps_mode: [HIGH, BALANCED, LOW]
- screen_brightness: [0, 4096]
- refresh_rate: [60, 90, 120]

RULES:
1. ALWAYS respect user manual adjustments (use LOCK action).
2. NEVER violate CRITICAL constraints from PDL.
3. Prioritize actions based on battery impact vs. user experience.
4. Use retrieved strategies as templates but adapt to current context.
5. Provide clear rationale.
"""

# TODO: 策略合成的输入中有用户的操作，那是每次用户操作都要调用一次策略合成吗
def strategy_planner_agent(context_summary, activity_result, memory_result, retrieved_strategies, pdl_constraints):
    """
    Strategy Planner Agent (Policy Composer)
    综合多方信息，生成最终电源管理策略。
    """
    
    # --- 1. System Prompt (完全遵循你的设计) ---
    system_prompt = system_prompt_version1

    # --- 2. 组装 Input Data (关键：数据清洗与精简) ---
    input_payload = {
        "Device_Context": context_summary,         # 电池、环境等
        "User_Activity": activity_result,          # 正在干什么
        "Memory_Intent": memory_result,            # 用户刚刚手动调了啥
        "Retrieved_Strategies": retrieved_strategies, # 知识库查到的参考模板
        "PDL_Constraints": pdl_constraints       # 硬性约束 (e.g. 导航时GPS不能关)
    }
    
    user_content = f"INPUT DATA:\n{json.dumps(input_payload, indent=2, ensure_ascii=False)}"

    # --- 3. 构造请求 ---
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "stream": False,
        "format": "json_object", 
        "temperature": 0.2 # 稍微有点创造性以适配策略，但要保持稳定
    }

    try:
        print(f"Strategy Planner 正在生成策略 (Model: {model_name})...")
        start_time = time.time()
        
        response = requests.post(url, headers=headers, json=payload, timeout=120) # 这是一个复杂的任务，超时时间设长一点
        
        if response.status_code == 200:
            result = response.json()['choices'][0]
            content = result['message']['content']
            clean = re.sub(r'```(?:json)?\n(.*)\n```', r'\1', content, flags=re.S)
            parsed_json = json.loads(clean)
            
            # 补全 policy_id (如果模型生成的只是占位符)
            if parsed_json.get("policy_id") == "<unique_id>" or not parsed_json.get("policy_id"):
                parsed_json["policy_id"] = f"policy_{uuid.uuid4().hex[:8]}"
                
            print(f"策略生成完成，耗时: {time.time() - start_time:.2f}s")
            return parsed_json
        else:
            print(f"Error: {response.status_code}")
            return _generate_fallback_policy("LLM Request Failed")
    
    except requests.exceptions.ConnectionError:
        print(f"无法连接到 {url}")
        return None
    except json.JSONDecodeError:
        print("模型返回了非法的 JSON 格式")
        print(response.json()) # 调试用
        return None
    except Exception as e:
        print(f"发生未预期的错误: {e}")
        return _generate_fallback_policy(str(e))


def _generate_fallback_policy(reason):
    """
    [MOCK/Safety] 兜底策略生成器
    当 LLM 挂了或者超时，系统必须返回一个安全的策略，而不是崩溃。
    """
    print(f"!!! 触发兜底策略 (原因: {reason}) !!!")
    return {
        "policy_id": f"fallback_{uuid.uuid4().hex[:8]}",
        "rationale": f"系统处于故障安全模式。原因: {reason}",
        "actions": [
            {
                "target": "screen_brightness",
                "action": "KEEP", # 保持现状是最安全的
                "value": None,
                "reason": "Fail-safe mode",
                "priority": "CRITICAL"
            }
        ],
        "estimated_savings": "0%",
        "estimated_impact": "minimal",
        "risk_level": "low"
    }

# --- 测试代码 ---
if __name__ == "__main__":
    # ==========================
    # 模拟上游 Agent 的输出数据
    # ==========================
    
    # 1. Context (来自 Sensor)
    mock_context = {
        "screenBrightness": 4096,
        "isScreenOn": True,
        "screenTimeout": 600000,
        "screenRefreshRate": 60.000004,
        "isWifiEnabled": True,
        "isBluetoothEnabled": False,
        "isNFCEnabled": False,
        "isMobileDataEnabled": False,
        "isAutoRotationEnabled": False,
        "gpsMode": 3,
        "gnssRate": -1,
        "isVolumeMuted": False,
        "mediaVolume": 25,
        "alarmVolume": 3,
        "ringVolume": 6,
        "notificationVolume": 5,
        
        "getBatteryPercentage": 100
    }
    
    # 2. Activity (来自 Agent 2)
    mock_activity = {
        "activity": "VIDEO_WATCHING",
        "confidence": 0.9,
        "sub_activity": "Music Streaming",
        "context_tags": {
            "app": "com.kugou.android",
            "ui_state": "Music Player",
            "user_intent": "Listening to music",
            "environment": "Indoor",
            "critical_level": "MEDIUM"
        },
        "reasoning": "The UI tree shows a music player interface with controls like play, pause, and seek bar, indicating the user is streaming music."
    }
    
    # 3. Memory (来自 Agent 3)
    # 假设用户刚刚什么都没干
    mock_memory = {
        "action": "NONE",
    }
    
    # 4. Retrieved Strategies (来自 Agent 4)
    mock_strategies = {
        "retrieved_strategies": [
            {
                "strategy_id": "nav_low_battery_template",
                "content": {
                    "principles": ["保持GPS HIGH", "降低屏幕刷新率至60Hz"],
                    "estimated_savings": "25%"
                }
            },
            {
                "strategy_id": "video_watching_template",
                "content": {
                    "principles": ["屏幕亮度设置为50%", "保持刷新率60Hz"],
                    "estimated_savings": "15%"
                }
            }
        ]
    }
    
    # 5. PDL Constraints (硬编码规则)
    mock_constraints = {
        "navigation_app": {
            "min_gps_mode": "BALANCED", # 导航时GPS最低只能是平衡模式
            "screen_timeout": "NEVER"   # 导航时不能息屏
        },
        "video_app": {
            "max_screen_brightness": 1024 # 看视频时屏幕亮度不能超过3000
        }
    }

    # ==========================
    # 执行 Agent
    # ==========================
    final_policy = strategy_planner_agent(
        mock_context, 
        mock_activity, 
        mock_memory, 
        mock_strategies, 
        mock_constraints
    )

    print("\n--- Strategy Planner Output ---")
    print(json.dumps(final_policy, ensure_ascii=False, indent=2))


typeical_result = """
--- Strategy Planner Output ---
{
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
"""