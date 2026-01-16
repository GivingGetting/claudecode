"""
Etsy Scraper - Etsy网站数据抓取工具
用于获取市场趋势、竞品信息和热门产品数据
"""

import asyncio
import random
import time
from typing import Optional
from dataclasses import dataclass, field
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


@dataclass
class EtsyProduct:
    """Etsy产品数据结构"""

    title: str
    price: float
    currency: str = "USD"
    url: str = ""
    shop_name: str = ""
    rating: float = 0.0
    reviews_count: int = 0
    sales_count: int = 0
    tags: list = field(default_factory=list)
    is_digital: bool = False
    is_bestseller: bool = False
    image_url: str = ""


@dataclass
class EtsyShop:
    """Etsy店铺数据结构"""

    name: str
    url: str = ""
    total_sales: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    products_count: int = 0
    location: str = ""
    since_year: int = 0


class EtsyScraper:
    """Etsy数据抓取器"""

    BASE_URL = "https://www.etsy.com"
    SEARCH_URL = "https://www.etsy.com/search"

    def __init__(self, delay: float = 2.0):
        """
        初始化抓取器

        Args:
            delay: 请求间隔时间（秒）
        """
        self.delay = delay
        self.ua = UserAgent()
        self._last_request_time = 0

    def _get_headers(self) -> dict:
        """获取请求头"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _wait_rate_limit(self):
        """等待速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed + random.uniform(0.5, 1.5))
        self._last_request_time = time.time()

    def search_products(
        self,
        query: str,
        max_results: int = 20,
        digital_only: bool = True,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "most_relevant",
    ) -> list[EtsyProduct]:
        """
        搜索Etsy产品

        Args:
            query: 搜索关键词
            max_results: 最大结果数
            digital_only: 只搜索数字产品
            min_price: 最低价格
            max_price: 最高价格
            sort_by: 排序方式 (most_relevant, lowest_price, highest_price, top_customer_reviews)

        Returns:
            产品列表
        """
        self._wait_rate_limit()

        params = {
            "q": query,
            "ref": "search_bar",
        }

        if digital_only:
            params["item_type"] = "digital"

        if min_price:
            params["min"] = str(min_price)
        if max_price:
            params["max"] = str(max_price)

        sort_map = {
            "most_relevant": "",
            "lowest_price": "price_asc",
            "highest_price": "price_desc",
            "top_customer_reviews": "top_reviews",
        }
        if sort_by in sort_map and sort_map[sort_by]:
            params["order"] = sort_map[sort_by]

        products = []

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    self.SEARCH_URL, params=params, headers=self._get_headers()
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "lxml")
                product_cards = soup.select(
                    "div[data-search-results] li.wt-list-unstyled"
                )[:max_results]

                for card in product_cards:
                    try:
                        product = self._parse_product_card(card)
                        if product:
                            products.append(product)
                    except Exception:
                        continue

        except httpx.HTTPError as e:
            print(f"HTTP请求错误: {e}")
        except Exception as e:
            print(f"抓取错误: {e}")

        return products

    def _parse_product_card(self, card) -> Optional[EtsyProduct]:
        """解析产品卡片HTML"""
        try:
            # 标题
            title_elem = card.select_one("h3")
            if not title_elem:
                title_elem = card.select_one(".v2-listing-card__title")
            title = title_elem.get_text(strip=True) if title_elem else ""

            if not title:
                return None

            # 价格
            price_elem = card.select_one(".currency-value")
            price = 0.0
            if price_elem:
                try:
                    price = float(price_elem.get_text(strip=True).replace(",", ""))
                except ValueError:
                    pass

            # URL
            url_elem = card.select_one("a[href*='/listing/']")
            url = url_elem["href"] if url_elem else ""
            if url and not url.startswith("http"):
                url = self.BASE_URL + url

            # 店铺名
            shop_elem = card.select_one(".v2-listing-card__shop")
            shop_name = shop_elem.get_text(strip=True) if shop_elem else ""

            # 评分和评论数
            rating = 0.0
            reviews_count = 0
            rating_elem = card.select_one("[aria-label*='star']")
            if rating_elem:
                try:
                    rating_text = rating_elem.get("aria-label", "")
                    if "star" in rating_text:
                        rating = float(rating_text.split()[0])
                except (ValueError, IndexError):
                    pass

            reviews_elem = card.select_one(".wt-text-caption")
            if reviews_elem:
                try:
                    reviews_text = reviews_elem.get_text(strip=True)
                    if "(" in reviews_text:
                        reviews_count = int(
                            reviews_text.split("(")[1].split(")")[0].replace(",", "")
                        )
                except (ValueError, IndexError):
                    pass

            # 是否畅销
            is_bestseller = bool(card.select_one(".wt-badge--status-01"))

            # 图片URL
            img_elem = card.select_one("img")
            image_url = img_elem.get("src", "") if img_elem else ""

            return EtsyProduct(
                title=title,
                price=price,
                url=url,
                shop_name=shop_name,
                rating=rating,
                reviews_count=reviews_count,
                is_digital=True,
                is_bestseller=is_bestseller,
                image_url=image_url,
            )

        except Exception:
            return None

    def get_trending_categories(self) -> list[dict]:
        """
        获取热门数字产品类别

        Returns:
            热门类别列表
        """
        # 基于Etsy数字产品市场的热门类别
        trending_categories = [
            {
                "name": "数字规划模板",
                "keywords": ["digital planner", "goodnotes planner", "notability planner"],
                "avg_price_range": (3, 15),
                "competition": "high",
                "trend": "growing",
            },
            {
                "name": "Canva模板",
                "keywords": ["canva template", "social media template", "instagram template"],
                "avg_price_range": (5, 25),
                "competition": "high",
                "trend": "stable",
            },
            {
                "name": "SVG切割文件",
                "keywords": ["svg bundle", "svg files", "cricut svg"],
                "avg_price_range": (2, 10),
                "competition": "very high",
                "trend": "stable",
            },
            {
                "name": "可打印艺术画",
                "keywords": ["printable wall art", "digital download art", "instant download print"],
                "avg_price_range": (3, 20),
                "competition": "high",
                "trend": "growing",
            },
            {
                "name": "Excel/Google表格模板",
                "keywords": ["spreadsheet template", "budget spreadsheet", "excel template"],
                "avg_price_range": (5, 30),
                "competition": "medium",
                "trend": "growing",
            },
            {
                "name": "Notion模板",
                "keywords": ["notion template", "notion planner", "notion dashboard"],
                "avg_price_range": (5, 25),
                "competition": "medium",
                "trend": "rapidly growing",
            },
            {
                "name": "简历模板",
                "keywords": ["resume template", "cv template", "cover letter template"],
                "avg_price_range": (5, 15),
                "competition": "high",
                "trend": "stable",
            },
            {
                "name": "婚礼邀请函模板",
                "keywords": ["wedding invitation template", "wedding suite", "save the date"],
                "avg_price_range": (8, 30),
                "competition": "very high",
                "trend": "stable",
            },
            {
                "name": "电子书模板",
                "keywords": ["ebook template", "lead magnet template", "workbook template"],
                "avg_price_range": (10, 40),
                "competition": "medium",
                "trend": "growing",
            },
            {
                "name": "社交媒体营销素材包",
                "keywords": ["social media kit", "brand kit", "marketing bundle"],
                "avg_price_range": (15, 50),
                "competition": "medium",
                "trend": "growing",
            },
            {
                "name": "Lightroom预设",
                "keywords": ["lightroom presets", "photo presets", "mobile presets"],
                "avg_price_range": (5, 25),
                "competition": "high",
                "trend": "stable",
            },
            {
                "name": "剪贴画和插图",
                "keywords": ["clipart bundle", "digital clipart", "illustration set"],
                "avg_price_range": (3, 15),
                "competition": "high",
                "trend": "stable",
            },
            {
                "name": "3D打印文件",
                "keywords": ["stl files", "3d print file", "3d model"],
                "avg_price_range": (3, 20),
                "competition": "medium",
                "trend": "growing",
            },
            {
                "name": "Procreate笔刷",
                "keywords": ["procreate brushes", "procreate brush set", "ipad brushes"],
                "avg_price_range": (5, 20),
                "competition": "medium",
                "trend": "growing",
            },
            {
                "name": "儿童教育活动",
                "keywords": ["printable activities", "homeschool printable", "kids worksheets"],
                "avg_price_range": (3, 12),
                "competition": "medium",
                "trend": "growing",
            },
        ]

        return trending_categories

    def get_niche_opportunities(self) -> list[dict]:
        """
        获取利基市场机会

        Returns:
            利基机会列表
        """
        niches = [
            {
                "niche": "AI提示词模板",
                "description": "ChatGPT、Midjourney等AI工具的提示词包",
                "potential": "very high",
                "competition": "low",
                "entry_difficulty": "low",
            },
            {
                "niche": "小众运动规划模板",
                "description": "针对特定运动如攀岩、冲浪的训练计划",
                "potential": "medium",
                "competition": "low",
                "entry_difficulty": "medium",
            },
            {
                "niche": "心理健康追踪模板",
                "description": "情绪追踪、冥想日记、治疗笔记模板",
                "potential": "high",
                "competition": "medium",
                "entry_difficulty": "low",
            },
            {
                "niche": "宠物护理规划",
                "description": "宠物健康追踪、训练计划、饮食记录",
                "potential": "medium",
                "competition": "low",
                "entry_difficulty": "low",
            },
            {
                "niche": "自由职业者工具包",
                "description": "合同模板、发票、客户管理表格",
                "potential": "high",
                "competition": "medium",
                "entry_difficulty": "medium",
            },
            {
                "niche": "可持续生活模板",
                "description": "零浪费追踪、碳足迹计算、环保目标规划",
                "potential": "medium",
                "competition": "low",
                "entry_difficulty": "low",
            },
            {
                "niche": "语言学习资源",
                "description": "特定语言的学习卡片、练习册、词汇表",
                "potential": "high",
                "competition": "medium",
                "entry_difficulty": "medium",
            },
            {
                "niche": "家庭财务规划",
                "description": "家庭预算、债务偿还计划、退休规划模板",
                "potential": "high",
                "competition": "medium",
                "entry_difficulty": "low",
            },
        ]

        return niches
