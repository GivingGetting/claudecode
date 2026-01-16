# Etsy AI Agent

帮助你在Etsy上销售数字产品赚钱的AI智能体

## 功能特性

- **市场分析** - 发现热门类别、利基市场和趋势
- **产品创意生成** - 基于市场数据生成数字产品创意
- **SEO优化** - 优化标题、描述、标签，提升搜索排名
- **定价策略** - 分析竞品价格，制定最优定价
- **竞品分析** - 深入分析竞争对手，发现差异化机会
- **营销建议** - 获取店铺运营和推广建议

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

复制 `.env.example` 为 `.env` 并填入你的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 使用 Anthropic Claude（推荐）
ANTHROPIC_API_KEY=your_api_key_here

# 或使用 OpenAI
OPENAI_API_KEY=your_api_key_here
AI_PROVIDER=openai
AI_MODEL=gpt-4-turbo
```

### 3. 运行

```bash
python main.py
```

## 命令行使用

### 快速开始指南

```bash
python main.py start
```

获取Etsy数字产品销售入门指南。

### 分析市场

```bash
# 基础分析
python main.py analyze "digital planner"

# 完整综合分析
python main.py analyze "digital planner" --full
```

### 生成产品创意

```bash
python main.py ideas "notion template" --audience "自由职业者" --count 5
```

### SEO优化

```bash
python main.py seo "2024 Digital Planner" --type "digital planner" --desc "A comprehensive digital planner for iPad"
```

### 定价建议

```bash
python main.py price "Premium Notion Dashboard" --type "notion template" --value "All-in-one productivity system"
```

### 竞品分析

```bash
python main.py competitors "canva template" --count 20
```

### 完整产品开发流程

```bash
python main.py develop "wedding invitation template" --audience "准新娘"
```

### 寻找适合你的利基市场

```bash
python main.py niche --interests "设计,摄影,旅行" --skills "Canva,Photoshop"
```

### 对话模式

```bash
python main.py chat
```

与AI助手交互对话，随时提问。

## 编程接口使用

```python
from etsy_agent import EtsyAgent

# 创建智能体
agent = EtsyAgent()

# 快速开始
guide = agent.quick_start()

# 分析市场
analysis = agent.comprehensive_analysis("digital planner")

# 生成产品创意
ideas = agent.product_generator.generate_ideas(
    category="notion template",
    target_audience="学生",
    num_ideas=5
)

# SEO优化
seo = agent.seo_optimizer.optimize_listing(
    product_name="2024 Student Planner",
    product_type="digital planner",
    product_description="完整的学生规划模板"
)

# 定价建议
pricing = agent.pricing_advisor.get_pricing_recommendation(
    product_name="Premium Planner Bundle",
    product_type="digital planner",
    unique_value="10合1规划包"
)

# 竞品分析
competitors = agent.competitor_analyzer.analyze_competitors("svg files")

# 完整产品开发流程
workflow = agent.product_development_workflow(
    niche="wedding template",
    target_audience="准新娘"
)

# 对话
response = agent.chat("如何提高我的Etsy店铺流量？")
```

## 项目结构

```
etsy-ai-agent/
├── main.py                    # 命令行入口
├── requirements.txt           # 依赖列表
├── .env.example              # 环境变量示例
├── README.md                 # 说明文档
└── etsy_agent/
    ├── __init__.py
    ├── agent.py              # 主智能体类
    ├── market_analyzer.py    # 市场分析模块
    ├── product_generator.py  # 产品生成模块
    ├── seo_optimizer.py      # SEO优化模块
    ├── pricing_advisor.py    # 定价顾问模块
    ├── competitor_analyzer.py # 竞品分析模块
    ├── utils/
    │   ├── __init__.py
    │   ├── llm_client.py     # LLM客户端
    │   └── etsy_scraper.py   # Etsy数据抓取
    └── prompts/
        ├── __init__.py
        └── templates.py      # 提示词模板
```

## 推荐数字产品类别

根据市场分析，以下类别适合新手入门：

1. **Notion模板** - 增长迅速，竞争适中
2. **数字规划模板** - 需求稳定，价格区间广
3. **Canva模板** - 制作简单，市场成熟
4. **Excel/Google表格模板** - 技术门槛低
5. **可打印艺术画** - 创意空间大

## 成功秘诀

1. **找准利基** - 不要试图服务所有人
2. **质量优先** - 宁可少而精
3. **持续优化** - 根据数据调整
4. **SEO为王** - 标题和标签是关键
5. **耐心坚持** - Etsy需要时间建立信誉

## 注意事项

- 本工具仅提供市场分析和建议，实际销售结果取决于多种因素
- 请遵守Etsy平台的使用条款和政策
- 确保你销售的数字产品是原创或有合法授权
- API调用可能产生费用，请注意用量

## License

MIT License
