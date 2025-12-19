import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class KnowledgeRetrievalSystem:
    def __init__(self):
        # 1. 加载 Embedding 模型 (这是核心，它负责理解语义)
        # 'all-MiniLM-L6-v2' 是一个轻量级模型，把句子变成 384 维的向量
        print("正在加载 Embedding 模型...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. 准备策略数据库 (Source Data)
        self.strategies = self._load_strategy_database()
        
        # 3. 构建向量索引 (Index Construction)
        self._build_index()

    def _load_strategy_database(self):
        """实际项目中这里会从 SQL 数据库或文件中读取"""
        return [
            {
                "strategy_id": "nav_low_battery_template",
                "search_text": "navigation map gps walking outdoor low battery critical save power", # 专门用于被检索的文本
                "content": {
                    "scenario": "导航低电量场景",
                    "principles": ["GPS HIGH", "Screen 60Hz"],
                    "estimated_savings": "25-35%",
                    "success_rate": 0.95,
                    "user_acceptance": 0.88
                }
            },
            {
                "strategy_id": "video_conf_template",
                "search_text": "video call zoom meeting teams indoor wifi high data usage",
                "content": {
                    "scenario": "视频会议场景",
                    "principles": ["WiFi Low Latency", "Brightness Auto"],
                    "estimated_savings": "15%",
                    "success_rate": 0.90,
                    "user_acceptance": 0.92
                }
            }
        ]

    def _build_index(self):
        """将所有策略的文本转化为向量，并存入 FAISS 索引"""
        print("正在构建向量索引...")
        # 提取所有策略的 "search_text"
        corpus = [s["search_text"] for s in self.strategies]
        
        # 编码：Text -> Vectors (numpy array)
        self.embeddings = self.model.encode(corpus)
        
        # 创建 FAISS 索引 (L2 距离或 Inner Product)
        dimension = self.embeddings.shape[1] # 通常是 384
        self.index = faiss.IndexFlatIP(dimension) # Inner Product 用于计算相似度
        self.index.add(self.embeddings)
        print(f"索引构建完成，共包含 {self.index.ntotal} 条策略。")

    def retrieve(self, query_text, top_k=3):
        """
        检索函数
        输入: 自然语言查询 (e.g. "Auto navigation with low power")
        输出: JSON 格式的检索结果
        """
        # 1. 将用户的查询也转化为向量
        query_vector = self.model.encode([query_text])
        
        # 2. 在索引中搜索最近的向量
        # D 是 Distance (相似度分数), I 是 Index (在 self.strategies 列表中的下标)
        D, I = self.index.search(query_vector, top_k)
        
        # 3. 组装结果
        retrieved_items = []
        for i in range(top_k):
            idx = I[0][i] # 获取检索到的策略在列表中的下标
            score = D[0][i] # 获取相似度分数
            
            if idx == -1: continue # 没找到
            
            strategy = self.strategies[idx]
            
            retrieved_items.append({
                "strategy_id": strategy["strategy_id"],
                "similarity": float(score), # 相似度
                "content": strategy["content"]
            })
            
        return {"retrieved_strategies": retrieved_items}

# --- 对应你的 Agent 接口封装 ---
def knowledge_retrieval_agent(system_instance, activity, battery_level, context_tags, top_k=3):
    # 1. 动态构造查询语句 (Prompt Engineering for Search)
    # 我们把结构化的参数，拼成一句自然语言，方便模型理解语义
    query_str = f"User is doing {activity} with battery {battery_level}%. Context: {context_tags}"
    
    # 2. 调用系统进行检索
    return system_instance.retrieve(query_str, top_k)

# --- 运行测试 ---
if __name__ == "__main__":
    # 初始化系统 (耗时操作，只需做一次)
    rag_system = KnowledgeRetrievalSystem()
    
    # 模拟输入
    agent_input = {
        "activity": "NAVIGATION",
        "battery_level": 35,
        "context_tags": {"critical_level": "HIGH", "environment": "outdoor"}
    }
    
    # 运行 Agent
    print("\n--- Searching ---")
    result = knowledge_retrieval_agent(
        rag_system, 
        agent_input["activity"], 
        agent_input["battery_level"], 
        agent_input["context_tags"]
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))