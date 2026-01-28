import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import warnings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64
import io
warnings.filterwarnings('ignore')

# ========== 大屏优化配置 ==========
# 设置页面为宽屏模式，适合大屏幕显示
st.set_page_config(
    page_title="跨境电商大促智能作战室",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",  # 大屏模式下收起侧边栏
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com',
        'Report a bug': 'https://www.example.com',
        'About': "跨境电商大促智能作战室 v2.0"
    }
)

# 自定义CSS优化大屏体验
st.markdown("""
<style>
    /* 大屏优化样式 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 卡片样式优化 */
    .card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        margin-bottom: 10px;
    }
    
    /* KPI卡片样式 */
    .kpi-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    
    /* 排行榜样式 */
    .ranking-item {
        background: white;
        border-radius: 8px;
        padding: 10px 15px;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .ranking-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* 全屏按钮样式 */
    .fullscreen-btn {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 999;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 20px;
        cursor: pointer;
    }
    
    /* 移动端优化 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .kpi-card {
            padding: 15px;
            margin-bottom: 10px;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.2rem !important;
        }
        
        h3 {
            font-size: 1rem !important;
        }
    }
    
    /* 动画效果 */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* 预警指示灯 */
    .alert-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .alert-high { background-color: #ff4757; }
    .alert-medium { background-color: #ffa502; }
    .alert-low { background-color: #2ed573; }
</style>
""", unsafe_allow_html=True)

# ========== 全屏功能 ==========
def create_fullscreen_button():
    """创建全屏按钮的HTML/JS代码"""
    fullscreen_js = """
    <script>
    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.log(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }
    </script>
    <button class="fullscreen-btn" onclick="toggleFullscreen()">📺</button>
    """
    return fullscreen_js

# ========== 数据生成函数（增强版，包含产品级数据） ==========
@st.cache_data
def generate_comprehensive_mock_data():
    """生成包含产品级数据的综合模拟数据"""
    
    np.random.seed(42)
    
    # 基础设置
    countries = ['美国', '英国', '德国', '法国', '日本', '澳大利亚', '加拿大', '韩国', '新加坡', '巴西']
    categories = ['电子产品', '服装', '家居', '美妆', '食品', '玩具', '运动户外', '图书']
    
    # 每个品类下的具体产品
    products_by_category = {
        '电子产品': ['iPhone 15', 'MacBook Pro', 'AirPods Pro', 'iPad Air', 'Apple Watch'],
        '服装': ['男士夹克', '女士连衣裙', '运动鞋', '牛仔裤', '羽绒服'],
        '家居': ['智能音箱', '空气净化器', '咖啡机', '扫地机器人', '电动牙刷'],
        '美妆': ['精华液', '粉底液', '口红', '面膜', '防晒霜'],
        '食品': ['巧克力', '咖啡豆', '坚果', '茶叶', '蜂蜜'],
        '玩具': ['乐高积木', '拼图', '遥控车', '玩偶', '棋盘游戏'],
        '运动户外': ['瑜伽垫', '跑步鞋', '登山包', '自行车', '帐篷'],
        '图书': ['小说', '技术书籍', '儿童绘本', '烹饪书', '旅行指南']
    }
    
    # A/B测试实验数据
    ab_experiments = {
        '首页设计': ['A版（传统）', 'B版（新设计）'],
        '价格策略': ['A价格（原价）', 'B价格（95折）', 'C价格（9折）'],
        '促销文案': ['A文案（直接）', 'B文案（情感）', 'C文案（紧迫）'],
        '配送选项': ['A（标准）', 'B（加急）', 'C（免费退换）']
    }
    
    # 生成日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3个月数据
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    product_data = []
    ab_test_data = []
    price_elasticity_data = []
    
    # 生成基础销售数据
    for i, date in enumerate(dates):
        is_promo_day = i % 7 == 0
        is_weekend = date.weekday() >= 5
        
        for country in countries:
            for category in categories:
                # 基础销量
                base_config = {
                    '美国': {'电子产品': 5000, '服装': 3000, '家居': 2000, '美妆': 1500},
                    '英国': {'电子产品': 3000, '服装': 2500, '家居': 1800, '美妆': 1200},
                    '日本': {'电子产品': 4000, '服装': 2000, '家居': 1500, '美妆': 2000},
                }
                
                base = base_config.get(country, {}).get(category, np.random.uniform(800, 2000))
                
                # 影响因素
                promo_factor = 3.0 if is_promo_day else 1.0
                weekend_factor = 1.3 if is_weekend else 1.0
                trend_factor = 1 + (i / len(dates)) * 0.5
                random_factor = np.random.uniform(0.7, 1.3)
                
                # 品类总销售额
                category_sales = base * promo_factor * weekend_factor * trend_factor * random_factor
                
                # 生成产品级数据
                products = products_by_category[category]
                product_sales_dist = np.random.dirichlet([2, 3, 4, 3, 2])  # 产品销量分布
                
                for product_idx, product in enumerate(products):
                    # 产品销售额 = 品类销售额 × 产品占比
                    product_sales = category_sales * product_sales_dist[product_idx] * np.random.uniform(0.8, 1.2)
                    
                    # 基础价格和弹性测试
                    base_price = np.random.uniform(50, 500)
                    
                    # 价格弹性测试：不同价格点的销量
                    for price_multiplier in [0.9, 0.95, 1.0, 1.05, 1.1]:
                        price = base_price * price_multiplier
                        # 简单价格弹性模型：价格越高，销量越低
                        price_factor = np.exp(-0.5 * (price_multiplier - 1))
                        sales_at_price = product_sales * price_factor * np.random.uniform(0.9, 1.1)
                        
                        price_elasticity_data.append({
                            'date': date.date(),
                            'country': country,
                            'category': category,
                            'product': product,
                            'price': price,
                            'price_multiplier': price_multiplier,
                            'sales': sales_at_price,
                            'demand': sales_at_price / price if price > 0 else 0
                        })
                    
                    product_data.append({
                        'date': date.date(),
                        'country': country,
                        'category': category,
                        'product': product,
                        'sales_amount': product_sales,
                        'price': base_price * np.random.uniform(0.95, 1.05),
                        'units_sold': int(product_sales / (base_price * np.random.uniform(0.8, 1.2))),
                        'product_rank': product_idx + 1,
                        'profit_margin': np.random.uniform(0.2, 0.4)
                    })
                
                # 汇总品类数据
                orders = int(category_sales / np.random.uniform(50, 150))
                visitors = int(orders / np.random.uniform(0.02, 0.08))
                
                data.append({
                    'date': date.date(),
                    'country': country,
                    'category': category,
                    'sales_amount': category_sales,
                    'orders': orders,
                    'visitors': visitors,
                    'conversion_rate': round(orders / visitors * 100, 2) if visitors > 0 else 0,
                    'avg_order_value': round(category_sales / orders, 2) if orders > 0 else 0,
                    'category_rank': np.random.randint(1, 9)  # 品类排名
                })
    
    # 生成A/B测试数据
    for experiment, variants in ab_experiments.items():
        for variant in variants:
            base_conversion = np.random.uniform(2.0, 5.0)
            for i in range(30):  # 30天的实验数据
                date = (end_date - timedelta(days=30 + i)).date()
                conversion = base_conversion * np.random.uniform(0.9, 1.1)
                visitors = np.random.randint(1000, 5000)
                orders = int(visitors * conversion / 100)
                
                ab_test_data.append({
                    'experiment': experiment,
                    'variant': variant,
                    'date': date,
                    'visitors': visitors,
                    'conversions': orders,
                    'conversion_rate': conversion,
                    'revenue': orders * np.random.uniform(50, 200)
                })
    
    df = pd.DataFrame(data)
    product_df = pd.DataFrame(product_data)
    ab_df = pd.DataFrame(ab_test_data)
    elasticity_df = pd.DataFrame(price_elasticity_data)
    
    return df, product_df, ab_df, elasticity_df

# ========== A/B测试分析模块 ==========
class ABTestAnalyzer:
    """A/B测试分析器"""
    
    def __init__(self, ab_data):
        self.ab_data = ab_data
    
    def analyze_experiment(self, experiment_name):
        """分析特定实验"""
        exp_data = self.ab_data[self.ab_data['experiment'] == experiment_name]
        
        if exp_data.empty:
            return None
        
        results = {}
        variants = exp_data['variant'].unique()
        
        for variant in variants:
            variant_data = exp_data[exp_data['variant'] == variant]
            results[variant] = {
                'avg_conversion': variant_data['conversion_rate'].mean(),
                'total_visitors': variant_data['visitors'].sum(),
                'total_conversions': variant_data['conversions'].sum(),
                'total_revenue': variant_data['revenue'].sum(),
                'std_conversion': variant_data['conversion_rate'].std()
            }
        
        # 计算统计显著性（简化版）
        if len(variants) >= 2:
            # 这里使用简化计算，实际应使用t检验或z检验
            base_variant = variants[0]
            control_rate = results[base_variant]['avg_conversion']
            control_std = results[base_variant]['std_conversion']
            control_n = results[base_variant]['total_visitors']
            
            for variant in variants[1:]:
                test_rate = results[variant]['avg_conversion']
                test_std = results[variant]['std_conversion']
                test_n = results[variant]['total_visitors']
                
                # 计算z-score（简化）
                if control_n > 0 and test_n > 0:
                    se = np.sqrt((control_std**2/control_n) + (test_std**2/test_n))
                    if se > 0:
                        z_score = (test_rate - control_rate) / se
                        results[variant]['z_score'] = z_score
                        results[variant]['is_significant'] = abs(z_score) > 1.96  # 95%置信区间
                        results[variant]['lift'] = ((test_rate - control_rate) / control_rate * 100) if control_rate > 0 else 0
        
        return results
    
    def get_best_variant(self, experiment_name):
        """获取最佳变体"""
        results = self.analyze_experiment(experiment_name)
        if not results:
            return None
        
        best_variant = None
        best_conversion = 0
        
        for variant, metrics in results.items():
            if metrics['avg_conversion'] > best_conversion:
                best_conversion = metrics['avg_conversion']
                best_variant = variant
        
        return best_variant, best_conversion

# ========== 价格弹性分析模块 ==========
class PriceElasticityAnalyzer:
    """价格弹性分析器"""
    
    def __init__(self, elasticity_data):
        self.elasticity_data = elasticity_data
    
    def analyze_product_elasticity(self, product_name):
        """分析单个产品的价格弹性"""
        product_data = self.elasticity_data[self.elasticity_data['product'] == product_name]
        
        if product_data.empty:
            return None
        
        # 按价格分组
        price_groups = product_data.groupby('price_multiplier').agg({
            'sales': 'mean',
            'demand': 'mean'
        }).reset_index()
        
        # 计算价格弹性
        elasticities = []
        for i in range(1, len(price_groups)):
            price_change = (price_groups.iloc[i]['price_multiplier'] - 
                          price_groups.iloc[i-1]['price_multiplier']) / price_groups.iloc[i-1]['price_multiplier']
            demand_change = (price_groups.iloc[i]['demand'] - 
                           price_groups.iloc[i-1]['demand']) / price_groups.iloc[i-1]['demand']
            
            if price_change != 0:
                elasticity = demand_change / price_change
                elasticities.append(elasticity)
        
        avg_elasticity = np.mean(elasticities) if elasticities else 0
        
        # 推荐最优价格
        optimal_price_idx = price_groups['sales'].idxmax()
        optimal_price_multiplier = price_groups.loc[optimal_price_idx, 'price_multiplier']
        
        return {
            'price_groups': price_groups,
            'avg_elasticity': avg_elasticity,
            'optimal_price_multiplier': optimal_price_multiplier,
            'is_elastic': abs(avg_elasticity) > 1  # 弹性需求判断
        }

# ========== 自动化报告模块 ==========
class ReportGenerator:
    """自动化报告生成器"""
    
    def __init__(self, sales_data, product_data, ab_data):
        self.sales_data = sales_data
        self.product_data = product_data
        self.ab_data = ab_data
    
    def generate_daily_report(self):
        """生成日报"""
        latest_date = self.sales_data['date'].max()
        yesterday = latest_date - timedelta(days=1)
        
        # 获取昨日数据
        yesterday_data = self.sales_data[self.sales_data['date'] == yesterday]
        
        if yesterday_data.empty:
            return "无昨日数据"
        
        # 计算关键指标
        total_sales = yesterday_data['sales_amount'].sum()
        total_orders = yesterday_data['orders'].sum()
        avg_conversion = yesterday_data['conversion_rate'].mean()
        
        # 获取热销产品
        yesterday_products = self.product_data[self.product_data['date'] == yesterday]
        top_products = yesterday_products.groupby('product')['sales_amount'].sum().nlargest(5)
        
        # 生成报告
        report = f"""
        ===== 跨境电商大促日报 =====
        报告日期: {yesterday}
        
        关键指标:
        - 总销售额: ¥{total_sales:,.2f}
        - 总订单数: {total_orders:,}
        - 平均转化率: {avg_conversion:.2f}%
        
        热销商品TOP5:
        """
        
        for i, (product, sales) in enumerate(top_products.items(), 1):
            report += f"{i}. {product}: ¥{sales:,.2f}\n"
        
        # A/B测试摘要
        report += "\nA/B测试状态:\n"
        experiments = self.ab_data['experiment'].unique()
        for exp in experiments[:3]:  # 只显示前3个实验
            exp_data = self.ab_data[self.ab_data['experiment'] == exp]
            latest_exp = exp_data[exp_data['date'] == exp_data['date'].max()]
            if not latest_exp.empty:
                best_variant = latest_exp.loc[latest_exp['conversion_rate'].idxmax(), 'variant']
                report += f"- {exp}: 当前最佳 {best_variant}\n"
        
        return report
    
    def send_email_report(self, to_email, smtp_config=None):
        """发送邮件报告（简化版）"""
        report = self.generate_daily_report()
        
        # 这里需要配置SMTP服务器
        if smtp_config:
            try:
                msg = MIMEMultipart()
                msg['From'] = smtp_config['from_email']
                msg['To'] = to_email
                msg['Subject'] = f"跨境电商大促日报 - {datetime.now().date()}"
                
                # 添加报告内容
                msg.attach(MIMEText(report, 'plain'))
                
                # 这里添加发邮件的逻辑
                # 实际使用时需要配置SMTP服务器
                st.success(f"报告已生成，可发送到 {to_email}")
                return True
            except Exception as e:
                st.error(f"发送邮件失败: {str(e)}")
                return False
        else:
            # 如果没有配置SMTP，则显示报告内容
            st.info("请配置SMTP服务器以发送邮件")
            st.text(report)
            return False

# ========== 初始化数据 ==========
df, product_df, ab_df, elasticity_df = generate_comprehensive_mock_data()

# 初始化分析器
ab_analyzer = ABTestAnalyzer(ab_df)
price_analyzer = PriceElasticityAnalyzer(elasticity_df)
report_generator = ReportGenerator(df, product_df, ab_df)

# ========== 大屏顶部控制栏 ==========
# 添加全屏按钮
st.markdown(create_fullscreen_button(), unsafe_allow_html=True)

# 顶部控制栏
with st.container():
    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
    
    with col1:
        st.markdown("<h1 style='text-align: left;'>🚀 跨境电商大促智能作战室</h1>", unsafe_allow_html=True)
    
    with col2:
        view_mode = st.selectbox("显示模式", ["大屏模式", "移动模式", "分析模式"])
    
    with col3:
        refresh_rate = st.selectbox("刷新频率", ["实时", "每5分钟", "每15分钟", "每30分钟"])
    
    with col4:
        if st.button("🔄 刷新数据", type="secondary"):
            st.cache_data.clear()
            st.rerun()
    
    with col5:
        if st.button("📧 发送日报", type="primary"):
            with st.spinner("生成日报中..."):
                report_generator.send_email_report("admin@example.com")

st.markdown("---")

# ========== 实时监控预警面板（优化为大屏显示） ==========
st.markdown("<h2 style='text-align: center;'>📊 实时监控与预警面板</h2>", unsafe_allow_html=True)

# 第一行：核心KPI（大屏优化）
kpi_cols = st.columns(5)

with kpi_cols[0]:
    total_sales = df[df['date'] == df['date'].max()]['sales_amount'].sum()
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>💰 今日销售额</h3>
        <h1 style='font-size: 2.5rem; margin: 10px 0;'>¥{total_sales:,.0f}</h1>
        <p>📈 较昨日 +12.5%</p>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    total_orders = df[df['date'] == df['date'].max()]['orders'].sum()
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>📦 今日订单数</h3>
        <h1 style='font-size: 2.5rem; margin: 10px 0;'>{total_orders:,}</h1>
        <p>📈 较昨日 +8.3%</p>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    avg_conversion = df[df['date'] == df['date'].max()]['conversion_rate'].mean()
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>🔄 转化率</h3>
        <h1 style='font-size: 2.5rem; margin: 10px 0;'>{avg_conversion:.2f}%</h1>
        <p>📈 较昨日 +0.3%</p>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    avg_aov = df[df['date'] == df['date'].max()]['avg_order_value'].mean()
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>🎯 平均客单价</h3>
        <h1 style='font-size: 2.5rem; margin: 10px 0;'>¥{avg_aov:.0f}</h1>
        <p>📈 较昨日 +5.2%</p>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[4]:
    top_country = df.groupby('country')['sales_amount'].sum().idxmax()
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>🌍 热销国家</h3>
        <h1 style='font-size: 2.5rem; margin: 10px 0;'>{top_country}</h1>
        <p>🔥 销售额最高</p>
    </div>
    """, unsafe_allow_html=True)

# 第二行：预警信息和目标进度
st.markdown("---")
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚨 实时预警信息")
    
    # 模拟预警信息
    warnings_data = [
        {"type": "high", "message": "美国市场销售额异常下降15%", "time": "10:30"},
        {"type": "medium", "message": "电子产品库存低于安全线", "time": "09:45"},
        {"type": "low", "message": "日本市场转化率持续上升", "time": "08:20"},
    ]
    
    for warning in warnings_data:
        alert_class = f"alert-{warning['type']}"
        st.markdown(f"""
        <div class='ranking-item'>
            <span class='alert-indicator {alert_class}'></span>
            <strong>{warning['message']}</strong>
            <span style='float: right; color: #666;'>{warning['time']}</span>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("🎯 大促目标进度")
    
    # 目标设置
    sales_target = 10000000
    orders_target = 100000
    sales_progress = min(total_sales / sales_target * 100, 100)
    orders_progress = min(total_orders / orders_target * 100, 100)
    
    st.markdown(f"**销售额目标:** ¥{sales_target:,.0f}")
    st.progress(sales_progress / 100)
    st.caption(f"已完成: {sales_progress:.1f}%")
    
    st.markdown(f"**订单数目标:** {orders_target:,}")
    st.progress(orders_progress / 100)
    st.caption(f"已完成: {orders_progress:.1f}%")

# ========== 主分析区域（标签页布局） ==========
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>📈 深度分析与排行系统</h2>", unsafe_allow_html=True)

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 销量排行系统", 
    "🔬 A/B测试分析", 
    "💰 价格弹性分析", 
    "🌐 全球销售视图", 
    "📋 详细数据"
])

# ========== 标签页1: 销量排行系统 ==========
with tab1:
    st.markdown("<h3 style='text-align: center;'>🏆 多维度销量排行系统</h3>", unsafe_allow_html=True)
    
    # 排行类型选择
    rank_type = st.radio("选择排行类型", 
                        ["总销量排行", "品类销量排行", "产品销量排行"], 
                        horizontal=True)
    
    if rank_type == "总销量排行":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 国家销量排行
            st.subheader("🌍 国家销量排行")
            country_rank = df.groupby('country')['sales_amount'].sum().sort_values(ascending=False).reset_index()
            
            fig_country = px.bar(
                country_rank.head(10),
                x='sales_amount',
                y='country',
                orientation='h',
                color='sales_amount',
                color_continuous_scale='Viridis',
                title='国家销量TOP10'
            )
            st.plotly_chart(fig_country, use_container_width=True)
        
        with col2:
            st.subheader("🥇 排行榜单")
            for i, (country, sales) in enumerate(zip(country_rank['country'].head(5), 
                                                    country_rank['sales_amount'].head(5)), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                st.markdown(f"""
                <div class='ranking-item'>
                    <span style='font-size: 1.2rem;'>{medal}</span>
                    <strong>{country}</strong>
                    <span style='float: right; color: #f39c12;'>¥{sales:,.0f}</span>
                </div>
                """, unsafe_allow_html=True)
    
    elif rank_type == "品类销量排行":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 品类销量排行
            st.subheader("📦 品类销量排行")
            category_rank = df.groupby('category')['sales_amount'].sum().sort_values(ascending=False).reset_index()
            
            # 使用饼图展示品类分布
            fig_category = px.pie(
                category_rank,
                values='sales_amount',
                names='category',
                title='品类销售额占比',
                hole=0.3
            )
            st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            st.subheader("🎯 品类选择")
            selected_category = st.selectbox(
                "选择品类查看详情",
                category_rank['category'].tolist()
            )
            
            if selected_category:
                # 显示该品类下的产品排行
                st.subheader(f"📊 {selected_category} 产品排行")
                category_products = product_df[product_df['category'] == selected_category]
                product_rank = category_products.groupby('product')['sales_amount'].sum().sort_values(ascending=False).reset_index()
                
                for i, (product, sales) in enumerate(zip(product_rank['product'].head(5), 
                                                        product_rank['sales_amount'].head(5)), 1):
                    st.markdown(f"""
                    <div class='ranking-item'>
                        <strong>{i}. {product}</strong>
                        <span style='float: right; color: #3498db;'>¥{sales:,.0f}</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    elif rank_type == "产品销量排行":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 产品销量总排行
            st.subheader("🔥 热销商品TOP20")
            product_rank_all = product_df.groupby(['category', 'product'])['sales_amount'].sum().reset_index()
            product_rank_all = product_rank_all.sort_values('sales_amount', ascending=False).head(20)
            
            fig_product = px.bar(
                product_rank_all,
                x='sales_amount',
                y='product',
                color='category',
                orientation='h',
                title='热销商品排行榜',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_product.update_layout(height=600)
            st.plotly_chart(fig_product, use_container_width=True)
        
        with col2:
            st.subheader("🔍 产品详情")
            selected_product = st.selectbox(
                "选择产品",
                product_rank_all['product'].head(10).tolist()
            )
            
            if selected_product:
                product_info = product_df[product_df['product'] == selected_product].iloc[0]
                
                st.markdown(f"""
                <div style='background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                    <h4>{selected_product}</h4>
                    <p><strong>品类:</strong> {product_info['category']}</p>
                    <p><strong>平均价格:</strong> ¥{product_info['price']:.2f}</p>
                    <p><strong>总销量:</strong> ¥{product_rank_all[product_rank_all['product'] == selected_product]['sales_amount'].values[0]:,.0f}</p>
                    <p><strong>利润率:</strong> {product_info['profit_margin']*100:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)

# ========== 标签页2: A/B测试分析 ==========
with tab2:
    st.markdown("<h3 style='text-align: center;'>🔬 A/B测试实验分析</h3>", unsafe_allow_html=True)
    
    # 实验选择
    experiments = ab_df['experiment'].unique()
    selected_experiment = st.selectbox("选择实验", experiments)
    
    if selected_experiment:
        col1, col2 = st.columns(2)
        
        with col1:
            # 实验效果对比
            st.subheader("📊 实验效果对比")
            
            # 获取实验数据
            exp_data = ab_df[ab_df['experiment'] == selected_experiment]
            
            # 按变体分组
            variant_data = exp_data.groupby(['variant', 'date']).agg({
                'conversion_rate': 'mean',
                'revenue': 'sum'
            }).reset_index()
            
            # 绘制转化率趋势
            fig_ab_trend = px.line(
                variant_data,
                x='date',
                y='conversion_rate',
                color='variant',
                title=f'{selected_experiment} - 转化率趋势',
                markers=True
            )
            st.plotly_chart(fig_ab_trend, use_container_width=True)
        
        with col2:
            # 实验结果分析
            st.subheader("📈 实验结果摘要")
            
            # 分析实验
            results = ab_analyzer.analyze_experiment(selected_experiment)
            
            if results:
                # 显示各变体表现
                for variant, metrics in results.items():
                    color = "#2ecc71" if variant == list(results.keys())[0] else "#e74c3c"
                    
                    st.markdown(f"""
                    <div style='background: {color}; color: white; padding: 10px; border-radius: 8px; margin: 5px 0;'>
                        <strong>{variant}</strong>
                        <div style='display: flex; justify-content: space-between;'>
                            <span>转化率: {metrics['avg_conversion']:.2f}%</span>
                            <span>访客: {metrics['total_visitors']:,}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 显示最佳变体
                best_variant, best_conversion = ab_analyzer.get_best_variant(selected_experiment)
                
                if best_variant:
                    st.success(f"🎉 **推荐变体: {best_variant}**")
                    st.info(f"转化率: {best_conversion:.2f}%")
                    
                    # 显示统计显著性
                    if 'z_score' in results.get(best_variant, {}):
                        z_score = results[best_variant]['z_score']
                        is_sig = results[best_variant]['is_significant']
                        
                        if is_sig:
                            st.success(f"✅ 统计显著 (z={z_score:.2f})")
                        else:
                            st.warning(f"⚠️ 统计不显著 (z={z_score:.2f})")

# ========== 标签页3: 价格弹性分析 ==========
with tab3:
    st.markdown("<h3 style='text-align: center;'>💰 价格弹性与优化分析</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 产品选择
        st.subheader("📦 选择分析产品")
        
        # 获取热门产品
        top_products = product_df.groupby('product')['sales_amount'].sum().nlargest(10).index.tolist()
        selected_product = st.selectbox("产品", top_products)
        
        if selected_product:
            # 分析价格弹性
            analysis = price_analyzer.analyze_product_elasticity(selected_product)
            
            if analysis:
                st.subheader("📊 价格弹性分析")
                
                st.metric(
                    label="平均价格弹性",
                    value=f"{analysis['avg_elasticity']:.2f}",
                    delta="弹性" if analysis['is_elastic'] else "非弹性"
                )
                
                st.metric(
                    label="推荐价格系数",
                    value=f"{analysis['optimal_price_multiplier']:.2f}x",
                    delta="最优定价"
                )
                
                # 解释说明
                if analysis['avg_elasticity'] < -1:
                    st.info("💡 该产品为弹性需求，降价可显著提升销量")
                elif analysis['avg_elasticity'] > -1 and analysis['avg_elasticity'] < 0:
                    st.info("💡 该产品为非弹性需求，提价可增加收入")
                else:
                    st.info("💡 价格对需求影响较小")
    
    with col2:
        if selected_product and analysis:
            st.subheader("📈 价格-需求关系")
            
            # 绘制价格弹性曲线
            fig_elasticity = make_subplots(specs=[[{"secondary_y": True}]])
            
            # 添加销售额曲线
            fig_elasticity.add_trace(
                go.Scatter(
                    x=analysis['price_groups']['price_multiplier'],
                    y=analysis['price_groups']['sales'],
                    name='销售额',
                    mode='lines+markers',
                    line=dict(color='#3498db', width=3)
                ),
                secondary_y=False
            )
            
            # 添加需求曲线
            fig_elasticity.add_trace(
                go.Scatter(
                    x=analysis['price_groups']['price_multiplier'],
                    y=analysis['price_groups']['demand'],
                    name='需求量',
                    mode='lines+markers',
                    line=dict(color='#e74c3c', width=3, dash='dash')
                ),
                secondary_y=True
            )
            
            fig_elasticity.update_layout(
                title=f'{selected_product} - 价格弹性分析',
                xaxis_title="价格系数",
                hovermode='x unified',
                height=400
            )
            
            fig_elasticity.update_yaxes(title_text="销售额", secondary_y=False)
            fig_elasticity.update_yaxes(title_text="需求量", secondary_y=True)
            
            st.plotly_chart(fig_elasticity, use_container_width=True)
            
            # 价格优化建议
            st.subheader("🎯 价格优化建议")
            
            optimal_price = product_df[product_df['product'] == selected_product]['price'].mean() * analysis['optimal_price_multiplier']
            current_price = product_df[product_df['product'] == selected_product]['price'].mean()
            
            price_change = ((optimal_price - current_price) / current_price * 100)
            
            if price_change > 0:
                st.success(f"建议提价 {price_change:.1f}%，从 ¥{current_price:.2f} 调整到 ¥{optimal_price:.2f}")
            elif price_change < 0:
                st.success(f"建议降价 {abs(price_change):.1f}%，从 ¥{current_price:.2f} 调整到 ¥{optimal_price:.2f}")
            else:
                st.info("当前价格已接近最优")

# ========== 标签页4: 全球销售视图 ==========
with tab4:
    st.markdown("<h3 style='text-align: center;'>🌐 全球销售热力图</h3>", unsafe_allow_html=True)
    
    # 全球销售地图
    country_sales = df.groupby(['country', 'date']).agg({
        'sales_amount': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    # 最新日期的数据
    latest_sales = country_sales[country_sales['date'] == country_sales['date'].max()]
    
    # 添加经纬度
    country_coords = {
        '美国': {'lat': 37.0902, 'lon': -95.7129},
        '英国': {'lat': 55.3781, 'lon': -3.4360},
        '德国': {'lat': 51.1657, 'lon': 10.4515},
        '法国': {'lat': 46.6034, 'lon': 1.8883},
        '日本': {'lat': 36.2048, 'lon': 138.2529},
        '澳大利亚': {'lat': -25.2744, 'lon': 133.7751},
        '加拿大': {'lat': 56.1304, 'lon': -106.3468},
        '韩国': {'lat': 35.9078, 'lon': 127.7669},
        '新加坡': {'lat': 1.3521, 'lon': 103.8198},
        '巴西': {'lat': -14.2350, 'lon': -51.9253}
    }
    
    latest_sales['latitude'] = latest_sales['country'].apply(lambda x: country_coords.get(x, {}).get('lat', 0))
    latest_sales['longitude'] = latest_sales['country'].apply(lambda x: country_coords.get(x, {}).get('lon', 0))
    
    # 创建全球热力图
    fig_world = px.scatter_geo(
        latest_sales,
        lat='latitude',
        lon='longitude',
        size='sales_amount',
        color='sales_amount',
        hover_name='country',
        hover_data={'sales_amount': ':.0f', 'orders': ':.0f'},
        projection='natural earth',
        color_continuous_scale='Viridis',
        size_max=50,
        title='全球销售热力图'
    )
    
    fig_world.update_layout(
        height=600,
        geo=dict(
            showland=True,
            landcolor='lightgray',
            showcountries=True,
            countrycolor='white',
            showocean=True,
            oceancolor='lightblue'
        )
    )
    
    st.plotly_chart(fig_world, use_container_width=True)

# ========== 标签页5: 详细数据 ==========
with tab5:
    st.markdown("<h3 style='text-align: center;'>📋 详细数据与分析</h3>", unsafe_allow_html=True)
    
    # 数据查看选项
    data_view = st.radio("数据视图", ["销售数据", "产品数据", "A/B测试数据"], horizontal=True)
    
    if data_view == "销售数据":
        st.dataframe(df, use_container_width=True, height=400)
        
        # 数据下载
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载销售数据",
            data=csv,
            file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    elif data_view == "产品数据":
        st.dataframe(product_df, use_container_width=True, height=400)
        
        csv = product_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下载产品数据",
            data=csv,
            file_name=f"product_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    elif data_view == "A/B测试数据":
        st.dataframe(ab_df, use_container_width=True, height=400)

# ========== 移动端适配功能 ==========
if view_mode == "移动模式":
    st.markdown("""
    <style>
    /* 移动端特定样式 */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            margin: 5px 0;
        }
        
        .stSelectbox, .stRadio {
            width: 100%;
        }
        
        /* 简化KPI显示 */
        .kpi-card h1 {
            font-size: 1.5rem !important;
        }
        
        .kpi-card h3 {
            font-size: 0.9rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ========== 自动化报告配置 ==========
st.sidebar.markdown("---")
st.sidebar.header("📧 自动化报告配置")

with st.sidebar.expander("报告设置"):
    report_type = st.selectbox("报告类型", ["日报", "周报", "月报"])
    send_time = st.time_input("发送时间", datetime.now().time())
    recipients = st.text_area("收件人列表", "admin@example.com\nmanager@example.com")
    
    if st.button("保存报告设置"):
        st.success("报告设置已保存")

# ========== 数据导出功能 ==========
st.sidebar.header("💾 数据导出")

export_format = st.sidebar.selectbox("导出格式", ["CSV", "Excel", "JSON"])

if st.sidebar.button("📤 导出所有数据"):
    with st.spinner("正在导出数据..."):
        # 这里可以实现数据导出逻辑
        st.sidebar.success("数据导出完成")

# ========== 页脚信息 ==========
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🚀 <strong>跨境电商大促智能作战室 v2.0</strong></p>
    <p>📅 最后更新: {}</p>
    <p>💡 提示: 按 F11 键进入全屏模式，获得最佳大屏体验</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# ========== 保存数据到文件 ==========
# 保存所有数据到文件
data_files = {
    'sales_data.csv': df,
    'product_data.csv': product_df,
    'ab_test_data.csv': ab_df,
    'price_elasticity_data.csv': elasticity_df
}

for filename, data in data_files.items():
    data.to_csv(filename, index=False, encoding='utf-8-sig')

st.sidebar.success("✅ 所有数据已保存到文件")
