"""
Product Generator - 产品创意生成模块
生成数字产品创意、产品描述和产品系列规划
"""

import json
from typing import Optional
from dataclasses import dataclass, field

from .utils.llm_client import LLMClient
from .utils.etsy_scraper import EtsyScraper
from .prompts.templates import PromptTemplates


@dataclass
class ProductIdea:
    """产品创意数据结构"""

    name: str
    description: str
    target_customer: str
    unique_selling_point: str
    estimated_creation_time: str
    recommended_price_range: str
    required_tools: list = field(default_factory=list)
    difficulty: str = "中等"
    market_potential: str = "中"


@dataclass
class ProductBundle:
    """产品捆绑包数据结构"""

    name: str
    included_products: list
    price_advantage: str


class ProductGenerator:
    """产品创意生成器"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        初始化产品生成器

        Args:
            llm_client: LLM客户端实例
        """
        self.llm = llm_client or LLMClient()
        self.scraper = EtsyScraper()

    def generate_ideas(
        self,
        category: str,
        target_audience: str = "通用",
        skill_level: str = "初学者",
        competitor_analysis: bool = True,
        num_ideas: int = 5,
    ) -> dict:
        """
        生成产品创意

        Args:
            category: 产品类别
            target_audience: 目标受众
            skill_level: 创作者技能水平
            competitor_analysis: 是否包含竞品分析
            num_ideas: 生成的创意数量

        Returns:
            产品创意和捆绑包建议
        """
        # 获取竞品信息
        competitor_info = "暂无竞品数据"
        if competitor_analysis:
            try:
                products = self.scraper.search_products(
                    category, max_results=10, digital_only=True
                )
                if products:
                    competitor_info = json.dumps(
                        [
                            {
                                "title": p.title,
                                "price": p.price,
                                "rating": p.rating,
                                "reviews": p.reviews_count,
                            }
                            for p in products
                        ],
                        ensure_ascii=False,
                        indent=2,
                    )
            except Exception:
                pass

        prompt = PromptTemplates.PRODUCT_IDEAS.format(
            category=category,
            target_audience=target_audience,
            competitor_info=competitor_info,
            skill_level=skill_level,
        )

        # 添加数量要求
        prompt = prompt.replace("5-10个", f"{num_ideas}个")

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.8,
        )

        return result

    def generate_product_line(
        self, niche: str, num_products: int = 10, coherent_branding: bool = True
    ) -> dict:
        """
        生成完整的产品线规划

        Args:
            niche: 利基市场
            num_products: 产品数量
            coherent_branding: 是否保持品牌一致性

        Returns:
            产品线规划
        """
        prompt = f"""请为以下利基市场设计一个完整的Etsy数字产品线：

【利基市场】{niche}
【产品数量】{num_products}个产品
【品牌一致性】{'需要保持统一的视觉风格和品牌调性' if coherent_branding else '可以多样化'}

请设计产品线，以JSON格式返回：
{{
    "product_line_name": "产品线名称",
    "brand_positioning": "品牌定位说明",
    "visual_style": {{
        "color_palette": ["颜色1", "颜色2", "颜色3"],
        "typography": "字体风格建议",
        "overall_aesthetic": "整体美学风格"
    }},
    "products": [
        {{
            "order": 1,
            "name": "产品名称",
            "type": "产品类型",
            "description": "产品描述",
            "price_point": "定价区间",
            "priority": "发布优先级（高/中/低）",
            "creation_complexity": "制作复杂度",
            "cross_sell_with": ["可搭配销售的产品"]
        }}
    ],
    "launch_strategy": {{
        "phase_1": {{
            "products": ["首批发布的产品"],
            "focus": "第一阶段重点"
        }},
        "phase_2": {{
            "products": ["第二批产品"],
            "focus": "第二阶段重点"
        }},
        "phase_3": {{
            "products": ["第三批产品"],
            "focus": "第三阶段重点"
        }}
    }},
    "bundle_opportunities": [
        {{
            "bundle_name": "捆绑包名称",
            "products": ["包含产品"],
            "discount_suggestion": "折扣建议"
        }}
    ],
    "upsell_path": "客户升级路径说明"
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.8,
        )

        return result

    def generate_description(
        self,
        product_name: str,
        product_type: str,
        contents: str,
        target_audience: str = "通用",
        usage: str = "数字下载后使用",
    ) -> dict:
        """
        生成产品描述

        Args:
            product_name: 产品名称
            product_type: 产品类型
            contents: 包含内容
            target_audience: 目标受众
            usage: 使用方式

        Returns:
            完整的产品描述
        """
        prompt = PromptTemplates.PRODUCT_DESCRIPTION.format(
            product_name=product_name,
            product_type=product_type,
            contents=contents,
            target_audience=target_audience,
            usage=usage,
        )

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def generate_seasonal_products(self, base_product_type: str) -> dict:
        """
        生成季节性/节日产品变体

        Args:
            base_product_type: 基础产品类型

        Returns:
            季节性产品建议
        """
        prompt = f"""请为以下基础数字产品类型生成季节性和节日变体：

【基础产品类型】{base_product_type}

请生成全年的季节性产品计划，以JSON格式返回：
{{
    "base_product": "{base_product_type}",
    "seasonal_calendar": [
        {{
            "month": 1,
            "month_name": "一月",
            "themes": ["新年", "目标设定"],
            "product_variations": [
                {{
                    "name": "产品变体名称",
                    "unique_twist": "独特卖点",
                    "best_launch_date": "最佳上架日期",
                    "expected_demand": "预期需求（高/中/低）"
                }}
            ]
        }}
    ],
    "holiday_specials": [
        {{
            "holiday": "节日名称",
            "date_range": "日期范围",
            "product_ideas": ["产品创意1", "产品创意2"],
            "marketing_angle": "营销角度",
            "advance_preparation": "提前准备时间"
        }}
    ],
    "evergreen_modifications": [
        {{
            "modification": "常青款调整建议",
            "reason": "原因说明"
        }}
    ]
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.8,
        )

        return result

    def suggest_improvements(self, current_product: dict) -> dict:
        """
        为现有产品提供改进建议

        Args:
            current_product: 当前产品信息

        Returns:
            改进建议
        """
        prompt = f"""请分析以下Etsy数字产品并提供改进建议：

【当前产品信息】
{json.dumps(current_product, ensure_ascii=False, indent=2)}

请提供详细的改进建议，以JSON格式返回：
{{
    "overall_assessment": "整体评估",
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["需改进点1", "需改进点2"],
    "title_improvements": {{
        "current_issues": ["当前标题问题"],
        "suggested_title": "建议的新标题",
        "title_tips": ["标题优化技巧"]
    }},
    "description_improvements": {{
        "current_issues": ["当前描述问题"],
        "key_additions": ["应该添加的内容"],
        "formatting_tips": ["格式优化建议"]
    }},
    "pricing_feedback": {{
        "current_assessment": "当前定价评估",
        "recommendation": "定价建议"
    }},
    "visual_suggestions": [
        "视觉改进建议1",
        "视觉改进建议2"
    ],
    "competitive_improvements": [
        "竞争力提升建议1",
        "竞争力提升建议2"
    ],
    "quick_wins": [
        {{
            "improvement": "快速改进项",
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
