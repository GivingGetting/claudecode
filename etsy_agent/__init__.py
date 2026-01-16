"""
Etsy AI Agent - 智能Etsy数字产品销售助手
帮助卖家在Etsy上发现机会、创建产品、优化列表并赚取收入
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .agent import EtsyAgent
from .market_analyzer import MarketAnalyzer
from .product_generator import ProductGenerator
from .seo_optimizer import SEOOptimizer
from .pricing_advisor import PricingAdvisor
from .competitor_analyzer import CompetitorAnalyzer

__all__ = [
    "EtsyAgent",
    "MarketAnalyzer",
    "ProductGenerator",
    "SEOOptimizer",
    "PricingAdvisor",
    "CompetitorAnalyzer",
]
