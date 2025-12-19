import re
import requests
import json
import time

# ==== 配置 =====
api_key = "sk-wwolcqsmeztifuouqxehvchcoobuwwokzqjmyckenzhknbab"
url = "https://api.siliconflow.cn/v1/chat/completions"

# FIXME: 低智能模型无法胜任复杂的数字验证任务
model_name = "deepseek-ai/DeepSeek-V3.2"
system_prompt_version1 = """
You are a Constraint Validator Agent for PowerLens.

TASK:
Verify that each action in the policy:
1. Does not violate any CRITICAL or PREFERRED constraints
2. Uses legal parameter values (within device capabilities)
3. Has acceptable risk level

OUTPUT FORMAT (JSON):
{
    "validation_result": "<APPROVED|REJECTED|APPROVED_WITH_WARNING>",
    "violations": [
        {
            "action_index": <int>,
            "violation_type": "<CONSTRAINT_VIOLATION|ILLEGAL_VALUE|USER_INTENT_VIOLATION|SAFETY_VIOLATION>",
            "constraint": "<text>",
            "severity": "<CRITICAL|HIGH|MEDIUM|LOW>",
            "message": "<explanation>"
        }
    ],
    "warnings": [
        {
            "action_index": <int>,
            "warning_type": "<type>",
            "message": "<text>",
            "mitigation": "<text>"
        }
    ],
    "approved_actions": [<list of indices>],
    "rejected_actions": [<list of indices>]
}

VALIDATION RULES:
1. CRITICAL constraints must NEVER be violated -> REJECT
2. PREFERRED constraints can be violated only if:
   - Battery level < 10% (extreme situation)
   - User historical acceptance > 0.7
   Otherwise -> WARNING
3. All parameter values must be in legal range -> REJECT
4. Actions with LOCK must not be overridden -> REJECT

DECISION LOGIC:
- If any CRITICAL violation -> validation_result = REJECTED
- If only warnings -> validation_result = APPROVED_WITH_WARNING
- If no violations or warnings -> validation_result = APPROVED
"""

# TODO: 验证策略应该是一个精确的过程，考虑不使用 LLM 而是使用传统代码判断？
def constraint_validator_agent(policy, pdl_constraints, device_capabilities, current_battery_level=50):
    """
    Constraint Validator Agent (Verification Engine)
    验证生成的策略是否合法且安全。
    
    TODO: 注意：为了执行验证规则（如 Rule 2: Battery < 10%），我们需要额外传入 current_battery_level。
    """
    
    # --- 1. System Prompt ---
    system_prompt = system_prompt_version1

    # --- 2. 组装 Input Payload ---
    # 我们需要显式地把 Battery Level 放进去，否则 Agent 无法判断 Rule 2
    validation_context = {
        "current_battery_level": 100,
        "is_extreme_battery": current_battery_level < 10
    }

    input_data = {
        "Policy_Proposal": policy,
        "PDL_Constraints": pdl_constraints,
        "Device_Capabilities": device_capabilities,
        "Validation_Context": validation_context
    }
    
    user_content = f"INPUT DATA:\n{json.dumps(input_data, indent=2, ensure_ascii=False)}"

    # --- 3. 发送请求 ---
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
        "temperature": 0.1 # 验证任务必须严谨，零创造性
    }

    try:
        print(f"Validator 正在审计策略 (Model: {model_name})...")
        start_time = time.time()
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()['choices'][0]
            content = result['message']['content']

            clean = re.sub(r'```(?:json)?\n(.*)\n```', r'\1', content, flags=re.S)
            parsed_json = json.loads(clean)
            
            print(f"审计完成，耗时: {time.time() - start_time:.2f}s")
            return parsed_json
        else:
            print(f"Error: {response.status_code}")
            return {"error": "Validation failed", "validation_result": "REJECTED"}

    except Exception as e:
        print(f"验证异常: {e}")
        return {"error": str(e), "validation_result": "REJECTED"}

# --- 测试代码 ---
if __name__ == "__main__":
    # 1. 模拟上一个 Agent 生成的策略 (包含一个故意设计的违规动作)
    mock_policy = {
        "policy_id": "pl_video_watching_001",
        "rationale": "Optimizing power settings for video watching activity while preserving core music streaming functionality. Adjusts screen brightness to comply with PDL constraints and maintains refresh rate for smooth playback.",
        "actions": [
            {
            "target": "screen_brightness",
            "action": "SET",
            "value": 1000,
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

    # 2. PDL 约束
    mock_constraints = {
        "critical": [
            "NEVER disable_gps WHEN activity == NAVIGATION",
            "NEVER set screen_brightness > 4096" # 实际上这通常在 capabilities 里，但也可能在 PDL
        ],
        "preferred": [
            "Avoid reducing refresh_rate below 60Hz"
        ]
    }

    # 3. 设备能力
    mock_caps = {
        "screen_brightness": {"min": 0, "max": 4096},
        "gps_modes": ["HIGH", "BALANCED", "LOW", "OFF"],
        "refresh_rate": {"min": 30, "max": 120}
    }

    # 4. 运行验证
    # 假设当前正在导航 (Context 隐含在 Policy 或 Constraints 检查逻辑中，
    # 但为了测试方便，我们在 Prompt 输入数据中通常会把 Context 也附带进去，
    # 这里我们依靠 Agent 根据约束文本 "WHEN activity == NAVIGATION" 进行语义推理，
    # 实际上最好在 input_data 里明确包含 current_activity)
    
    # *修正*: 为了让测试通过，我们需要在 Constraint 文本里明确上下文，
    # 或者像上面代码一样，把 context 注入。
    # 这里我们直接测试 Agent 对 "NEVER set screen_brightness > 255" 的反应。

    result = constraint_validator_agent(mock_policy, mock_constraints, mock_caps)

    print("\n--- Validation Report ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))

typical_result = """
--- Validation Report ---
{
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
"""