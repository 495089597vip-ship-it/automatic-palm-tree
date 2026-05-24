import os
from typing import Tuple, Optional
import openai
from dotenv import load_dotenv

load_dotenv()

class AIAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def is_available(self) -> bool:
        """Check if OpenAI API is configured"""
        return bool(self.api_key)
    
    def analyze_content(self, title: str, author: str, content: str, notes: str) -> Tuple[bool, str]:
        """Analyze Douyin content using OpenAI API"""
        if not self.is_available():
            return False, "未配置 OpenAI API Key"
        
        try:
            # Prepare the analysis prompt
            prompt = f"""
请分析以下抖音内容，并提供专业的内容分析报告。

标题: {title}
作者: {author}
内容描述: {content}
备注: {notes}

请从以下方面进行分析：
1. 内容类型和特点
2. 目标受众
3. 互动潜力
4. 优化建议
5. 关键词提取

请用中文提供简洁有用的分析。
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的短视频内容分析师，特别是对抖音内容有深入了解。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis = response.choices[0].message.content
            return True, analysis
        except openai.error.AuthenticationError:
            return False, "OpenAI API Key 无效或已过期"
        except openai.error.RateLimitError:
            return False, "请求过于频繁，请稍后重试"
        except openai.error.APIError as e:
            return False, f"API 错误: {str(e)}"
        except Exception as e:
            return False, f"分析失败: {str(e)}"
    
    def analyze_batch(self, items: list) -> Tuple[bool, str]:
        """Analyze multiple items"""
        if not self.is_available():
            return False, "未配置 OpenAI API Key"
        
        results = []
        for item in items:
            success, analysis = self.analyze_content(
                item.get('title', ''),
                item.get('author', ''),
                item.get('content', ''),
                item.get('notes', '')
            )
            if success:
                results.append(analysis)
            else:
                results.append(f"分析失败: {analysis}")
        
        return True, "\n\n---\n\n".join(results)
