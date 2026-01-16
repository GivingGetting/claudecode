"""
Competitor Analyzer - 竞品分析模块
分析Etsy上的竞争对手、成功模式和市场差异化机会
"""

import json
from typing import Optional

from .utils.llm_client import LLMClient
from .utils.etsy_scraper import EtsyScraper
from .prompts.templates import PromptTemplates


class CompetitorAnalyzer:
    """竞品分析器 - 深入分析Etsy竞争对手"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        初始化竞品分析器

        Args:
            llm_client: LLM客户端实例
        """
        self.llm = llm_client or LLMClient()
        self.scraper = EtsyScraper()

    def analyze_competitors(
        self, category: str, max_competitors: int = 20
    ) -> dict:
        """
        分析特定类别的竞争对手

        Args:
            category: 产品类别
            max_competitors: 最大分析数量

        Returns:
            竞品分析报告
        """
        # 获取竞品数据
        products = self.scraper.search_products(
            category, max_results=max_competitors, digital_only=True
        )

        if not products:
            return {"error": f"未找到'{category}'相关竞品", "suggestion": "请尝试其他关键词"}

        competitors_data = json.dumps(
            [
                {
                    "title": p.title,
                    "price": p.price,
                    "shop_name": p.shop_name,
                    "rating": p.rating,
                    "reviews_count": p.reviews_count,
                    "is_bestseller": p.is_bestseller,
                    "url": p.url,
                }
                for p in products
            ],
            ensure_ascii=False,
            indent=2,
        )

        prompt = PromptTemplates.COMPETITOR_ANALYSIS.format(
            competitors_data=competitors_data, category=category
        )

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def find_market_gaps(self, category: str) -> dict:
        """
        发现市场空白和机会

        Args:
            category: 产品类别

        Returns:
            市场空白分析
        """
        # 获取现有产品
        products = self.scraper.search_products(
            category, max_results=30, digital_only=True
        )

        product_titles = [p.title for p in products]

        prompt = f"""请分析以下Etsy数字产品类别中的市场空白和机会：

【类别】{category}

【现有产品标题样本】
{json.dumps(product_titles, ensure_ascii=False, indent=2)}

请识别市场空白，返回JSON格式：
{{
    "category_analysis": {{
        "current_offerings": "当前市场提供的产品类型",
        "saturation_areas": ["饱和领域1", "饱和领域2"],
        "underserved_areas": ["未充分服务的领域1", "领域2"]
    }},
    "market_gaps": [
        {{
            "gap": "市场空白描述",
            "evidence": "证据/原因",
            "potential_products": ["可以填补的产品1", "产品2"],
            "difficulty_to_fill": "填补难度（低/中/高）",
            "potential_reward": "潜在回报（低/中/高）",
            "first_mover_advantage": "是否有先发优势"
        }}
    ],
    "niche_opportunities": [
        {{
            "niche": "利基机会",
            "description": "描述",
            "target_customer": "目标客户",
            "entry_strategy": "进入策略"
        }}
    ],
    "avoid_areas": [
        {{
            "area": "应避免的领域",
            "reason": "原因"
        }}
    ],
    "recommended_focus": {{
        "primary": "主要聚焦方向",
        "secondary": "次要方向",
        "rationale": "理由"
    }}
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.8,
        )

        return result

    def analyze_top_sellers(self, category: str, count: int = 10) -> dict:
        """
        分析顶级卖家的成功模式

        Args:
            category: 产品类别
            count: 分析数量

        Returns:
            成功模式分析
        """
        # 获取评价最高的产品
        products = self.scraper.search_products(
            category,
            max_results=count,
            digital_only=True,
            sort_by="top_customer_reviews",
        )

        top_sellers = [
            {
                "title": p.title,
                "price": p.price,
                "rating": p.rating,
                "reviews": p.reviews_count,
                "shop": p.shop_name,
                "is_bestseller": p.is_bestseller,
            }
            for p in products
            if p.reviews_count > 0
        ]

        prompt = f"""请分析以下Etsy数字产品顶级卖家的成功模式：

【类别】{category}

【顶级产品数据】
{json.dumps(top_sellers, ensure_ascii=False, indent=2)}

请返回JSON格式的成功模式分析：
{{
    "success_patterns": [
        {{
            "pattern": "成功模式",
            "evidence": "证据",
            "how_to_replicate": "如何复制这个模式",
            "difficulty": "复制难度"
        }}
    ],
    "common_traits": {{
        "pricing": "定价特点",
        "titles": "标题特点",
        "product_types": "产品类型特点",
        "value_proposition": "价值主张特点"
    }},
    "differentiation_examples": [
        {{
            "product": "产品名称",
            "unique_angle": "独特角度",
            "lesson": "可学习的点"
        }}
    ],
    "actionable_insights": [
        {{
            "insight": "洞察",
            "action": "具体行动",
            "expected_outcome": "预期结果"
        }}
    ],
    "benchmarks": {{
        "minimum_viable_reviews": "最少需要多少评价",
        "target_rating": "目标评分",
        "price_sweet_spot": "价格甜点"
    }}
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        result["analyzed_products"] = top_sellers

        return result

    def swot_analysis(self, your_product: dict, category: str) -> dict:
        """
        SWOT分析

        Args:
            your_product: 你的产品信息
            category: 产品类别

        Returns:
            SWOT分析结果
        """
        # 获取竞品数据作为对比
        competitors = self.scraper.search_products(
            category, max_results=15, digital_only=True
        )

        competitor_data = [
            {"title": p.title, "price": p.price, "reviews": p.reviews_count}
            for p in competitors
        ]

        prompt = f"""请对以下产品进行SWOT分析（相对于市场竞品）：

【你的产品】
{json.dumps(your_product, ensure_ascii=False, indent=2)}

【市场竞品样本】
{json.dumps(competitor_data, ensure_ascii=False, indent=2)}

请返回JSON格式的SWOT分析：
{{
    "strengths": [
        {{
            "strength": "优势",
            "impact": "影响程度（高/中/低）",
            "how_to_leverage": "如何利用这个优势"
        }}
    ],
    "weaknesses": [
        {{
            "weakness": "劣势",
            "impact": "影响程度",
            "mitigation_strategy": "缓解策略"
        }}
    ],
    "opportunities": [
        {{
            "opportunity": "机会",
            "urgency": "紧迫性",
            "action_required": "需要的行动"
        }}
    ],
    "threats": [
        {{
            "threat": "威胁",
            "likelihood": "发生可能性",
            "defensive_strategy": "防御策略"
        }}
    ],
    "strategic_recommendations": [
        {{
            "recommendation": "战略建议",
            "priority": "优先级",
            "implementation": "实施方式"
        }}
    ],
    "competitive_position": {{
        "current": "当前竞争位置",
        "target": "目标位置",
        "gap_analysis": "差距分析"
    }}
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def trend_analysis(self, category: str) -> dict:
        """
        分析类别趋势

        Args:
            category: 产品类别

        Returns:
            趋势分析
        """
        # 获取产品数据
        products = self.scraper.search_products(
            category, max_results=25, digital_only=True
        )

        product_data = [
            {
                "title": p.title,
                "price": p.price,
                "is_bestseller": p.is_bestseller,
            }
            for p in products
        ]

        prompt = f"""请分析以下Etsy数字产品类别的趋势：

【类别】{category}

【当前产品样本】
{json.dumps(product_data, ensure_ascii=False, indent=2)}

请返回JSON格式的趋势分析：
{{
    "current_trends": [
        {{
            "trend": "趋势描述",
            "strength": "趋势强度",
            "longevity": "预计持续时间",
            "opportunity": "机会分析"
        }}
    ],
    "emerging_trends": [
        {{
            "trend": "新兴趋势",
            "signals": ["信号1", "信号2"],
            "early_adopter_advantage": "早期进入优势"
        }}
    ],
    "declining_trends": [
        {{
            "trend": "下降趋势",
            "reason": "原因",
            "advice": "建议"
        }}
    ],
    "seasonal_patterns": [
        {{
            "season": "季节",
            "trend_characteristics": "趋势特点",
            "preparation_advice": "准备建议"
        }}
    ],
    "future_predictions": [
        {{
            "prediction": "预测",
            "timeframe": "时间框架",
            "confidence": "置信度",
            "preparation_steps": ["准备步骤1", "步骤2"]
        }}
    ],
    "recommended_strategy": {{
        "short_term": "短期策略",
        "long_term": "长期策略"
    }}
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.8,
        )

        return result
