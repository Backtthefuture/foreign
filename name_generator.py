import os
import json
import requests
from typing import Dict, List
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class GLMNameGenerator:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        if not self.api_key:
            raise ValueError("API_KEY environment variable is not set")
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model = "glm-4-flash"
        
    def _create_prompt(self, english_name: str) -> str:
        return f'''你是一位极具创意的中文起名专家，特别擅长为外国人起既有文化内涵又充满梗的中文名字。请发挥你的想象力，为他们创造既有趣又得体的中文名。

核心原则：
1. 名字要有趣但不失礼貌，可以幽默但不能尴尬
2. 可以融入网络流行语、知名梗或当代文化元素
3. 保持音律优美，避免生僻字
4. 名字最好暗含一个有趣的故事或双关含义

名字设计要求：
1. 姓氏：选择音近的中国姓氏，可以考虑谐音梗
2. 名字：1-2个字，可以是：
   - 经典文化梗的现代演绎
   - 网络流行语的巧妙运用
   - 中西文化的妙趣结合
3. 整体要朗朗上口，让人会心一笑

文化解读要求：
1. 解释名字背后的梗或趣味
2. 说明双关语或文字游戏（如果有）
3. 点明文化内涵，但要用轻松幽默的口吻

请严格按照以下JSON格式输出3个不同风格的名字方案：
{{
    "names": [
        {{
            "chinese_name": "中文名（网络流行语风格）",
            "pinyin": "拼音（带声调）",
            "meaning": "字面含义（包含梗点）",
            "cultural_explanation": "名字背后的趣味故事（100字以内）",
            "english_explanation": "A witty explanation of the name's cultural meaning and humor (within 50 words)"
        }},
        {{
            "chinese_name": "中文名（经典文化梗风格）",
            "pinyin": "拼音（带声调）",
            "meaning": "字面含义（包含梗点）",
            "cultural_explanation": "名字背后的趣味故事（100字以内）",
            "english_explanation": "A witty explanation of the name's cultural meaning and humor (within 50 words)"
        }},
        {{
            "chinese_name": "中文名（中西文化结合风格）",
            "pinyin": "拼音（带声调）",
            "meaning": "字面含义（包含梗点）",
            "cultural_explanation": "名字背后的趣味故事（100字以内）",
            "english_explanation": "A witty explanation of the name's cultural meaning and humor (within 50 words)"
        }}
    ]
}}

注意事项：
1. 名字要让中国人一看就觉得有趣，但又不会让当事人难堪
2. 解释要诙谐有趣，让人会心一笑
3. 可以适当玩梗，但要注意分寸
4. 英文解释也要体现出名字的幽默感
5. 三个名字方案要风格迥异：
   - 方案1：运用当下流行的网络用语或梗
   - 方案2：基于中国传统文化的趣味改编
   - 方案3：中西文化碰撞产生的有趣联想

请根据输入的英文名：{english_name}，按照以上要求生成3个风格不同的中文名字方案。请确保返回的是合法的JSON格式。'''

    def _make_api_request(self, messages: List[Dict], max_retries: int = 3) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 1500,
            "stream": False
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"API请求失败: {str(e)}")
                time.sleep(1)  # 等待1秒后重试
                continue

    def _parse_response(self, content: str) -> Dict:
        """解析API响应内容，确保返回正确的JSON格式"""
        try:
            # 尝试直接解析JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            try:
                # 查找第一个{和最后一个}之间的内容
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    return json.loads(json_str)
                raise Exception("无法在响应中找到有效的JSON")
            except Exception as e:
                raise Exception(f"解析响应失败: {str(e)}")

    def _validate_response(self, result: Dict) -> Dict:
        """验证响应数据的格式是否正确"""
        if 'names' not in result:
            raise Exception("响应格式错误：缺少'names'字段")
        
        required_fields = ['chinese_name', 'pinyin', 'meaning', 
                         'cultural_explanation', 'english_explanation']
        
        for name_data in result['names']:
            missing_fields = [field for field in required_fields if field not in name_data]
            if missing_fields:
                raise Exception(f"响应格式错误：缺少字段 {', '.join(missing_fields)}")
        
        return result

    def generate_names(self, english_name: str) -> Dict:
        """生成中文名字建议"""
        if not english_name or not english_name.strip():
            raise ValueError("英文名不能为空")

        prompt = self._create_prompt(english_name)
        messages = [
            {"role": "system", "content": "你是一个专业的中文起名专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._make_api_request(messages)
            content = response['choices'][0]['message']['content']
            result = self._parse_response(content)
            validated_result = self._validate_response(result)
            return validated_result
        except Exception as e:
            print(f"生成名字时出错: {str(e)}")
            # 返回一个默认响应而不是抛出异常
            return {
                "names": [
                    {
                        "chinese_name": "李友好",
                        "pinyin": "lǐ yǒu hǎo",
                        "meaning": "友善和美好的人",
                        "cultural_explanation": "李是常见姓氏，友好表示友善美好之意",
                        "english_explanation": "A name representing friendliness and kindness"
                    }
                ]
            }

    def format_response(self, api_result: Dict) -> List[Dict]:
        """格式化API返回的结果为前端所需的格式"""
        formatted_names = []
        for name_data in api_result.get('names', []):
            formatted_names.append({
                'chinese_name': name_data['chinese_name'],
                'pinyin': name_data['pinyin'],
                'meaning': name_data['meaning'],
                'cultural_explanation': name_data['cultural_explanation'],
                'english_explanation': name_data['english_explanation']
            })
        return formatted_names
