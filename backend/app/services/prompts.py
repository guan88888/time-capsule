"""
AI提示词模板
"""
from typing import List, Dict, Optional

class PromptTemplates:
    """提示词模板类"""
    
    # 系统提示词
    SYSTEM_PROMPT_GENERAL = "你是一个友善、专业的AI助手，擅长理解和帮助用户。请用简洁、温暖的语言回答。"
    
    SYSTEM_PROMPT_CREATIVE = "你是一个有创意的AI助手，擅长生成有趣、有吸引力的内容。"
    
    SYSTEM_PROMPT_COUNSELING = "你是一个专业的心理健康顾问，能够提供温暖、专业的心理健康建议。"
    
    SYSTEM_PROMPT_ANALYSIS = "你是一个专业的数据分析师，能够分析数据并提供有价值的洞察。"
    
    @staticmethod
    def generate_title(content: str, count: int = 3) -> str:
        """
        生成标题的提示词
        
        Args:
            content: 胶囊内容
            count: 生成标题数量
        """
        return f"""根据以下胶囊内容，生成{count}个简洁有吸引力的标题（每个不超过15字）。

要求：
1. 标题要简洁明了，能概括内容核心
2. 标题要有吸引力，能引起共鸣
3. 每个标题用换行符分隔，不要编号

胶囊内容：
{content}

请直接输出{count}个标题，每个标题一行："""

    @staticmethod
    def recommend_tags(title: str, content: str, count: int = 5) -> str:
        """
        推荐标签的提示词
        
        Args:
            title: 胶囊标题
            content: 胶囊内容
            count: 推荐标签数量
        """
        return f"""分析以下胶囊内容，推荐{count}个标签。

要求：
1. 标签要准确反映内容主题和情感
2. 单个标签2-4个字
3. 标签之间用逗号分隔，不要编号
4. 直接输出标签，格式：标签1,标签2,标签3

标题：{title}
内容：{content}

请直接输出{count}个标签："""

    @staticmethod
    def mental_suggestion(
        emotion_score: int,
        review_text: str,
        original_content: str
    ) -> str:
        """
        心理健康建议的提示词
        
        Args:
            emotion_score: 情绪评分（0-4）
            review_text: 回顾文本
            original_content: 原始胶囊内容
        """
        emotion_map = {
            0: "非常难过",
            1: "有点低落",
            2: "平静",
            3: "还不错",
            4: "非常开心"
        }
        emotion_desc = emotion_map.get(emotion_score, "未知")
        
        return f"""作为专业的心理健康顾问，请根据以下信息生成一段温暖、专业的心理健康建议。

用户情绪评分：{emotion_score}（{emotion_desc}）
回顾内容：{review_text}
原始胶囊内容：{original_content}

要求：
1. 建议要温暖、鼓励，避免说教
2. 结合用户的具体情况（情绪评分、回顾内容、原始内容）
3. 提供实用的改善建议
4. 字数控制在100-150字
5. 使用第二人称"你"来称呼用户

请生成心理健康建议："""

    @staticmethod
    def optimize_content(content: str) -> str:
        """
        内容优化的提示词
        
        Args:
            content: 待优化的内容
        """
        return f"""请优化以下胶囊内容，提供：
1. 语法检查（如有错误请指出）
2. 措辞润色建议（如何让表达更生动）
3. 表达优化（如何让内容更清晰）

原内容：
{content}

请按以下格式输出：
【优化建议】
（具体建议内容）

【优化后的内容】
（优化后的完整内容）"""

    @staticmethod
    def analyze_goal(target: str, progress: int, review_text: str) -> str:
        """
        目标分析的提示词
        
        Args:
            target: 原始目标
            progress: 当前进度（0-100）
            review_text: 回顾文本
        """
        return f"""分析以下目标完成情况，并提供建议。

原始目标：{target}
当前进度：{progress}%
回顾内容：{review_text}

请提供：
1. 完成情况评估（简洁明了）
2. 可能的原因分析（如果有阻碍因素）
3. 下一步行动建议（50-100字，实用具体）

请按以下格式输出：
【完成情况】
（评估内容）

【原因分析】
（如有阻碍因素，分析原因）

【行动建议】
（下一步具体建议）"""

    @staticmethod
    def emotion_trend_analysis(emotion_data: List[Dict]) -> str:
        """
        情绪趋势分析的提示词
        
        Args:
            emotion_data: 情绪数据列表 [{"date": "2024-01-01", "score": 3, "review": "..."}, ...]
        """
        # 构建数据文本
        data_text = "\n".join([
            f"日期：{item['date']}，情绪评分：{item['score']}，回顾：{item.get('review', '无')}"
            for item in emotion_data
        ])
        
        return f"""分析用户近期的情绪数据，生成情绪分析报告。

情绪数据：
{data_text}

请生成报告，包括：
1. 情绪趋势总结（整体变化趋势）
2. 主要情绪影响因素（什么导致了情绪变化）
3. 改善建议（100-200字，提供实用建议）

请按以下格式输出：
【情绪趋势】
（趋势总结）

【影响因素】
（主要影响因素）

【改善建议】
（具体建议）"""

    @staticmethod
    def reflection_questions(original_content: str, review_text: str, count: int = 3) -> str:
        """
        反思引导问题的提示词
        
        Args:
            original_content: 原始胶囊内容
            review_text: 当前回顾文本
            count: 生成问题数量
        """
        return f"""根据以下胶囊内容和回顾，生成{count}个引导性反思问题，帮助用户深度思考。

原始胶囊内容：{original_content}
当前回顾：{review_text}

要求：
1. 问题是开放性的，能引发深度思考
2. 每个问题20-30字
3. 问题要有启发性，帮助用户更好地理解自己
4. 每个问题用换行符分隔，不要编号

请直接输出{count}个问题，每个问题一行："""

    @staticmethod
    def detect_inappropriate_content(text: str) -> str:
        """
        内容检测的提示词
        
        Args:
            text: 待检测的文本
        """
        return f"""检测以下评论内容是否包含不当言论（辱骂、广告、色情、政治敏感等）。

评论内容：
{text}

请按以下JSON格式输出：
{{
    "is_appropriate": true/false,
    "reason": "原因说明（如果是不当内容，说明违规类型）"
}}"""

    @staticmethod
    def suggest_comment_reply(comment: str, capsule_content: str) -> str:
        """
        评论回复建议的提示词
        
        Args:
            comment: 用户评论
            capsule_content: 胶囊内容
        """
        return f"""根据以下评论和胶囊内容，生成2个友好、合适的回复建议。

胶囊内容：{capsule_content}
用户评论：{comment}

要求：
1. 回复要友好、尊重
2. 回复要贴合评论内容
3. 每个回复30-50字
4. 每个回复用换行符分隔，不要编号

请直接输出2个回复建议，每个回复一行："""


# 便捷函数
def get_prompt_template(template_name: str, **kwargs) -> str:
    """
    获取提示词模板的便捷函数
    
    使用示例:
        prompt = get_prompt_template("generate_title", content="我今天很开心")
    """
    templates = PromptTemplates()
    method = getattr(templates, template_name, None)
    if method and callable(method):
        return method(**kwargs)
    else:
        raise ValueError(f"提示词模板 '{template_name}' 不存在")
