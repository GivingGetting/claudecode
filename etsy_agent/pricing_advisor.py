"""
Pricing Advisor - 定价策略模块
分析市场价格、制定定价策略、优化价格点
"""

import json
from typing import Optional

from .utils.llm_client import LLMClient
from .utils.etsy_scraper import EtsyScraper
from .prompts.templates import PromptTemplates


class PricingAdvisor:
    """定价顾问 - 帮助制定最优定价策略"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        初始化定价顾问

        Args:
            llm_client: LLM客户端实例
        """
        self.llm = llm_client or LLMClient()
        self.scraper = EtsyScraper()

    def get_pricing_recommendation(
        self,
        product_name: str,
        product_type: str,
        unique_value: str,
        creation_cost: str = "未知",
        market_position: str = "中端市场",
        analyze_competitors: bool = True,
    ) -> dict:
        """
        获取定价建议

        Args:
            product_name: 产品名称
            product_type: 产品类型
            unique_value: 独特价值/卖点
            creation_cost: 制作成本/时间
            market_position: 市场定位
            analyze_competitors: 是否分析竞品价格

        Returns:
            定价建议
        """
        # 获取竞品价格数据
        competitor_prices = "暂无竞品数据"
        if analyze_competitors:
            try:
                products = self.scraper.search_products(
                    product_type, max_results=15, digital_only=True
                )
                if products:
                    prices = [p.price for p in products if p.price > 0]
                    competitor_prices = json.dumps(
                        {
                            "sample_prices": prices,
                            "min_price": min(prices) if prices else 0,
                            "max_price": max(prices) if prices else 0,
                            "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
                            "products": [
                                {"title": p.title[:50], "price": p.price, "reviews": p.reviews_count}
                                for p in products[:10]
                            ],
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
            except Exception:
                pass

        prompt = PromptTemplates.PRICING_STRATEGY.format(
            product_name=product_name,
            product_type=product_type,
            unique_value=unique_value,
            creation_cost=creation_cost,
            competitor_prices=competitor_prices,
            market_position=market_position,
        )

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def analyze_price_elasticity(self, product_type: str, current_price: float) -> dict:
        """
        分析价格弹性

        Args:
            product_type: 产品类型
            current_price: 当前价格

        Returns:
            价格弹性分析
        """
        # 获取该类型产品的价格分布
        products = self.scraper.search_products(
            product_type, max_results=20, digital_only=True
        )

        prices = [p.price for p in products if p.price > 0]
        price_data = {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "avg": round(sum(prices) / len(prices), 2) if prices else 0,
            "distribution": prices,
        }

        prompt = f"""请分析以下数字产品的价格弹性：

【产品类型】{product_type}
【当前价格】${current_price}
【市场价格数据】
{json.dumps(price_data, ensure_ascii=False, indent=2)}

请返回JSON格式的价格弹性分析：
{{
    "current_position": "当前价格在市场中的位置",
    "price_sensitivity": "价格敏感度评估（高/中/低）",
    "elasticity_analysis": {{
        "if_increase_10_percent": "预计销量影响",
        "if_decrease_10_percent": "预计销量影响",
        "optimal_adjustment": "最优调整建议"
    }},
    "price_tiers": [
        {{
            "tier": "价格层级名称",
            "range": "价格范围",
            "target_customer": "目标客户",
            "value_perception": "价值感知"
        }}
    ],
    "psychological_price_points": [
        {{
            "price": 价格数字,
            "psychology": "心理效应说明",
            "recommendation": "是否推荐"
        }}
    ],
    "testing_strategy": {{
        "a_b_test_suggestion": "A/B测试建议",
        "price_test_range": "测试价格范围"
    }}
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def calculate_bundle_pricing(
        self, products: list[dict], target_discount: float = 0.2
    ) -> dict:
        """
        计算捆绑包定价

        Args:
            products: 产品列表，每个包含name和price
            target_discount: 目标折扣率

        Returns:
            捆绑包定价建议
        """
        total_individual = sum(p.get("price", 0) for p in products)

        prompt = f"""请为以下产品组合计算最优捆绑包定价：

【产品列表】
{json.dumps(products, ensure_ascii=False, indent=2)}

【单独购买总价】${total_individual}
【目标折扣率】{target_discount * 100}%

请返回JSON格式的捆绑包定价方案：
{{
    "individual_total": {total_individual},
    "recommended_bundle_price": 推荐捆绑价格,
    "actual_discount": "实际折扣率",
    "perceived_value": "感知价值分析",
    "bundle_naming_suggestions": ["捆绑包命名建议1", "建议2"],
    "pricing_psychology": "定价心理学分析",
    "alternative_bundles": [
        {{
            "name": "备选捆绑方案",
            "included_products": ["产品1", "产品2"],
            "price": 价格,
            "target_customer": "目标客户"
        }}
    ],
    "upsell_strategy": {{
        "from_single_to_bundle": "从单品到捆绑的升级策略",
        "messaging": "促销文案建议"
    }}
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def get_sale_pricing_strategy(
        self, original_price: float, product_type: str, sale_reason: str = "促销活动"
    ) -> dict:
        """
        获取促销定价策略

        Args:
            original_price: 原价
            product_type: 产品类型
            sale_reason: 促销原因

        Returns:
            促销定价策略
        """
        prompt = f"""请为以下产品制定促销定价策略：

【原价】${original_price}
【产品类型】{product_type}
【促销原因】{sale_reason}

请返回JSON格式的促销定价策略：
{{
    "original_price": {original_price},
    "recommended_sale_prices": [
        {{
            "discount_level": "折扣级别（轻度/中度/深度）",
            "sale_price": 促销价,
            "discount_percentage": "折扣百分比",
            "best_for": "最适合的场景",
            "expected_conversion_boost": "预期转化提升"
        }}
    ],
    "etsy_sale_features": {{
        "use_sale_badge": true,
        "suggested_duration": "建议促销时长",
        "best_timing": "最佳促销时机"
    }},
    "psychological_tactics": [
        {{
            "tactic": "心理策略",
            "implementation": "如何实施",
            "expected_effect": "预期效果"
        }}
    ],
    "urgency_messaging": [
        "紧迫感文案1",
        "紧迫感文案2"
    ],
    "post_sale_strategy": "促销结束后的策略",
    "cautions": ["注意事项1", "注意事项2"]
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def competitive_price_analysis(self, product_type: str) -> dict:
        """
        竞品价格分析

        Args:
            product_type: 产品类型

        Returns:
            竞品价格分析报告
        """
        # 获取不同排序方式的产品
        products_relevant = self.scraper.search_products(
            product_type, max_results=15, digital_only=True, sort_by="most_relevant"
        )

        products_reviews = self.scraper.search_products(
            product_type, max_results=15, digital_only=True, sort_by="top_customer_reviews"
        )

        all_products = products_relevant + products_reviews
        # 去重
        seen_titles = set()
        unique_products = []
        for p in all_products:
            if p.title not in seen_titles:
                seen_titles.add(p.title)
                unique_products.append(p)

        prices = [p.price for p in unique_products if p.price > 0]

        price_brackets = {
            "under_5": len([p for p in prices if p < 5]),
            "5_to_10": len([p for p in prices if 5 <= p < 10]),
            "10_to_20": len([p for p in prices if 10 <= p < 20]),
            "20_to_50": len([p for p in prices if 20 <= p < 50]),
            "over_50": len([p for p in prices if p >= 50]),
        }

        product_data = [
            {
                "title": p.title[:60],
                "price": p.price,
                "rating": p.rating,
                "reviews": p.reviews_count,
                "is_bestseller": p.is_bestseller,
            }
            for p in unique_products[:20]
        ]

        prompt = f"""请分析以下Etsy数字产品类别的竞品价格：

【产品类别】{product_type}

【价格统计】
- 最低价: ${min(prices) if prices else 0}
- 最高价: ${max(prices) if prices else 0}
- 平均价: ${round(sum(prices)/len(prices), 2) if prices else 0}
- 价格分布: {json.dumps(price_brackets)}

【产品样本】
{json.dumps(product_data, ensure_ascii=False, indent=2)}

请返回JSON格式的竞品价格分析：
{{
    "market_overview": {{
        "price_range": "价格范围描述",
        "dominant_price_point": "主流价格点",
        "market_maturity": "市场成熟度"
    }},
    "price_segments": [
        {{
            "segment": "价格区间",
            "characteristics": "该区间产品特点",
            "competition_level": "竞争程度",
            "opportunity": "机会分析"
        }}
    ],
    "bestseller_pricing_pattern": {{
        "common_price_range": "畅销品价格范围",
        "key_insight": "关键洞察"
    }},
    "pricing_opportunities": [
        {{
            "opportunity": "定价机会",
            "strategy": "策略建议",
            "risk_level": "风险等级"
        }}
    ],
    "recommended_entry_price": {{
        "price": 建议入门价格,
        "rationale": "理由说明"
    }},
    "premium_pricing_potential": {{
        "possible": true/false,
        "requirements": ["要求1", "要求2"],
        "suggested_premium_price": 建议高端价格
    }}
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        result["raw_statistics"] = {
            "total_products_analyzed": len(unique_products),
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
            "price_brackets": price_brackets,
        }

        return result
