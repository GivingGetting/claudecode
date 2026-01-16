"""
Etsy AI Agent - 主智能体类
整合所有模块，提供统一的接口来帮助Etsy数字产品销售
"""

import json
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from .utils.llm_client import LLMClient
from .market_analyzer import MarketAnalyzer
from .product_generator import ProductGenerator
from .seo_optimizer import SEOOptimizer
from .pricing_advisor import PricingAdvisor
from .competitor_analyzer import CompetitorAnalyzer
from .prompts.templates import PromptTemplates


@dataclass
class AgentConfig:
    """智能体配置"""

    ai_provider: str = "anthropic"
    ai_model: str = "claude-sonnet-4-20250514"
    language: str = "zh"
    verbose: bool = True


class EtsyAgent:
    """
    Etsy AI智能体 - 你的Etsy数字产品销售助手

    功能：
    - 市场分析和趋势发现
    - 产品创意生成
    - SEO优化
    - 定价策略
    - 竞品分析
    - 营销建议
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        初始化Etsy AI智能体

        Args:
            config: 智能体配置
        """
        self.config = config or AgentConfig()
        self.llm = LLMClient(
            provider=self.config.ai_provider, model=self.config.ai_model
        )

        # 初始化各功能模块
        self.market_analyzer = MarketAnalyzer(self.llm)
        self.product_generator = ProductGenerator(self.llm)
        self.seo_optimizer = SEOOptimizer(self.llm)
        self.pricing_advisor = PricingAdvisor(self.llm)
        self.competitor_analyzer = CompetitorAnalyzer(self.llm)

        # 会话历史
        self.conversation_history = []

    def _log(self, message: str):
        """输出日志"""
        if self.config.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")

    # ==================== 快速启动功能 ====================

    def quick_start(self) -> dict:
        """
        快速启动指南 - 帮助新手开始Etsy数字产品之旅

        Returns:
            入门指南和建议
        """
        self._log("生成快速启动指南...")

        prompt = """请生成一份Etsy数字产品销售的快速启动指南。

返回JSON格式：
{
    "welcome_message": "欢迎语",
    "getting_started_steps": [
        {
            "step": 1,
            "title": "步骤标题",
            "description": "详细描述",
            "time_needed": "预计时间",
            "tips": ["技巧1", "技巧2"]
        }
    ],
    "recommended_categories_for_beginners": [
        {
            "category": "类别名称",
            "why_good_for_beginners": "为什么适合新手",
            "tools_needed": ["工具1", "工具2"],
            "potential_income": "潜在收入"
        }
    ],
    "common_mistakes_to_avoid": [
        {
            "mistake": "常见错误",
            "solution": "解决方案"
        }
    ],
    "success_timeline": {
        "first_week": "第一周目标",
        "first_month": "第一个月目标",
        "first_quarter": "第一季度目标"
    },
    "essential_tools": [
        {
            "tool": "工具名称",
            "purpose": "用途",
            "cost": "费用",
            "alternative": "替代品"
        }
    ],
    "motivation": "激励语"
}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    def find_your_niche(
        self, interests: list[str] = None, skills: list[str] = None
    ) -> dict:
        """
        帮助找到适合你的利基市场

        Args:
            interests: 你的兴趣列表
            skills: 你的技能列表

        Returns:
            利基市场建议
        """
        self._log("分析最适合你的利基市场...")

        interests_str = ", ".join(interests) if interests else "未指定"
        skills_str = ", ".join(skills) if skills else "未指定"

        prompt = f"""请根据以下信息，帮助推荐最适合的Etsy数字产品利基市场：

【兴趣爱好】{interests_str}
【技能特长】{skills_str}

请返回JSON格式：
{{
    "analysis": "兴趣和技能分析",
    "recommended_niches": [
        {{
            "niche": "利基市场名称",
            "match_score": "匹配度（1-10）",
            "why_suitable": "为什么适合你",
            "skill_gap": "需要补充的技能",
            "first_product_idea": "第一个产品创意",
            "competition_level": "竞争程度",
            "income_potential": "收入潜力"
        }}
    ],
    "skill_development_path": [
        {{
            "skill": "需要学习的技能",
            "resources": ["学习资源"],
            "time_to_learn": "学习时间"
        }}
    ],
    "immediate_action": "立即可以采取的行动"
}}"""

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.8,
        )

        return result

    # ==================== 综合分析功能 ====================

    def comprehensive_analysis(self, category: str) -> dict:
        """
        对特定类别进行全面分析

        Args:
            category: 产品类别

        Returns:
            全面分析报告
        """
        self._log(f"开始对 '{category}' 进行全面分析...")

        # 收集各模块的分析结果
        results = {}

        self._log("1. 分析市场状况...")
        results["market"] = self.market_analyzer.analyze_category(category)

        self._log("2. 分析竞争对手...")
        results["competitors"] = self.competitor_analyzer.analyze_competitors(category)

        self._log("3. 分析价格...")
        results["pricing"] = self.pricing_advisor.competitive_price_analysis(category)

        self._log("4. 发现市场空白...")
        results["gaps"] = self.competitor_analyzer.find_market_gaps(category)

        self._log("5. 分析趋势...")
        results["trends"] = self.competitor_analyzer.trend_analysis(category)

        # 生成综合报告
        self._log("6. 生成综合报告...")

        prompt = f"""基于以下各模块的分析结果，请生成一份综合分析报告：

【类别】{category}

【市场分析】
{json.dumps(results['market'], ensure_ascii=False, indent=2)[:2000]}

【竞品分析】
{json.dumps(results['competitors'], ensure_ascii=False, indent=2)[:2000]}

【定价分析】
{json.dumps(results['pricing'], ensure_ascii=False, indent=2)[:2000]}

请生成简洁的综合报告，返回JSON格式：
{{
    "executive_summary": "执行摘要（3-5句话）",
    "key_insights": [
        {{
            "insight": "关键洞察",
            "importance": "重要性",
            "action": "建议行动"
        }}
    ],
    "opportunity_score": "机会评分（1-10）",
    "risk_assessment": {{
        "level": "风险等级",
        "main_risks": ["主要风险"],
        "mitigations": ["缓解措施"]
    }},
    "recommended_strategy": {{
        "entry_approach": "进入策略",
        "differentiation": "差异化方向",
        "pricing_strategy": "定价策略",
        "first_products": ["建议首批产品"]
    }},
    "success_probability": "成功概率估计",
    "next_steps": [
        {{
            "step": "下一步",
            "priority": "优先级",
            "detail": "详细说明"
        }}
    ]
}}"""

        summary = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        results["summary"] = summary
        self._log("分析完成！")

        return results

    # ==================== 产品开发工作流 ====================

    def product_development_workflow(
        self, niche: str, target_audience: str = "通用"
    ) -> dict:
        """
        完整的产品开发工作流

        Args:
            niche: 利基市场
            target_audience: 目标受众

        Returns:
            完整的产品开发方案
        """
        self._log(f"开始产品开发工作流: {niche}")

        workflow = {}

        # Step 1: 生成产品创意
        self._log("Step 1: 生成产品创意...")
        workflow["ideas"] = self.product_generator.generate_ideas(
            category=niche, target_audience=target_audience, num_ideas=5
        )

        # Step 2: 为最佳创意生成产品描述
        self._log("Step 2: 生成产品描述...")
        if workflow["ideas"].get("product_ideas"):
            best_idea = workflow["ideas"]["product_ideas"][0]
            workflow["description"] = self.product_generator.generate_description(
                product_name=best_idea["name"],
                product_type=niche,
                contents=best_idea.get("description", ""),
                target_audience=target_audience,
            )

        # Step 3: SEO优化
        self._log("Step 3: SEO优化...")
        if workflow.get("description"):
            workflow["seo"] = self.seo_optimizer.optimize_listing(
                product_name=best_idea["name"],
                product_type=niche,
                product_description=workflow["description"].get("full_description", ""),
            )

        # Step 4: 定价建议
        self._log("Step 4: 定价建议...")
        workflow["pricing"] = self.pricing_advisor.get_pricing_recommendation(
            product_name=best_idea["name"] if workflow["ideas"].get("product_ideas") else niche,
            product_type=niche,
            unique_value=best_idea.get("unique_selling_point", "") if workflow["ideas"].get("product_ideas") else "",
        )

        # Step 5: 生成上架清单
        self._log("Step 5: 生成上架清单...")

        prompt = f"""基于以下产品开发信息，请生成一份Etsy上架清单：

【产品创意】
{json.dumps(workflow.get('ideas', {}).get('product_ideas', [{}])[0] if workflow.get('ideas', {}).get('product_ideas') else {}, ensure_ascii=False, indent=2)}

【产品描述】
{json.dumps(workflow.get('description', {}), ensure_ascii=False, indent=2)[:1500]}

【SEO优化】
{json.dumps(workflow.get('seo', {}), ensure_ascii=False, indent=2)[:1500]}

【定价】
{json.dumps(workflow.get('pricing', {}), ensure_ascii=False, indent=2)[:1000]}

请生成可直接使用的上架清单，返回JSON格式：
{{
    "listing_checklist": {{
        "title": "最终标题",
        "price": "定价",
        "tags": ["标签1", "标签2"],
        "description": "完整描述",
        "category_path": "建议类别路径",
        "shipping": "配送设置（数字产品）"
    }},
    "product_images_needed": [
        {{
            "image_type": "图片类型（主图/场景图等）",
            "requirements": "要求",
            "tips": "拍摄/设计技巧"
        }}
    ],
    "file_preparation": {{
        "file_formats": ["建议格式"],
        "organization": "文件组织建议",
        "readme_include": "是否需要说明文件"
    }},
    "pre_launch_checklist": [
        "上架前检查项1",
        "检查项2"
    ],
    "launch_day_actions": [
        "上架当天行动1",
        "行动2"
    ]
}}"""

        workflow["launch_checklist"] = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        self._log("产品开发工作流完成！")
        return workflow

    # ==================== 店铺建设功能 ====================

    def shop_branding(
        self,
        main_category: str,
        style: str = "现代简约",
        target_audience: str = "通用",
    ) -> dict:
        """
        店铺品牌建设

        Args:
            main_category: 主营类别
            style: 风格偏好
            target_audience: 目标受众

        Returns:
            品牌建设方案
        """
        self._log("生成店铺品牌方案...")

        # 生成店铺名称
        shop_names = self.llm.chat_json(
            prompt=PromptTemplates.SHOP_NAME_IDEAS.format(
                main_category=main_category,
                style=style,
                target_audience=target_audience,
                keywords="自动生成",
            ),
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.9,
        )

        # 生成品牌视觉方案
        visual_prompt = f"""请为以下Etsy店铺生成品牌视觉方案：

【主营类别】{main_category}
【风格】{style}
【目标受众】{target_audience}

返回JSON格式：
{{
    "color_palette": {{
        "primary": "主色（含色值）",
        "secondary": "辅助色",
        "accent": "强调色",
        "neutral": "中性色",
        "usage_guide": "颜色使用指南"
    }},
    "typography": {{
        "heading_font": "标题字体推荐",
        "body_font": "正文字体推荐",
        "font_pairing_reason": "字体搭配原因"
    }},
    "visual_style": {{
        "overall_aesthetic": "整体美学",
        "mood": "情绪/氛围",
        "key_visual_elements": ["视觉元素1", "元素2"]
    }},
    "shop_banner": {{
        "dimensions": "尺寸要求",
        "content_suggestions": ["内容建议"],
        "design_tips": ["设计技巧"]
    }},
    "product_photo_style": {{
        "background": "背景建议",
        "lighting": "光线建议",
        "props": "道具建议",
        "consistency_tips": ["一致性技巧"]
    }},
    "brand_voice": {{
        "tone": "语调",
        "personality": "品牌个性",
        "key_phrases": ["常用短语/表达"]
    }}
}}"""

        visual_branding = self.llm.chat_json(
            prompt=visual_prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.8,
        )

        return {
            "shop_names": shop_names,
            "visual_branding": visual_branding,
        }

    def marketing_plan(
        self,
        shop_name: str,
        main_products: str,
        target_revenue: str = "$500/月",
        budget: str = "免费",
    ) -> dict:
        """
        生成营销计划

        Args:
            shop_name: 店铺名称
            main_products: 主营产品
            target_revenue: 目标收入
            budget: 营销预算

        Returns:
            营销计划
        """
        self._log("生成营销计划...")

        prompt = PromptTemplates.MARKETING_PLAN.format(
            shop_name=shop_name,
            main_products=main_products,
            target_revenue=target_revenue,
            budget=budget,
            current_following="0（新店铺）",
        )

        result = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        return result

    # ==================== 对话功能 ====================

    def chat(self, message: str) -> str:
        """
        与智能体对话

        Args:
            message: 用户消息

        Returns:
            智能体回复
        """
        # 构建对话上下文
        context = "\n".join(
            [f"用户: {h['user']}\n助手: {h['assistant']}" for h in self.conversation_history[-5:]]
        )

        system_prompt = f"""{PromptTemplates.SYSTEM_ETSY_EXPERT}

你是一个专注于帮助用户在Etsy上销售数字产品的AI助手。你可以：
1. 分析市场和竞争对手
2. 生成产品创意
3. 优化SEO（标题、描述、标签）
4. 制定定价策略
5. 提供营销建议

请用简洁、友好的方式回答问题。如果用户的问题需要具体数据分析，建议他们使用具体的功能函数。

之前的对话：
{context if context else '（新对话）'}"""

        response = self.llm.chat(
            prompt=message, system_prompt=system_prompt, temperature=0.7
        )

        # 保存对话历史
        self.conversation_history.append({"user": message, "assistant": response})

        return response

    # ==================== 报告生成 ====================

    def generate_daily_insights(self, categories: list[str] = None) -> dict:
        """
        生成每日市场洞察

        Args:
            categories: 关注的类别列表

        Returns:
            每日洞察报告
        """
        self._log("生成每日市场洞察...")

        if categories is None:
            categories = ["digital planner", "canva template", "svg files"]

        insights = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "categories": {},
        }

        for category in categories:
            self._log(f"分析: {category}")
            try:
                # 获取简要市场数据
                analysis = self.market_analyzer.analyze_category(category)
                insights["categories"][category] = {
                    "summary": analysis.get("category_overview", ""),
                    "competition": analysis.get("competition_level", ""),
                    "opportunity": analysis.get("recommended_entry_strategy", ""),
                    "statistics": analysis.get("statistics", {}),
                }
            except Exception as e:
                insights["categories"][category] = {"error": str(e)}

        # 生成整体建议
        prompt = f"""基于以下类别的市场数据，生成今日行动建议：

{json.dumps(insights['categories'], ensure_ascii=False, indent=2)}

返回JSON格式：
{{
    "top_opportunity_today": "今日最佳机会",
    "action_items": ["今日行动1", "行动2", "行动3"],
    "market_alert": "市场提醒（如有）",
    "motivation": "今日激励语"
}}"""

        daily_advice = self.llm.chat_json(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_ETSY_EXPERT,
            temperature=0.7,
        )

        insights["daily_advice"] = daily_advice

        return insights
