import requests

def ask_sillicon(prompt) -> requests.Response:
    api_key = "sk-wwolcqsmeztifuouqxehvchcoobuwwokzqjmyckenzhknbab"
    url = "https://api.siliconflow.cn/v1/chat/completions"

    # 提示词
    system_prompt = "You are a helpful assistant."
    user_prompt = prompt

    # 网络
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",   
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.5,
        "response_format": { "type": "text" },
    }

    return requests.post(url, headers=headers, json=payload, timeout=30)

system_prompt_version1 = """
你是一个代码大师.

TASK:
完成用户的代码请求, 生成符合要求的代码片段和说明.

OUTPUT FORMAT(JSON):
{
    "code": "生成的代码片段",
    "description": "代码片段的说明",
    "language": "<Python|C++|C|GO|scheme>",
    "difficulty": "<0.0-1.0>",
}


"""
def ask_sillicon_json(prompt) -> requests.Response:
    api_key = "sk-wwolcqsmeztifuouqxehvchcoobuwwokzqjmyckenzhknbab"
    url = "https://api.siliconflow.cn/v1/chat/completions"

    # 提示词
    system_prompt = system_prompt_version1
    user_prompt = prompt

    # 网络
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",   
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.1,
        "response_format": { "type": "json_object" },
    }

    return requests.post(url, headers=headers, json=payload, timeout=30)
    pass

if __name__ == "__main__":
    response = ask_sillicon_json("写一个python的helloworld代码")
    print("=======origin=========")
    print(response)
    print("=======json=========")
    print(response.json())
    print("=======json with []=========")
    print(response.json()['choices'][0]['message']['content'])
    print("=======text=========")
    print(response.text)
    print("=======status code=========")
    print(response.status_code)
    print("=======header=========")
    print(response.headers)

