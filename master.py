import json
from ActivityRecognitionAgent import activity_recognition_agent
from StrategyPlannerAgent import strategy_planner_agent
from ConstraintVaildatorAgent import constraint_validator_agent
from ActionExecutorAgent import action_executor_agent


def main():
    # Step 1: 识别当前用户活动
    activity = activity_recognition_agent(context, ui_tree, history)
    activity = json.dumps(activity, ensure_ascii=False, indent=2)
    print(f"[master]Recognized Activity: {activity}\n")

    # Step 2: 规划节能策略
    policy = strategy_planner_agent(context, activity, mock_memory, strategies, constraints)
    policy = json.dumps(policy, ensure_ascii=False, indent=2)
    print(f"[master]Planned Strategies: {policy}\n")

    # Step 3: 验证策略约束
    valid_strategies = constraint_validator_agent(policy, constraints, capacity, current_battery_level=100)
    valid_strategies = json.dumps(valid_strategies, ensure_ascii=False, indent=2)
    print(f"[master]Valid Strategies: {valid_strategies}\n")

    # Step 4: 执行动作
    action_seq = action_executor_agent(policy, valid_strategies)
    action_seq_json = json.dumps(action_seq, ensure_ascii=False, indent=2)
    print(f"[master]Generated Action Sequence: {action_seq_json}\n")

    # 输出要执行的命令 for test
    print("[master]Shell Commands to Execute:")
    for cmd in action_seq['executed_commands']:
        print(f"第{cmd['command_index']}个要执行的命令是{cmd['command']}")



# ======== 数据 ========
# 手机能力
capacity = {
    "screen_brightness": {"min": 0, "max": 4096},
    "gps_modes": ["HIGH", "BALANCED", "LOW", "OFF"],
    "refresh_rate": {"min": 30, "max": 120}
}

# 手机状态
context = {
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

# 前台应用UI
ui_tree = {
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

# 最近使用的应用
history = {
    "recentAppsRaw": "  * Recent #0: Task{45fbc6 #269 type=standard A=10331:com.example.suapp}\n  * Recent #1: Task{e5a4d47 #5 type=undefined I=com.android.launcher\\/.Launcher}\n  * Recent #2: Task{81eb588 #267 type=standard A=10342:android.task.kugou}\n"
}

# 刚刚用户的操作
mock_memory = {
    "action": "NONE"
}

# 通用策略
strategies = {
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

# PDL 约束
constraints = {
    "navigation_app": {
        "min_gps_mode": "BALANCED", # 导航时GPS最低只能是平衡模式
        "screen_timeout": "NEVER"   # 导航时不能息屏
    },
    "video_app": {
        "max_screen_brightness": 3000 # 看视频时屏幕亮度不能超过3000
    },
    "music_app": {
        "is_volume_muted": False # 听音乐时候不能静音
    }
    
}

if __name__ == "__main__":
    main()


