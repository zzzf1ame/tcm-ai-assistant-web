import requests
import json
from datetime import datetime
import config

class TCMAIChat:
    def __init__(self):
        self.provider = config.API_PROVIDER
        
    def build_system_prompt(self, user_profile, relevant_knowledge):
        """构建系统提示词"""
        profile_text = ""
        if user_profile:
            profile_text = f"""
用户档案：
- 年龄：{user_profile.get('age', '未知')}岁
- 性别：{user_profile.get('gender', '未知')}
- 体质：{user_profile.get('constitution', '未测评')}
- 地区：{user_profile.get('location', '未知')}
"""
        
        knowledge_text = relevant_knowledge if relevant_knowledge else ""
        
        system_prompt = f"""你是一位专业的中医养生顾问，具有丰富的中医理论知识和临床经验。

{profile_text}

{knowledge_text}

你的职责：
1. **必须根据用户的体质类型给出针对性建议**（这是最重要的！）
2. 基于中医理论（阴阳五行、脏腑经络、气血津液等）给出专业建议
3. 推荐具体可执行的食疗方、穴位按摩、生活调理建议
4. 解释中医术语，让普通人也能理解

重要原则：
1. **不同体质的调理方法完全不同，必须体现差异**
   - 气虚：补气（黄芪、党参、山药）
   - 阳虚：温阳（羊肉、韭菜、生姜）
   - 阴虚：滋阴（银耳、百合、梨）
   - 痰湿：祛湿（薏米、冬瓜、山楂）
   - 湿热：清热（绿豆、苦瓜、黄瓜）
   - 血瘀：活血（山楂、黑木耳、红花）
   - 气郁：疏肝（玫瑰花、佛手、橙子）
2. 不要诊断疾病，不要开处方药
3. 遇到严重症状，建议及时就医
4. 给出的建议要具体、可操作
5. 语言要通俗易懂

回答格式：
- 第一句必须明确提到用户的体质特点
- 解释为什么会出现这个症状（从体质角度）
- 给出2-3个针对该体质的具体方案
- 强调该体质的注意事项
"""
        return system_prompt
        
    def chat_qwen(self, messages, system_prompt):
        """调用通义千问API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.QWEN_API_KEY}"
            }
            
            # 通义千问的消息格式
            qwen_messages = [{"role": "system", "content": system_prompt}]
            qwen_messages.extend(messages)
            
            data = {
                "model": config.MODEL,
                "input": {
                    "messages": qwen_messages
                },
                "parameters": {
                    "max_tokens": config.MAX_TOKENS,
                    "temperature": config.TEMPERATURE,
                    "top_p": 0.8
                }
            }
            
            response = requests.post(
                config.QWEN_API_URL,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 尝试多种可能的响应格式
                if result.get("output"):
                    if result["output"].get("text"):
                        return True, result["output"]["text"]
                    elif result["output"].get("choices"):
                        return True, result["output"]["choices"][0]["message"]["content"]
                elif result.get("choices"):
                    return True, result["choices"][0]["message"]["content"]
                else:
                    return False, f"无法解析响应格式"
            else:
                return False, f"通义千问API错误: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "通义千问响应超时"
        except requests.exceptions.ConnectionError:
            return False, "无法连接到通义千问"
        except Exception as e:
            return False, f"通义千问请求失败: {str(e)}"
            
    def chat_deepseek(self, messages, system_prompt):
        """调用DeepSeek API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}"
            }
            
            # DeepSeek使用OpenAI格式
            deepseek_messages = [{"role": "system", "content": system_prompt}]
            deepseek_messages.extend(messages)
            
            data = {
                "model": "deepseek-chat",
                "messages": deepseek_messages,
                "max_tokens": config.MAX_TOKENS,
                "temperature": config.TEMPERATURE
            }
            
            response = requests.post(
                config.DEEPSEEK_API_URL,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return True, result["choices"][0]["message"]["content"]
            else:
                return False, f"DeepSeek API错误: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "DeepSeek响应超时"
        except requests.exceptions.ConnectionError:
            return False, "无法连接到DeepSeek"
        except Exception as e:
            return False, f"DeepSeek请求失败: {str(e)}"
        
    def chat(self, user_message, user_profile=None, relevant_knowledge="", conversation_history=None):
        """发送对话请求（支持自动切换）"""
        try:
            system_prompt = self.build_system_prompt(user_profile, relevant_knowledge)
            
            messages = []
            
            # 添加历史对话
            if conversation_history:
                for conv in conversation_history[-5:]:
                    messages.append({
                        "role": "user",
                        "content": conv['user_message']
                    })
                    messages.append({
                        "role": "assistant",
                        "content": conv['ai_response']
                    })
            
            # 添加当前消息
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 根据配置选择API
            if self.provider == "qwen":
                success, response = self.chat_qwen(messages, system_prompt)
                
                # 如果千问失败且开启自动切换，切换到DeepSeek
                if not success and config.AUTO_SWITCH_ON_TIMEOUT and ("超时" in response or "连接" in response):
                    print(f"[自动切换] 通义千问失败: {response}，切换到DeepSeek")
                    success, response = self.chat_deepseek(messages, system_prompt)
                    if success:
                        response = f"{response}\n\n_（本次使用DeepSeek备用服务）_"
                
                return success, response
                
            elif self.provider == "deepseek":
                success, response = self.chat_deepseek(messages, system_prompt)
                
                # 如果DeepSeek失败且开启自动切换，切换到千问
                if not success and config.AUTO_SWITCH_ON_TIMEOUT and ("超时" in response or "连接" in response):
                    print(f"[自动切换] DeepSeek失败: {response}，切换到通义千问")
                    success, response = self.chat_qwen(messages, system_prompt)
                    if success:
                        response = f"{response}\n\n_（本次使用通义千问备用服务）_"
                
                return success, response
            else:
                return False, f"不支持的API提供商: {self.provider}"
                
        except Exception as e:
            return False, f"发生错误: {str(e)}"
