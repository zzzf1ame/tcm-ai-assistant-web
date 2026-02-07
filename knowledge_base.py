import json
from pathlib import Path

class KnowledgeBase:
    def __init__(self, knowledge_path):
        self.knowledge_path = knowledge_path
        self.knowledge = self.load_knowledge()
        
    def load_knowledge(self):
        """加载知识库"""
        if Path(self.knowledge_path).exists():
            with open(self.knowledge_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"体质知识": [], "症状知识": [], "方剂知识": [], "穴位知识": [], "食疗知识": []}
        
    def search(self, query, max_results=3):
        """搜索相关知识"""
        query_lower = query.lower()
        results = []
        
        for category, items in self.knowledge.items():
            for item in items:
                keywords = item.get('keywords', [])
                if any(kw in query_lower for kw in keywords):
                    results.append({
                        'category': category,
                        'content': item['content']
                    })
                    
        return results[:max_results]
        
    def format_knowledge(self, results):
        """格式化知识为文本"""
        if not results:
            return ""
            
        formatted = "相关中医知识：\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. [{result['category']}] {result['content']}\n"
            
        return formatted
