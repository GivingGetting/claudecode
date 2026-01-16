#!/usr/bin/env python3
"""
Etsy AI Agent - 命令行入口
帮助你在Etsy上销售数字产品赚钱的AI智能体
"""

import os
import sys
import json
from typing import Optional

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from etsy_agent import EtsyAgent
from etsy_agent.agent import AgentConfig

# 创建CLI应用
app = typer.Typer(
    name="etsy-agent",
    help="🛍️ Etsy AI 智能体 - 帮助你在Etsy上销售数字产品赚钱",
    add_completion=False,
)

console = Console()

# 全局agent实例
_agent: Optional[EtsyAgent] = None


def get_agent() -> EtsyAgent:
    """获取或创建agent实例"""
    global _agent
    if _agent is None:
        config = AgentConfig(
            ai_provider=os.getenv("AI_PROVIDER", "anthropic"),
            ai_model=os.getenv("AI_MODEL", "claude-sonnet-4-20250514"),
            language=os.getenv("DEFAULT_LANGUAGE", "zh"),
            verbose=True,
        )
        _agent = EtsyAgent(config)
    return _agent


def print_json_result(result: dict, title: str = "结果"):
    """美化打印JSON结果"""
    console.print(Panel(
        json.dumps(result, ensure_ascii=False, indent=2),
        title=title,
        border_style="green",
    ))


def print_welcome():
    """打印欢迎信息"""
    welcome_text = """
# 🛍️ Etsy AI 智能体

欢迎使用 Etsy AI 智能体！我将帮助你：

- 📊 **分析市场** - 发现热门类别和利基机会
- 💡 **生成创意** - 创建独特的数字产品
- 🔍 **优化SEO** - 提升产品搜索排名
- 💰 **制定定价** - 最大化你的收益
- 🎯 **分析竞品** - 了解市场竞争

输入 `etsy-agent --help` 查看所有命令
"""
    console.print(Markdown(welcome_text))


@app.command("start")
def quick_start():
    """
    🚀 快速开始 - 获取Etsy数字产品销售入门指南
    """
    console.print("\n[bold cyan]🚀 生成快速启动指南...[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在分析...", total=None)
        agent = get_agent()
        result = agent.quick_start()
        progress.update(task, completed=True)

    # 显示欢迎信息
    console.print(Panel(
        result.get("welcome_message", "欢迎开始你的Etsy之旅！"),
        title="👋 欢迎",
        border_style="cyan",
    ))

    # 显示入门步骤
    console.print("\n[bold]📝 入门步骤[/bold]\n")
    for step in result.get("getting_started_steps", []):
        console.print(f"[cyan]{step['step']}. {step['title']}[/cyan]")
        console.print(f"   {step['description']}")
        console.print(f"   ⏱️ 预计时间: {step['time_needed']}")
        console.print()

    # 显示推荐类别
    console.print("\n[bold]🎯 新手推荐类别[/bold]\n")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("类别")
    table.add_column("为什么适合新手")
    table.add_column("所需工具")
    table.add_column("收入潜力")

    for cat in result.get("recommended_categories_for_beginners", [])[:5]:
        table.add_row(
            cat.get("category", ""),
            cat.get("why_good_for_beginners", ""),
            ", ".join(cat.get("tools_needed", [])),
            cat.get("potential_income", ""),
        )

    console.print(table)

    # 显示激励语
    console.print(Panel(
        result.get("motivation", "相信自己，开始行动！"),
        title="💪 加油",
        border_style="green",
    ))


@app.command("analyze")
def analyze_market(
    category: str = typer.Argument(..., help="要分析的产品类别，如 'digital planner'"),
    full: bool = typer.Option(False, "--full", "-f", help="进行完整的综合分析"),
):
    """
    📊 分析市场 - 分析特定类别的市场状况和机会
    """
    console.print(f"\n[bold cyan]📊 分析市场: {category}[/bold cyan]\n")

    agent = get_agent()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if full:
            task = progress.add_task("进行综合分析...", total=None)
            result = agent.comprehensive_analysis(category)
        else:
            task = progress.add_task("分析类别...", total=None)
            result = agent.market_analyzer.analyze_category(category)
        progress.update(task, completed=True)

    if full:
        # 显示综合报告摘要
        summary = result.get("summary", {})
        console.print(Panel(
            summary.get("executive_summary", ""),
            title="📋 执行摘要",
            border_style="cyan",
        ))

        # 关键洞察
        console.print("\n[bold]🔍 关键洞察[/bold]\n")
        for insight in summary.get("key_insights", []):
            console.print(f"• {insight['insight']}")
            console.print(f"  [dim]行动: {insight['action']}[/dim]\n")

        # 机会评分
        console.print(f"[bold green]机会评分: {summary.get('opportunity_score', 'N/A')}/10[/bold green]")

    else:
        # 显示简单分析结果
        console.print(Panel(
            result.get("category_overview", "分析完成"),
            title="📊 类别概述",
            border_style="cyan",
        ))

        # 统计数据
        stats = result.get("statistics", {})
        if stats:
            console.print("\n[bold]📈 统计数据[/bold]")
            console.print(f"• 平均价格: ${stats.get('avg_price', 0)}")
            console.print(f"• 价格区间: ${stats.get('min_price', 0)} - ${stats.get('max_price', 0)}")
            console.print(f"• 平均评分: {stats.get('avg_rating', 0)}")
            console.print(f"• 分析产品数: {stats.get('total_products_analyzed', 0)}")

        # 入门建议
        if result.get("recommended_entry_strategy"):
            console.print(Panel(
                result.get("recommended_entry_strategy", ""),
                title="💡 入门策略",
                border_style="green",
            ))


@app.command("ideas")
def generate_ideas(
    category: str = typer.Argument(..., help="产品类别"),
    audience: str = typer.Option("通用", "--audience", "-a", help="目标受众"),
    count: int = typer.Option(5, "--count", "-n", help="生成创意数量"),
):
    """
    💡 生成创意 - 为特定类别生成数字产品创意
    """
    console.print(f"\n[bold cyan]💡 生成产品创意: {category}[/bold cyan]\n")

    agent = get_agent()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("生成创意中...", total=None)
        result = agent.product_generator.generate_ideas(
            category=category,
            target_audience=audience,
            num_ideas=count,
        )
        progress.update(task, completed=True)

    # 显示产品创意
    console.print("\n[bold]🎨 产品创意[/bold]\n")

    for i, idea in enumerate(result.get("product_ideas", []), 1):
        console.print(Panel(
            f"""**{idea.get('name', '未命名')}**

{idea.get('description', '')}

• 目标客户: {idea.get('target_customer', '')}
• 独特卖点: {idea.get('unique_selling_point', '')}
• 建议价格: {idea.get('recommended_price_range', '')}
• 制作难度: {idea.get('difficulty', '')}
• 市场潜力: {idea.get('market_potential', '')}
• 所需工具: {', '.join(idea.get('required_tools', []))}""",
            title=f"创意 {i}",
            border_style="magenta",
        ))

    # 显示捆绑包建议
    bundles = result.get("bundle_ideas", [])
    if bundles:
        console.print("\n[bold]📦 捆绑包建议[/bold]\n")
        for bundle in bundles:
            console.print(f"• {bundle.get('name', '')}")
            console.print(f"  包含: {', '.join(bundle.get('included_products', []))}")


@app.command("seo")
def optimize_seo(
    name: str = typer.Argument(..., help="产品名称"),
    product_type: str = typer.Option(..., "--type", "-t", help="产品类型"),
    description: str = typer.Option("", "--desc", "-d", help="产品描述"),
):
    """
    🔍 SEO优化 - 优化产品标题、标签和描述
    """
    console.print(f"\n[bold cyan]🔍 SEO优化: {name}[/bold cyan]\n")

    agent = get_agent()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("优化SEO...", total=None)
        result = agent.seo_optimizer.optimize_listing(
            product_name=name,
            product_type=product_type,
            product_description=description or f"{name} - {product_type}",
        )
        progress.update(task, completed=True)

    # 显示优化后的标题
    console.print(Panel(
        result.get("optimized_title", ""),
        title="📝 优化后标题",
        border_style="green",
    ))

    # 显示标签
    tags = result.get("tags", [])
    console.print(f"\n[bold]🏷️ 推荐标签 ({len(tags)}/13)[/bold]")
    console.print(" | ".join(tags))

    # 显示关键词
    keywords = result.get("keywords", {})
    console.print("\n[bold]🔑 关键词策略[/bold]")
    console.print(f"• 主要关键词: {', '.join(keywords.get('primary', []))}")
    console.print(f"• 次要关键词: {', '.join(keywords.get('secondary', []))}")
    console.print(f"• 长尾关键词: {', '.join(keywords.get('long_tail', []))}")

    # 显示描述建议
    desc = result.get("description", {})
    if desc:
        console.print(Panel(
            desc.get("opening_hook", ""),
            title="✨ 开头吸引语（前160字符）",
            border_style="cyan",
        ))


@app.command("price")
def pricing_advice(
    name: str = typer.Argument(..., help="产品名称"),
    product_type: str = typer.Option(..., "--type", "-t", help="产品类型"),
    value: str = typer.Option("", "--value", "-v", help="独特价值/卖点"),
):
    """
    💰 定价建议 - 获取最优定价策略
    """
    console.print(f"\n[bold cyan]💰 定价建议: {name}[/bold cyan]\n")

    agent = get_agent()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("分析定价...", total=None)
        result = agent.pricing_advisor.get_pricing_recommendation(
            product_name=name,
            product_type=product_type,
            unique_value=value or "数字产品",
        )
        progress.update(task, completed=True)

    # 显示推荐价格
    price_range = result.get("price_range", {})
    console.print(Panel(
        f"""**推荐价格: ${result.get('recommended_price', 0)}**

价格区间:
• 最低价: ${price_range.get('minimum', 0)}
• 最优价: ${price_range.get('optimal', 0)}
• 最高价: ${price_range.get('maximum', 0)}

{result.get('pricing_rationale', '')}""",
        title="💵 定价建议",
        border_style="green",
    ))

    # 心理定价
    console.print(Panel(
        result.get("psychological_pricing_tip", ""),
        title="🧠 心理定价技巧",
        border_style="cyan",
    ))

    # 促销建议
    sale = result.get("sale_strategy", {})
    if sale:
        console.print("\n[bold]🏷️ 促销策略[/bold]")
        console.print(f"• 常规折扣: {sale.get('regular_sale_discount', '')}")
        console.print(f"• 特殊活动: {sale.get('special_event_discount', '')}")
        console.print(f"• 首购优惠: {sale.get('first_purchase_offer', '')}")


@app.command("competitors")
def analyze_competitors(
    category: str = typer.Argument(..., help="产品类别"),
    count: int = typer.Option(20, "--count", "-n", help="分析数量"),
):
    """
    🎯 竞品分析 - 分析竞争对手和市场机会
    """
    console.print(f"\n[bold cyan]🎯 竞品分析: {category}[/bold cyan]\n")

    agent = get_agent()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("分析竞品...", total=None)
        result = agent.competitor_analyzer.analyze_competitors(category, count)
        progress.update(task, completed=True)

    # 市场概览
    overview = result.get("market_overview", {})
    console.print(Panel(
        f"""分析产品数: {overview.get('total_competitors_analyzed', 0)}
平均价格: ${overview.get('average_price', 0)}
价格区间: {overview.get('price_range', '')}
平均评论数: {overview.get('average_reviews', 0)}""",
        title="📊 市场概览",
        border_style="cyan",
    ))

    # 市场空白
    gaps = result.get("market_gaps", [])
    if gaps:
        console.print("\n[bold]🎯 市场空白机会[/bold]\n")
        for gap in gaps:
            console.print(f"• [bold]{gap.get('gap', '')}[/bold]")
            console.print(f"  {gap.get('opportunity', '')}")
            console.print(f"  [dim]如何填补: {gap.get('how_to_fill', '')}[/dim]\n")

    # 竞争优势
    advantages = result.get("competitive_advantages", [])
    if advantages:
        console.print("\n[bold]💪 可建立的竞争优势[/bold]")
        for adv in advantages:
            console.print(f"• {adv}")


@app.command("develop")
def product_workflow(
    niche: str = typer.Argument(..., help="利基市场/产品类型"),
    audience: str = typer.Option("通用", "--audience", "-a", help="目标受众"),
):
    """
    🛠️ 产品开发 - 完整的产品开发工作流
    """
    console.print(f"\n[bold cyan]🛠️ 产品开发工作流: {niche}[/bold cyan]\n")

    agent = get_agent()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("执行产品开发工作流...", total=None)
        result = agent.product_development_workflow(niche, audience)
        progress.update(task, completed=True)

    # 显示产品创意
    ideas = result.get("ideas", {}).get("product_ideas", [])
    if ideas:
        best_idea = ideas[0]
        console.print(Panel(
            f"""**{best_idea.get('name', '')}**

{best_idea.get('description', '')}

• 独特卖点: {best_idea.get('unique_selling_point', '')}
• 建议价格: {best_idea.get('recommended_price_range', '')}""",
            title="💡 推荐产品创意",
            border_style="magenta",
        ))

    # 显示SEO优化结果
    seo = result.get("seo", {})
    if seo:
        console.print(Panel(
            seo.get("optimized_title", ""),
            title="📝 优化后标题",
            border_style="green",
        ))
        console.print(f"\n🏷️ 标签: {' | '.join(seo.get('tags', []))}")

    # 显示定价建议
    pricing = result.get("pricing", {})
    if pricing:
        console.print(f"\n💰 建议定价: ${pricing.get('recommended_price', 0)}")

    # 显示上架清单
    checklist = result.get("launch_checklist", {}).get("listing_checklist", {})
    if checklist:
        console.print(Panel(
            f"""标题: {checklist.get('title', '')}
定价: {checklist.get('price', '')}
标签: {', '.join(checklist.get('tags', [])[:5])}...
类别: {checklist.get('category_path', '')}""",
            title="📋 上架清单",
            border_style="cyan",
        ))

    # 保存完整结果
    output_file = f"product_development_{niche.replace(' ', '_')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    console.print(f"\n[dim]完整结果已保存至: {output_file}[/dim]")


@app.command("niche")
def find_niche(
    interests: str = typer.Option("", "--interests", "-i", help="你的兴趣（逗号分隔）"),
    skills: str = typer.Option("", "--skills", "-s", help="你的技能（逗号分隔）"),
):
    """
    🧭 找利基 - 帮你找到最适合的利基市场
    """
    console.print("\n[bold cyan]🧭 寻找适合你的利基市场[/bold cyan]\n")

    agent = get_agent()

    interests_list = [i.strip() for i in interests.split(",") if i.strip()] if interests else None
    skills_list = [s.strip() for s in skills.split(",") if s.strip()] if skills else None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("分析最佳利基市场...", total=None)
        result = agent.find_your_niche(interests_list, skills_list)
        progress.update(task, completed=True)

    # 显示分析
    console.print(Panel(
        result.get("analysis", ""),
        title="📊 分析结果",
        border_style="cyan",
    ))

    # 显示推荐利基
    console.print("\n[bold]🎯 推荐利基市场[/bold]\n")

    for niche in result.get("recommended_niches", []):
        match_score = niche.get("match_score", 0)
        score_color = "green" if match_score >= 8 else "yellow" if match_score >= 6 else "red"

        console.print(Panel(
            f"""**匹配度: [{score_color}]{match_score}/10[/{score_color}]**

{niche.get('why_suitable', '')}

• 首个产品创意: {niche.get('first_product_idea', '')}
• 竞争程度: {niche.get('competition_level', '')}
• 收入潜力: {niche.get('income_potential', '')}
• 需补充技能: {niche.get('skill_gap', '无')}""",
            title=niche.get("niche", ""),
            border_style=score_color,
        ))

    # 立即行动
    console.print(Panel(
        result.get("immediate_action", "开始行动吧！"),
        title="⚡ 立即行动",
        border_style="green",
    ))


@app.command("chat")
def interactive_chat():
    """
    💬 对话模式 - 与AI助手交互对话
    """
    console.print("\n[bold cyan]💬 Etsy AI 助手对话模式[/bold cyan]")
    console.print("[dim]输入 'quit' 或 'exit' 退出对话[/dim]\n")

    agent = get_agent()

    while True:
        try:
            user_input = console.input("[bold green]你: [/bold green]")

            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("\n[cyan]再见！祝你在Etsy上成功！🎉[/cyan]\n")
                break

            if not user_input.strip():
                continue

            with console.status("[bold cyan]思考中...[/bold cyan]"):
                response = agent.chat(user_input)

            console.print(f"\n[bold cyan]助手: [/bold cyan]{response}\n")

        except KeyboardInterrupt:
            console.print("\n\n[cyan]再见！🎉[/cyan]\n")
            break


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    🛍️ Etsy AI 智能体 - 帮助你在Etsy上销售数字产品赚钱
    """
    if ctx.invoked_subcommand is None:
        print_welcome()
        console.print("\n[dim]使用 --help 查看所有命令[/dim]\n")


if __name__ == "__main__":
    app()
