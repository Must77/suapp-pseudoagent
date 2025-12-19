import json

# ==========================================
# [MOCK DATA] 策略知识库
# 在产品阶段，这将是被索引在 FAISS 中的海量数据
# ==========================================
MOCK_STRATEGY_KB = [
    {
        "strategy_id": "nav_low_battery_template",
        "keywords": ["navigation", "low_battery", "outdoor", "high_critical"], # 用于模拟检索的隐藏字段
        "content": {
            "scenario": "导航低电量场景（电量30-40%）",
            "principles": [
                "保持GPS HIGH模式（核心功能）",
                "保持用户手动设置的屏幕亮度（用户意图）",
                "降低屏幕刷新率至60Hz（节省15-20%屏幕功耗）",
                "暂停后台应用同步（节省网络和CPU功耗）"
            ],
            "estimated_savings": "25-35%",
            "success_rate": 0.95,
            "user_acceptance": 0.88
        }
    },
    {
        "strategy_id": "video_conference_indoor_template",
        "keywords": ["video_conference", "indoor", "wifi"],
        "content": {
            "scenario": "室内视频会议场景",
            "principles": [
                "启用Wi-Fi低延迟模式",
                "自动调节屏幕亮度至室内标准",
                "限制后台下载带宽"
            ],
            "estimated_savings": "10-15%",
            "success_rate": 0.90,
            "user_acceptance": 0.92
        }
    },
    {
        "strategy_id": "reading_oled_saving_template",
        "keywords": ["reading", "oled", "dark_mode"],
        "content": {
            "scenario": "OLED屏幕阅读省电模式",
            "principles": [
                "强制开启纯黑背景（Dark Mode）",
                "降低非活跃区域刷新率"
            ],
            "estimated_savings": "40%",
            "success_rate": 0.85,
            "user_acceptance": 0.80
        }
    }
]

# ==========================================
# [AGENT Logic]
# ==========================================

# TODO: 确认复杂性
def knowledge_retrieval_agent(activity, battery_level, context_tags, top_k=3):
    """
    Knowledge Retrieval Agent (Manager-RAG)
    无需调用 Ollama，模拟向量检索过程。
    """
    
    # 1. 构建 Query (模拟将上下文转化为检索向量的过程)
    # 在真实 RAG 中，这个 query_str 会被送入 Sentence-BERT
    query_str = f"{activity} battery:{battery_level} {context_tags.get('environment', '')} {context_tags.get('critical_level', '')}"
    print(f"[RAG Internal] Generated Query: {query_str}")

    # 2. 检索逻辑 (MOCK: 基于简单的规则打分模拟 Cosine Similarity)
    # 在产品阶段，这里替换为: D, I = index.search(query_vector, top_k)
    scored_results = []
    
    for item in MOCK_STRATEGY_KB:
        score = 0.0
        keywords = item["keywords"]
        
        # --- 简单的模拟打分逻辑 ---
        # 命中 Activity 加分最多
        if activity.lower() in [k.lower() for k in keywords]:
            score += 0.5
        
        # 命中 Environment 加分
        if context_tags.get("environment") and any(context_tags["environment"] in k for k in keywords):
            score += 0.2
            
        # 命中 Battery 范围 (简单逻辑)
        if "low_battery" in keywords and battery_level < 40:
            score += 0.2
        elif "high_battery" in keywords and battery_level > 80:
            score += 0.1
            
        # 添加一点随机抖动模拟真实向量的非完美匹配 (0.01 - 0.05)
        # score += random.uniform(0.01, 0.05) 
        
        # 只有分数 > 0 才视为相关
        if score > 0:
            # 归一化到 0.0 - 1.0 之间 (简单截断)
            final_similarity = min(score + 0.1, 0.99) 
            
            scored_results.append({
                "strategy_id": item["strategy_id"],
                "similarity": round(final_similarity, 2), # 保留两位小数
                "content": item["content"]
            })

    # 3. 排序并取 Top-K
    scored_results.sort(key=lambda x: x["similarity"], reverse=True)
    retrieved = scored_results[:top_k]

    # 4. 构建输出接口
    output = {
        "retrieved_strategies": retrieved
    }
    
    return output

# --- 测试代码 ---
if __name__ == "__main__":
    # 输入接口数据
    input_data = {
        "activity": "NAVIGATION",
        "battery_level": 35,
        "context_tags": {
            "critical_level": "HIGH",
            "environment": "outdoor_bright"
        },
        "top_k": 3
    }

    print("Agent Input:", json.dumps(input_data, indent=2, ensure_ascii=False))
    
    result = knowledge_retrieval_agent(
        activity=input_data["activity"],
        battery_level=input_data["battery_level"],
        context_tags=input_data["context_tags"],
        top_k=input_data["top_k"]
    )

    print("\n--- Knowledge Retrieval Agent Output ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# 产品阶段伪代码 (Production Placeholder)
# import faiss
# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer('all-MiniLM-L6-v2') # 轻量级模型
# index = faiss.read_index("strategies.index") # 加载预先构建好的索引

# def real_search(query_str):
#     query_vector = model.encode([query_str])
#     D, I = index.search(query_vector, k=3)
#     # D is distances (similarity), I is IDs
#     # ... 根据 ID 从数据库查 content ...