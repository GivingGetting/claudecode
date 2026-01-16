"""
SEO Optimizer - SEO优化模块
优化Etsy产品标题、描述、标签和关键词
"""

import json
from typing import Optional

from .utils.llm_client import LLMClient
from .prompts.templates import PromptTemplates


class SEOOptimizer:
    """SEO优化器 - 优化Etsy产品列表的搜索可见性"""

    # Etsy SEO限制
    MAX_TITLE_LENGTH = 140
    MAX_TAG_LENGTH = 20
    MAX_TAGS = 13
    DESCRIPTION_PREVIEW_LENGTH = 160

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        初始化SEO优化器

        Args:
            llm_client: LLM客户端实例
        """
        self.llm = llm_client or LLMClient()

    def optimize_listing(
        self,
        product_name: str,
        product_type: str,
        product_description: str,
        target_market: str = "美国",
    ) -> dict:
        """
        全面优化产品列表

        Args:
            product_name: 产品名称
            product_type: 产品类型
            product_description: 产品描述
            target_market: 目标市场

        Returns:
            优化后的SEO内容
        """
        prompt = PromptTemplates.SEO_OPTIMIZATION.format(
            product_name=product_name,
            product_type=product_type,
            product_description=product_description,
            target_market=target_market,
        )

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        # 验证并调整结果
        result = self._validate_and_fix(result)

        return result

    def _validate_and_fix(self, seo_data: dict) -> dict:
        """验证并修复SEO数据以符合Etsy限制"""
        # 验证标题长度
        if "optimized_title" in seo_data:
            title = seo_data["optimized_title"]
            if len(title) > self.MAX_TITLE_LENGTH:
                seo_data["optimized_title"] = title[: self.MAX_TITLE_LENGTH - 3] + "..."
                seo_data["title_warning"] = f"标题已截断至{self.MAX_TITLE_LENGTH}字符"

        # 验证标签
        if "tags" in seo_data:
            tags = seo_data["tags"]
            # 限制标签数量
            if len(tags) > self.MAX_TAGS:
                tags = tags[: self.MAX_TAGS]
            # 限制每个标签长度
            tags = [tag[:self.MAX_TAG_LENGTH] for tag in tags]
            seo_data["tags"] = tags

        return seo_data

    def generate_tags(
        self, product_name: str, product_type: str, additional_keywords: list = None
    ) -> list[str]:
        """
        生成优化的Etsy标签

        Args:
            product_name: 产品名称
            product_type: 产品类型
            additional_keywords: 额外关键词

        Returns:
            优化后的标签列表（最多13个）
        """
        additional = ", ".join(additional_keywords) if additional_keywords else "无"

        prompt = f"""请为以下Etsy数字产品生成13个优化的标签：

【产品名称】{product_name}
【产品类型】{product_type}
【额外关键词】{additional}

标签要求：
1. 每个标签最多20个字符
2. 总共13个标签
3. 混合使用：主要关键词、长尾关键词、同义词、相关搜索词
4. 英文标签（因为Etsy主要市场是英语国家）

请返回JSON格式：
{{
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13"],
    "tag_strategy": "标签策略说明",
    "primary_keywords_used": ["主要关键词"],
    "long_tail_keywords_used": ["长尾关键词"]
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        tags = result.get("tags", [])
        # 确保符合限制
        tags = [tag[:self.MAX_TAG_LENGTH] for tag in tags[:self.MAX_TAGS]]

        return tags

    def optimize_title(
        self, current_title: str, product_type: str, target_keywords: list = None
    ) -> dict:
        """
        优化产品标题

        Args:
            current_title: 当前标题
            product_type: 产品类型
            target_keywords: 目标关键词

        Returns:
            优化后的标题和建议
        """
        keywords = ", ".join(target_keywords) if target_keywords else "自动选择"

        prompt = f"""请优化以下Etsy产品标题：

【当前标题】{current_title}
【产品类型】{product_type}
【目标关键词】{keywords}

Etsy标题优化原则：
1. 最多140个字符
2. 最重要的关键词放在前面
3. 使用买家会搜索的词汇
4. 清楚描述产品是什么
5. 可以包含多个相关关键词

请返回JSON格式：
{{
    "optimized_title": "优化后的标题",
    "character_count": 字符数,
    "improvements_made": ["改进1", "改进2"],
    "keywords_included": ["包含的关键词"],
    "alternative_titles": ["备选标题1", "备选标题2"],
    "title_score": "标题评分（1-10）",
    "tips": ["进一步优化建议"]
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        # 验证标题长度
        if "optimized_title" in result:
            title = result["optimized_title"]
            if len(title) > self.MAX_TITLE_LENGTH:
                result["optimized_title"] = title[: self.MAX_TITLE_LENGTH - 3] + "..."
                result["warning"] = "标题已自动截断"
            result["character_count"] = len(result["optimized_title"])

        return result

    def keyword_research(self, seed_keyword: str, depth: str = "medium") -> dict:
        """
        关键词研究

        Args:
            seed_keyword: 种子关键词
            depth: 研究深度（light/medium/deep）

        Returns:
            关键词研究结果
        """
        depth_instructions = {
            "light": "提供5-10个相关关键词",
            "medium": "提供15-20个相关关键词，包含分析",
            "deep": "提供30+个关键词，详细分析每个关键词的价值",
        }

        prompt = f"""请对以下Etsy数字产品关键词进行研究：

【种子关键词】{seed_keyword}
【研究深度】{depth_instructions.get(depth, depth_instructions['medium'])}

请返回JSON格式的关键词研究报告：
{{
    "seed_keyword": "{seed_keyword}",
    "search_intent": "搜索意图分析",
    "primary_keywords": [
        {{
            "keyword": "关键词",
            "relevance": "相关度（高/中/低）",
            "competition": "竞争程度",
            "recommended_use": "建议用法（标题/标签/描述）"
        }}
    ],
    "long_tail_keywords": [
        {{
            "keyword": "长尾关键词",
            "specificity": "具体程度",
            "buyer_intent": "购买意图强度"
        }}
    ],
    "related_searches": ["相关搜索1", "相关搜索2"],
    "trending_variations": ["趋势变体1", "趋势变体2"],
    "avoid_keywords": ["应避免的关键词"],
    "keyword_clusters": [
        {{
            "cluster_name": "关键词群名称",
            "keywords": ["关键词1", "关键词2"],
            "best_for": "最适合的产品类型"
        }}
    ],
    "recommendations": {{
        "best_title_keywords": ["最佳标题关键词"],
        "best_tag_keywords": ["最佳标签关键词"],
        "content_keywords": ["内容关键词"]
    }}
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def analyze_listing_seo(self, listing_data: dict) -> dict:
        """
        分析现有列表的SEO状况

        Args:
            listing_data: 列表数据（包含title, description, tags等）

        Returns:
            SEO分析报告和改进建议
        """
        prompt = f"""请分析以下Etsy产品列表的SEO状况：

【列表数据】
{json.dumps(listing_data, ensure_ascii=False, indent=2)}

请返回JSON格式的SEO分析报告：
{{
    "overall_score": "总体评分（1-100）",
    "title_analysis": {{
        "score": "标题评分",
        "length": "标题长度",
        "keyword_usage": "关键词使用评价",
        "issues": ["问题1", "问题2"],
        "improvements": ["改进建议1", "改进建议2"]
    }},
    "tags_analysis": {{
        "score": "标签评分",
        "count": "标签数量",
        "quality": "标签质量评价",
        "missing_opportunities": ["遗漏的关键词机会"],
        "redundant_tags": ["冗余标签"],
        "suggested_replacements": {{"旧标签": "新标签建议"}}
    }},
    "description_analysis": {{
        "score": "描述评分",
        "first_160_chars": "前160字符评价",
        "keyword_density": "关键词密度",
        "readability": "可读性评价",
        "call_to_action": "行动号召评价",
        "improvements": ["改进建议"]
    }},
    "competitive_analysis": {{
        "strengths": ["竞争优势"],
        "weaknesses": ["竞争劣势"],
        "opportunities": ["机会"]
    }},
    "priority_actions": [
        {{
            "action": "优先行动",
            "impact": "预期影响",
            "effort": "所需努力"
        }}
    ]
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def generate_multilingual_keywords(
        self, product_name: str, languages: list = None
    ) -> dict:
        """
        生成多语言关键词

        Args:
            product_name: 产品名称
            languages: 目标语言列表

        Returns:
            多语言关键词
        """
        if languages is None:
            languages = ["English", "German", "French", "Spanish"]

        prompt = f"""请为以下产品生成多语言SEO关键词：

【产品名称】{product_name}
【目标语言】{', '.join(languages)}

请返回JSON格式：
{{
    "product": "{product_name}",
    "multilingual_keywords": {{
        "English": {{
            "title_keywords": ["关键词1", "关键词2"],
            "tags": ["标签1", "标签2"]
        }},
        "German": {{
            "title_keywords": ["关键词1", "关键词2"],
            "tags": ["标签1", "标签2"]
        }}
    }},
    "market_notes": {{
        "language": "该市场的特别注意事项"
    }}
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result
