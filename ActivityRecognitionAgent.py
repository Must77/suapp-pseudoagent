import re
import requests
import json
import time

from myutils import OLLAMA_URL, MODEL_NAME, TIMEOUT

# ==== 配置 ====
api_key = "sk-wwolcqsmeztifuouqxehvchcoobuwwokzqjmyckenzhknbab"
url = "https://api.siliconflow.cn/v1/chat/completions"

model_name = "deepseek-ai/DeepSeek-V3.2"
system_prompt_version1 = """
You are an Activity Recognition Agent for a mobile power management system.

TASK:
Identify the user's current activity and intent.

OUTPUT FORMAT (JSON):
{
"activity": "<ACTIVITY_TYPE>", 
"confidence": <0.0-1.0>,
"sub_activity": "<SUB_ACTIVITY>", 
"context_tags": {
"app": "<app_name>",
"ui_state": "<state>",
"user_intent": "<intent>",
"environment": "<environment>",
"critical_level": "<HIGH|MEDIUM|LOW>"
},
"reasoning": "<brief_explanation>"
}

ACTIVITY TYPES:
- NAVIGATION: User is using a navigation app (maps, GPS)
- VIDEO_CONFERENCE: User is in a video call (Zoom, Teams, WeChat)
- READING: User is reading text content (articles, books, documents)
- GAMING: User is playing games
- VIDEO_WATCHING: User is watching videos
- IDLE: Device is idle or in standby

CRITICAL_LEVEL:
- HIGH: Activity cannot be interrupted
- MEDIUM: Activity is important but can tolerate some degradation
- LOW: Non-critical activity

RULES:
1. Use UI tree to identify the current app and UI state
2. Use sensor data to infer user behavior
3. Use environment data to infer context
4. Assign confidence based on data consistency
5. Keep reasoning brief (max 2 sentences)
"""
# ==== END ====

def activity_recognition_agent(context_data, ui_tree, history):
    """
    Activity Recognition Agent
    输入: context_data (dict), ui_tree (dict/str), history (list)
    输出: 解析后的 JSON (dict)
    """

    # 1. 准备 System Prompt
    system_prompt = system_prompt_version1

    # 2. 准备 User Input (将输入数据打包)
    user_input_payload = {
        "context": context_data,
        "ui_tree": ui_tree,
        "historical_activities": history
    }
    # 将字典转换为格式化的字符串，方便模型理解
    user_content = f"INPUT DATA:\n{json.dumps(user_input_payload, ensure_ascii=False, indent=2)}"

    # 3. 构造请求 Payload
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
        "temperature": 0.1 # 降低随机性，提高分析的确定性
    }

    try:
        # 4. 发送请求
        print(f"Agent 正在分析上下文 (Model: {model_name})...")
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

# --- 测试代码 ---
if __name__ == "__main__":
    # 模拟输入数据 (Mock Data)
    
    # 1. Context Monitor 输出
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

    # 2. UI Tree
    mock_ui_tree = {
        "className": "android.widget.FrameLayout",
        "childCount": 1,
        "children": [
            {
                "viewId": "com.kugou.android:id/cvr",
                "className": "android.view.ViewGroup",
                "childCount": 2,
                "children": [
                    {
                        "className": "android.view.View",
                        "isClickable": True
                    },
                    {
                        "className": "android.view.ViewGroup",
                        "isClickable": True,
                        "childCount": 30,
                        "children": [
                            {
                                "className": "android.view.View",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/de10",
                                "className": "android.view.ViewGroup",
                                "childCount": 1,
                                "children": [
                                    {
                                        "className": "android.widget.FrameLayout",
                                        "isClickable": True,
                                        "childCount": 16,
                                        "children": [
                                            {
                                                "viewId": "com.kugou.android:id/h0m1",
                                                "className": "android.widget.ImageView",
                                                "contentDescription": "播放"
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/uc9",
                                                "className": "android.widget.ImageButton",
                                                "isClickable": True
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/fof1",
                                                "className": "android.widget.FrameLayout",
                                                "contentDescription": "歌词"
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/fo71",
                                                "className": "android.widget.ImageView",
                                                "contentDescription": "收起播放控制",
                                                "isClickable": True
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/f5a0",
                                                "className": "android.widget.HorizontalScrollView",
                                                "childCount": 1,
                                                "children": [
                                                    {
                                                        "viewId": "com.kugou.android:id/gpd0",
                                                        "className": "android.widget.TextView",
                                                        "text": "加州旅馆",
                                                        "isClickable": True
                                                    }
                                                ]
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/d4q1",
                                                "className": "android.widget.LinearLayout",
                                                "contentDescription": "华语群星",
                                                "childCount": 1,
                                                "children": [
                                                    {
                                                        "className": "android.widget.TextView",
                                                        "text": "华语群星",
                                                        "isClickable": True
                                                    }
                                                ]
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/lsk",
                                                "className": "android.widget.FrameLayout",
                                                "childCount": 1,
                                                "children": [
                                                    {
                                                        "viewId": "com.kugou.android:id/d4j1",
                                                        "className": "android.widget.TextView",
                                                        "text": "关注",
                                                        "contentDescription": "关注",
                                                        "isClickable": True
                                                    }
                                                ]
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/lsm",
                                                "className": "android.widget.FrameLayout",
                                                "isClickable": True
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/d4t0",
                                                "className": "android.widget.FrameLayout",
                                                "isClickable": True,
                                                "childCount": 1,
                                                "children": [
                                                    {
                                                        "viewId": "com.kugou.android:id/de91",
                                                        "className": "android.widget.TextView",
                                                        "text": "高品"
                                                    }
                                                ]
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/d4v1",
                                                "className": "android.widget.Button",
                                                "contentDescription": "音效",
                                                "isClickable": True,
                                                "childCount": 1,
                                                "children": [
                                                    {
                                                        "viewId": "com.kugou.android:id/dej1",
                                                        "className": "android.widget.TextView",
                                                        "text": "音效"
                                                    }
                                                ]
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/t8p",
                                                "className": "android.widget.ImageButton",
                                                "contentDescription": "歌词设置",
                                                "isClickable": True
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/t8o",
                                                "className": "android.widget.ImageButton",
                                                "isClickable": True
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/t8t",
                                                "className": "android.widget.FrameLayout",
                                                "isClickable": True,
                                                "childCount": 1,
                                                "children": [
                                                    {
                                                        "viewId": "com.kugou.android:id/t8m",
                                                        "className": "android.widget.ImageButton",
                                                        "contentDescription": "打开伴唱"
                                                    }
                                                ]
                                            },
                                            {
                                                "className": "android.widget.ImageView",
                                                "contentDescription": "收藏",
                                                "isClickable": True
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/d5i0",
                                                "className": "android.widget.RelativeLayout",
                                                "contentDescription": "歌曲评论 38条",
                                                "isClickable": True,
                                                "childCount": 1,
                                                "children": [
                                                    {
                                                        "viewId": "com.kugou.android:id/deu1",
                                                        "className": "android.widget.TextView",
                                                        "text": "38"
                                                    }
                                                ]
                                            },
                                            {
                                                "viewId": "com.kugou.android:id/db20",
                                                "className": "android.widget.FrameLayout",
                                                "contentDescription": "更多",
                                                "isClickable": True
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "className": "android.widget.FrameLayout",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/d511",
                                "className": "android.widget.RelativeLayout",
                                "contentDescription": "返回",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/de60",
                                "className": "android.view.ViewGroup",
                                "isClickable": True,
                                "childCount": 2,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/d_31",
                                        "className": "android.widget.TextView",
                                        "text": "11"
                                    },
                                    {
                                        "viewId": "com.kugou.android:id/d_40",
                                        "className": "android.widget.TextView",
                                        "text": "人在听"
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/ddv1",
                                "className": "android.widget.FrameLayout",
                                "contentDescription": "横屏",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/d5e1",
                                "className": "android.widget.ImageButton",
                                "contentDescription": "分享",
                                "isClickable": True
                            },
                            {
                                "className": "android.view.View",
                                "contentDescription": "当前第2页,共4页"
                            },
                            {
                                "viewId": "com.kugou.android:id/ebc1",
                                "className": "android.widget.RelativeLayout",
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/lpn",
                                        "className": "android.widget.FrameLayout",
                                        "contentDescription": "歌词",
                                        "childCount": 1,
                                        "children": [
                                            {
                                                "className": "android.view.View"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/f5a0",
                                "className": "android.widget.HorizontalScrollView",
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/gpd0",
                                        "className": "android.widget.TextView",
                                        "text": "加州旅馆",
                                        "isClickable": True
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/d4q1",
                                "className": "android.widget.LinearLayout",
                                "contentDescription": "华语群星",
                                "childCount": 1,
                                "children": [
                                    {
                                        "className": "android.widget.TextView",
                                        "text": "华语群星",
                                        "isClickable": True
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/lsk",
                                "className": "android.widget.FrameLayout",
                                "isClickable": True,
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/d4j1",
                                        "className": "android.widget.TextView",
                                        "text": "关注",
                                        "contentDescription": "关注",
                                        "isClickable": True
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/lsm",
                                "className": "android.widget.FrameLayout",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/d4t0",
                                "className": "android.widget.FrameLayout",
                                "isClickable": True,
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/de91",
                                        "className": "android.widget.TextView",
                                        "text": "高品"
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/d4v1",
                                "className": "android.widget.Button",
                                "contentDescription": "音效",
                                "isClickable": True,
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/dej1",
                                        "className": "android.widget.TextView",
                                        "text": "音效"
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/d4x0",
                                "className": "android.widget.Button",
                                "contentDescription": "AI音乐",
                                "isClickable": True,
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/dej1",
                                        "className": "android.widget.TextView",
                                        "text": "伴唱"
                                    }
                                ]
                            },
                            {
                                "className": "android.widget.LinearLayout",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/d5s0",
                                "className": "android.widget.ImageView",
                                "contentDescription": "下载",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/d4o1",
                                "className": "android.widget.FrameLayout",
                                "isClickable": True
                            },
                            {
                                "className": "android.widget.ImageView",
                                "contentDescription": "收藏",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/d5i0",
                                "className": "android.widget.RelativeLayout",
                                "contentDescription": "歌曲评论 38条",
                                "isClickable": True,
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/deu1",
                                        "className": "android.widget.TextView",
                                        "text": "38"
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/db20",
                                "className": "android.widget.FrameLayout",
                                "contentDescription": "更多",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/lr6",
                                "className": "android.widget.FrameLayout",
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/dd71",
                                        "className": "android.widget.SeekBar",
                                        "contentDescription": "播放进度"
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/dbs0",
                                "className": "android.widget.FrameLayout",
                                "contentDescription": "顺序播放",
                                "isClickable": True,
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/dbs1",
                                        "className": "android.widget.ImageButton",
                                        "contentDescription": "播放模式"
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/dbu0",
                                "className": "android.widget.ImageButton",
                                "contentDescription": "上一首",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/dbv0",
                                "className": "android.widget.ImageButton",
                                "contentDescription": "播放",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/dbt1",
                                "className": "android.widget.ImageButton",
                                "contentDescription": "下一首",
                                "isClickable": True
                            },
                            {
                                "viewId": "com.kugou.android:id/d530",
                                "className": "android.widget.RelativeLayout",
                                "isClickable": True,
                                "childCount": 1,
                                "children": [
                                    {
                                        "viewId": "com.kugou.android:id/d531",
                                        "className": "android.widget.Button",
                                        "contentDescription": "播放队列"
                                    }
                                ]
                            },
                            {
                                "viewId": "com.kugou.android:id/d5n1",
                                "className": "android.widget.TextView",
                                "text": "04:18",
                                "contentDescription": "当前播放时长04分18秒"
                            },
                            {
                                "viewId": "com.kugou.android:id/del1",
                                "className": "android.widget.TextView",
                                "text": "05:05",
                                "contentDescription": "歌曲总时长05分05秒"
                            }
                        ]
                    }
                ]
            }
        ]
    }


    # 3. 历史记录
    mock_history = {
        "recentAppsRaw": "  * Recent #0: Task{45fbc6 #269 type=standard A=10331:com.example.suapp}\n  * Recent #1: Task{e5a4d47 #5 type=undefined I=com.android.launcher\\/.Launcher}\n  * Recent #2: Task{81eb588 #267 type=standard A=10342:android.task.kugou}\n"
    }

    # 运行 Agent
    result = activity_recognition_agent(mock_context, mock_ui_tree, mock_history)

    # 打印结果
    if result:
        print("\n--- Agent Output ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))

typical_result = """
--- Agent Output ---
{
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
"""