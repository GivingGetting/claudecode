"""
Market Analyzer - 市场分析模块
分析Etsy数字产品市场趋势、热门类别和机会
"""

import json
from typing import Optional
from dataclasses import dataclass

from .utils.llm_client import LLMClient
from .utils.etsy_scraper import EtsyScraper
from .prompts.templates import PromptTemplates


@dataclass
class MarketInsight:
    """市场洞察数据结构"""

    summary: str
    top_opportunities: list
    trends: list
    recommendations: list
    raw_data: dict


class MarketAnalyzer:
    """市场分析器 - 分析Etsy数字产品市场"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        初始化市场分析器

        Args:
            llm_client: LLM客户端实例，如果为None则创建新实例
        """
        self.llm = llm_client or LLMClient()
        self.scraper = EtsyScraper()

    def analyze_market(
        self,
        categories: Optional[list[str]] = None,
        include_products: bool = True,
        max_products_per_category: int = 10,
    ) -> MarketInsight:
        """
        分析整体市场状况

        Args:
            categories: 要分析的类别列表，None则分析所有热门类别
            include_products: 是否包含实际产品数据
            max_products_per_category: 每个类别最多抓取的产品数

        Returns:
            MarketInsight: 市场洞察结果
        """
        # 获取热门类别数据
        trending = self.scraper.get_trending_categories()

        if categories:
            trending = [c for c in trending if c["name"] in categories]

        # 获取产品样本数据
        products_data = {}
        if include_products:
            for category in trending[:5]:  # 限制分析的类别数
                keyword = category["keywords"][0]
                try:
                    products = self.scraper.search_products(
                        keyword, max_results=max_products_per_category, digital_only=True
                    )
                    products_data[category["name"]] = [
                        {
                            "title": p.title,
                            "price": p.price,
                            "rating": p.rating,
                            "reviews": p.reviews_count,
                            "is_bestseller": p.is_bestseller,
                        }
                        for p in products
                    ]
                except Exception as e:
                    print(f"获取 {category['name']} 产品数据失败: {e}")
                    products_data[category["name"]] = []

        # 准备分析提示
        categories_str = json.dumps(trending, ensure_ascii=False, indent=2)
        products_str = json.dumps(products_data, ensure_ascii=False, indent=2)

        prompt = PromptTemplates.MARKET_ANALYSIS.format(
            categories_data=categories_str, products_data=products_str
        )

        # 调用AI分析
        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return MarketInsight(
            summary=result.get("market_summary", ""),
            top_opportunities=result.get("top_opportunities", []),
            trends=result.get("trends", []),
            recommendations=result.get("recommendations", []),
            raw_data=result,
        )

    def find_niche_opportunities(self) -> list[dict]:
        """
        发现利基市场机会

        Returns:
            利基机会列表
        """
        niches = self.scraper.get_niche_opportunities()

        # 使用AI补充分析
        prompt = f"""基于以下利基市场数据，请评估每个利基的当前机会价值，并添加具体的入门建议：

{json.dumps(niches, ensure_ascii=False, indent=2)}

请为每个利基添加以下信息并返回JSON：
{{
    "niches": [
        {{
            "niche": "原利基名称",
            "description": "原描述",
            "potential": "潜力评级",
            "competition": "竞争程度",
            "entry_difficulty": "入门难度",
            "specific_product_ideas": ["具体产品idea1", "具体产品idea2"],
            "first_steps": ["入门第一步", "第二步", "第三步"],
            "tools_needed": ["需要的工具"],
            "time_to_first_sale": "预计首次销售时间"
        }}
    ]
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result.get("niches", niches)

    def analyze_category(self, category_name: str) -> dict:
        """
        深入分析特定类别

        Args:
            category_name: 类别名称或关键词

        Returns:
            类别分析结果
        """
        # 搜索该类别的产品
        products = self.scraper.search_products(
            category_name, max_results=20, digital_only=True
        )

        if not products:
            return {
                "error": f"未找到'{category_name}'相关产品",
                "suggestion": "请尝试其他关键词",
            }

        # 计算统计数据
        prices = [p.price for p in products if p.price > 0]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        ratings = [p.rating for p in products if p.rating > 0]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        reviews = [p.reviews_count for p in products]
        avg_reviews = sum(reviews) / len(reviews) if reviews else 0

        bestsellers = sum(1 for p in products if p.is_bestseller)

        product_data = [
            {
                "title": p.title,
                "price": p.price,
                "rating": p.rating,
                "reviews": p.reviews_count,
                "is_bestseller": p.is_bestseller,
            }
            for p in products
        ]

        prompt = f"""请深入分析以下Etsy数字产品类别：

【类别】{category_name}

【统计数据】
- 平均价格: ${avg_price:.2f}
- 价格区间: ${min_price:.2f} - ${max_price:.2f}
- 平均评分: {avg_rating:.1f}
- 平均评论数: {avg_reviews:.0f}
- 畅销产品占比: {bestsellers}/{len(products)}

【产品样本】
{json.dumps(product_data, ensure_ascii=False, indent=2)}

请提供详细的类别分析，以JSON格式返回：
{{
    "category_overview": "类别概述",
    "market_size_estimate": "市场规模估计",
    "competition_level": "竞争程度（低/中/高/非常高）",
    "entry_barrier": "入门门槛",
    "price_analysis": {{
        "sweet_spot": "最佳价格点",
        "premium_opportunity": "是否有高端市场机会",
        "budget_opportunity": "是否有低价市场机会"
    }},
    "success_patterns": ["成功产品的共同特点1", "特点2"],
    "common_mistakes": ["常见错误1", "错误2"],
    "differentiation_ideas": ["差异化创意1", "创意2"],
    "recommended_entry_strategy": "建议的入门策略",
    "estimated_monthly_potential": "预估月收入潜力"
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        result["statistics"] = {
            "avg_price": round(avg_price, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "avg_rating": round(avg_rating, 1),
            "avg_reviews": round(avg_reviews, 0),
            "total_products_analyzed": len(products),
            "bestsellers_count": bestsellers,
        }

        return result

    def get_trending_keywords(self, category: Optional[str] = None) -> list[dict]:
        """
        获取热门搜索关键词

        Args:
            category: 特定类别，None则返回通用关键词

        Returns:
            关键词列表及其趋势信息
        """
        base_keywords = [
            "digital planner",
            "printable",
            "svg",
            "canva template",
            "notion template",
            "spreadsheet",
            "wedding invitation",
            "wall art",
            "ebook template",
            "social media template",
        ]

        if category:
            base_keywords = [f"{category} {kw}" for kw in base_keywords[:5]]

        prompt = f"""基于以下Etsy数字产品基础关键词，请生成一份热门关键词分析报告：

基础关键词: {', '.join(base_keywords)}
{f'目标类别: {category}' if category else '通用数字产品'}

请返回JSON格式的关键词分析：
{{
    "trending_keywords": [
        {{
            "keyword": "关键词",
            "search_volume": "搜索量估计（高/中/低）",
            "competition": "竞争程度（高/中/低）",
            "trend": "趋势（上升/稳定/下降）",
            "best_for": "最适合的产品类型",
            "long_tail_variations": ["长尾变体1", "长尾变体2"]
        }}
    ],
    "seasonal_keywords": [
        {{
            "keyword": "季节性关键词",
            "peak_months": ["月份1", "月份2"],
            "preparation_tip": "准备建议"
        }}
    ],
    "emerging_keywords": [
        {{
            "keyword": "新兴关键词",
            "why_emerging": "为什么正在兴起",
            "opportunity_window": "机会窗口"
        }}
    ]
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result
