"""
Prompt Templates - AI提示词模板集合
用于各种Etsy数字产品销售任务的提示词
"""


class PromptTemplates:
    """所有AI提示词模板"""

    # 系统提示词
    SYSTEM_ETSY_EXPERT = """你是一位资深的Etsy数字产品销售专家，拥有丰富的经验：
- 深入了解Etsy平台的运营规则和算法
- 精通数字产品的设计、定价和营销策略
- 熟悉SEO优化和关键词研究
- 了解各种数字产品类别的市场趋势
- 能够提供实用、可操作的建议

请始终用中文回复，除非用户明确要求使用其他语言。
在给出建议时，请确保具体、可行、有数据支持。"""

    # 市场分析提示词
    MARKET_ANALYSIS = """基于以下市场数据，请分析Etsy数字产品市场的机会：

【热门类别数据】
{categories_data}

【搜索到的产品样本】
{products_data}

请提供以下分析（以JSON格式返回）：
{{
    "market_summary": "市场整体概况（2-3句话）",
    "top_opportunities": [
        {{
            "category": "类别名称",
            "why": "为什么是机会",
            "difficulty": "入门难度（低/中/高）",
            "potential_monthly_income": "预估月收入范围"
        }}
    ],
    "trends": [
        {{
            "trend": "趋势描述",
            "impact": "对卖家的影响"
        }}
    ],
    "recommendations": [
        "具体建议1",
        "具体建议2",
        "具体建议3"
    ]
}}"""

    # 产品创意生成提示词
    PRODUCT_IDEAS = """基于以下信息，为Etsy数字产品店铺生成产品创意：

【目标类别】{category}
【目标受众】{target_audience}
【竞品信息】{competitor_info}
【预算/技能水平】{skill_level}

请生成5-10个具体的产品创意，以JSON格式返回：
{{
    "product_ideas": [
        {{
            "name": "产品名称",
            "description": "产品描述（50-100字）",
            "target_customer": "目标客户画像",
            "unique_selling_point": "独特卖点",
            "estimated_creation_time": "预估制作时间",
            "recommended_price_range": "建议价格范围（美元）",
            "required_tools": ["所需工具1", "所需工具2"],
            "difficulty": "制作难度（简单/中等/困难）",
            "market_potential": "市场潜力（低/中/高）"
        }}
    ],
    "bundle_ideas": [
        {{
            "name": "捆绑包名称",
            "included_products": ["产品1", "产品2"],
            "price_advantage": "价格优势说明"
        }}
    ]
}}"""

    # SEO优化提示词
    SEO_OPTIMIZATION = """请为以下Etsy数字产品优化SEO：

【产品信息】
名称：{product_name}
类型：{product_type}
描述：{product_description}
目标市场：{target_market}

请提供完整的SEO优化方案，以JSON格式返回：
{{
    "optimized_title": "优化后的标题（最多140字符，包含主要关键词）",
    "tags": ["标签1", "标签2", "..."],  // 13个标签，每个最多20字符
    "description": {{
        "opening_hook": "开头吸引语（前160字符很重要）",
        "main_body": "产品详细描述",
        "features_list": ["特点1", "特点2", "..."],
        "call_to_action": "行动号召",
        "full_description": "完整描述文本"
    }},
    "keywords": {{
        "primary": ["主要关键词1", "主要关键词2"],
        "secondary": ["次要关键词1", "次要关键词2"],
        "long_tail": ["长尾关键词1", "长尾关键词2"]
    }},
    "category_suggestion": "建议的Etsy类别",
    "seo_tips": ["额外SEO建议1", "额外SEO建议2"]
}}"""

    # 定价策略提示词
    PRICING_STRATEGY = """请为以下Etsy数字产品制定定价策略：

【产品信息】
名称：{product_name}
类型：{product_type}
独特卖点：{unique_value}
制作成本/时间：{creation_cost}

【竞品价格数据】
{competitor_prices}

【市场定位】
{market_position}

请提供定价建议，以JSON格式返回：
{{
    "recommended_price": 价格数字（美元）,
    "price_range": {{
        "minimum": 最低价,
        "optimal": 最优价,
        "maximum": 最高价
    }},
    "pricing_rationale": "定价理由说明",
    "psychological_pricing_tip": "心理定价建议",
    "bundle_pricing": {{
        "single_item": 单品价格,
        "bundle_discount": "捆绑折扣建议",
        "example_bundle": "示例捆绑方案"
    }},
    "seasonal_adjustments": [
        {{
            "season": "季节/节日",
            "adjustment": "价格调整建议"
        }}
    ],
    "sale_strategy": {{
        "regular_sale_discount": "常规促销折扣",
        "special_event_discount": "特殊活动折扣",
        "first_purchase_offer": "首购优惠建议"
    }}
}}"""

    # 竞品分析提示词
    COMPETITOR_ANALYSIS = """请分析以下Etsy竞品数据：

【竞品列表】
{competitors_data}

【目标类别】
{category}

请提供竞品分析报告，以JSON格式返回：
{{
    "market_overview": {{
        "total_competitors_analyzed": 数量,
        "average_price": 平均价格,
        "price_range": "价格区间",
        "average_reviews": 平均评论数
    }},
    "top_performers": [
        {{
            "name": "产品名称",
            "success_factors": ["成功因素1", "成功因素2"],
            "what_to_learn": "可以学习的地方"
        }}
    ],
    "market_gaps": [
        {{
            "gap": "市场空白描述",
            "opportunity": "机会说明",
            "how_to_fill": "如何填补这个空白"
        }}
    ],
    "competitive_advantages": [
        "可以建立的竞争优势1",
        "可以建立的竞争优势2"
    ],
    "avoid_these": [
        "应该避免的做法1",
        "应该避免的做法2"
    ],
    "differentiation_strategies": [
        {{
            "strategy": "差异化策略",
            "implementation": "如何实施"
        }}
    ]
}}"""

    # 产品描述生成提示词
    PRODUCT_DESCRIPTION = """请为以下Etsy数字产品撰写吸引人的产品描述：

【产品信息】
名称：{product_name}
类型：{product_type}
包含内容：{contents}
适用人群：{target_audience}
使用方式：{usage}

请生成专业的产品描述，以JSON格式返回：
{{
    "headline": "吸引人的标题",
    "opening_paragraph": "开头段落（抓住注意力）",
    "what_you_get": [
        "包含内容1",
        "包含内容2"
    ],
    "features_benefits": [
        {{
            "feature": "功能特点",
            "benefit": "对买家的好处"
        }}
    ],
    "how_to_use": "使用说明",
    "why_choose_us": "为什么选择我们",
    "faq": [
        {{
            "question": "常见问题",
            "answer": "答案"
        }}
    ],
    "closing_cta": "结尾行动号召",
    "full_description": "完整的产品描述文本（可直接复制使用）"
}}"""

    # 店铺名称生成提示词
    SHOP_NAME_IDEAS = """请为Etsy数字产品店铺生成店铺名称创意：

【店铺定位】
主营类别：{main_category}
目标风格：{style}
目标受众：{target_audience}
关键词偏好：{keywords}

请生成10个店铺名称，以JSON格式返回：
{{
    "shop_names": [
        {{
            "name": "店铺名称",
            "meaning": "含义说明",
            "availability_tips": "域名/社交媒体可用性建议",
            "brand_potential": "品牌发展潜力"
        }}
    ],
    "naming_tips": [
        "店铺命名建议1",
        "店铺命名建议2"
    ]
}}"""

    # 营销计划生成提示词
    MARKETING_PLAN = """请为Etsy数字产品店铺制定营销计划：

【店铺信息】
店铺名称：{shop_name}
主营产品：{main_products}
目标月销售额：{target_revenue}
可用预算：{budget}
当前粉丝基础：{current_following}

请生成营销计划，以JSON格式返回：
{{
    "marketing_strategy": {{
        "overall_approach": "整体策略说明",
        "unique_positioning": "独特定位"
    }},
    "free_marketing": [
        {{
            "channel": "渠道名称",
            "actions": ["具体行动1", "具体行动2"],
            "expected_results": "预期效果",
            "time_investment": "时间投入"
        }}
    ],
    "paid_marketing": [
        {{
            "channel": "渠道名称",
            "budget_allocation": "预算分配",
            "roi_expectation": "预期ROI",
            "tips": "使用技巧"
        }}
    ],
    "content_calendar": [
        {{
            "week": 1,
            "focus": "重点内容",
            "posts": ["帖子主题1", "帖子主题2"]
        }}
    ],
    "etsy_specific": {{
        "etsy_ads_recommendation": "Etsy广告建议",
        "etsy_seo_actions": ["SEO行动1", "SEO行动2"],
        "star_seller_path": "成为星级卖家的路径"
    }},
    "metrics_to_track": [
        {{
            "metric": "指标名称",
            "target": "目标值",
            "how_to_measure": "如何测量"
        }}
    ]
}}"""
