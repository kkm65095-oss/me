# 2_dashboard.py
"""
第二部分：创建可视化仪表板
这个文件从第一步生成的文件中读取数据
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ========== 页面配置 ==========
st.set_page_config(
    page_title="跨境电商大促智能作战室",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com',
        'Report a bug': 'https://www.example.com',
        'About': "跨境电商大促智能作战室 v2.0"
    }
)

# ========== 自定义CSS优化大屏体验 ==========
st.markdown("""
<style>
    /* 大屏优化样式 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* KPI卡片样式 */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .kpi-card h3 {
        font-size: 0.9rem;
        margin-bottom: 8px;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .kpi-card h1 {
        font-size: 1.8rem;
        margin: 5px 0;
        font-weight: bold;
    }
    
    .kpi-card p {
        font-size: 0.8rem;
        margin: 0;
        color: rgba(255, 255, 255, 0.8);
    }
    
    /* 排行榜样式 */
    .ranking-item {
        background: white;
        border-radius: 8px;
        padding: 12px 15px;
        margin: 6px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .ranking-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* 预警指示灯 */
    .alert-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .alert-high { background-color: #ff4757; }
    .alert-medium { background-color: #ffa502; }
    .alert-low { background-color: #2ed573; }
    
    /* 移动端优化 */
    @media (max-width: 768px) {
        .kpi-card {
            height: 120px;
            padding: 10px;
        }
        
        .kpi-card h1 {
            font-size: 1.5rem;
        }
        
        .kpi-card h3 {
            font-size: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ========== 数据加载函数 ==========
@st.cache_data
def load_data_from_files():
    """从第一步生成的文件中加载数据"""
    try:
        print("📂 正在加载数据文件...")
        
        # 加载数据
        df = pd.read_csv('test_sales_data.csv')
        product_df = pd.read_csv('test_product_data.csv')
        ab_df = pd.read_csv('test_ab_data.csv')
        elasticity_df = pd.read_csv('test_elasticity_data.csv')
        
        # 确保日期列是日期类型
        df['date'] = pd.to_datetime(df['date'])
        product_df['date'] = pd.to_datetime(product_df['date'])
        ab_df['date'] = pd.to_datetime(ab_df['date'])
        elasticity_df['date'] = pd.to_datetime(elasticity_df['date'])
        
        print(f"✅ 数据加载完成:")
        print(f"   销售数据: {len(df):,} 行")
        print(f"   产品数据: {len(product_df):,} 行")
        print(f"   A/B测试数据: {len(ab_df):,} 行")
        print(f"   价格弹性数据: {len(elasticity_df):,} 行")
        
        return df, product_df, ab_df, elasticity_df
        
    except FileNotFoundError as e:
        st.error(f"❌ 找不到数据文件: {e}")
        st.info("请先运行第一步的代码生成数据文件")
        return None, None, None, None

# ========== 分析器类 ==========
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
        
        return results

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
            'is_elastic': abs(avg_elasticity) > 1
        }

# ========== 主程序开始 ==========
st.title("🚀 跨境电商春季大促智能作战室")
st.markdown("---")

# 加载数据
with st.spinner("正在加载数据..."):
    df, product_df, ab_df, elasticity_df = load_data_from_files()

if df is None:
    st.stop()

# 初始化分析器
ab_analyzer = ABTestAnalyzer(ab_df)
price_analyzer = PriceElasticityAnalyzer(elasticity_df)

# ========== 侧边栏配置 ==========
with st.sidebar:
    st.title("⚙️ 控制面板")
    
    # 数据信息
    st.header("📊 数据概览")
    st.info(f"数据时间范围: {df['date'].min().date()} 至 {df['date'].max().date()}")
    st.info(f"总数据量: {len(df):,} 条记录")
    
    # 日期筛选
    st.header("📅 日期筛选")
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    date_range = st.date_input(
        "选择日期范围",
        value=(max_date - timedelta(days=7), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 国家筛选
    st.header("🌍 国家筛选")
    all_countries = df['country'].unique().tolist()
    selected_countries = st.multiselect(
        "选择国家",
        options=all_countries,
        default=all_countries[:3]
    )
    
    # 品类筛选
    st.header("📦 品类筛选")
    all_categories = df['category'].unique().tolist()
    selected_categories = st.multiselect(
        "选择品类",
        options=all_categories,
        default=all_categories[:3]
    )
    
    # 显示模式
    st.header("👁️ 显示模式")
    view_mode = st.selectbox("选择显示模式", ["大屏模式", "移动模式", "精简模式"])

# ========== 数据筛选 ==========
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[
        (df['date'].dt.date >= start_date) & 
        (df['date'].dt.date <= end_date) &
        (df['country'].isin(selected_countries if selected_countries else all_countries)) &
        (df['category'].isin(selected_categories if selected_categories else all_categories))
    ]
else:
    filtered_df = df

# ========== 顶部KPI面板 ==========
st.markdown("### 📊 实时监控面板")

# 计算核心指标
latest_date = filtered_df['date'].max()
today_data = filtered_df[filtered_df['date'] == latest_date]
yesterday_data = filtered_df[filtered_df['date'] == latest_date - timedelta(days=1)]

total_sales = today_data['sales_amount'].sum()
total_orders = today_data['orders'].sum()
avg_conversion = today_data['conversion_rate'].mean()
avg_aov = today_data['avg_order_value'].mean()

# 计算增长率
if not yesterday_data.empty:
    sales_growth = ((total_sales - yesterday_data['sales_amount'].sum()) / yesterday_data['sales_amount'].sum() * 100) if yesterday_data['sales_amount'].sum() > 0 else 0
    orders_growth = ((total_orders - yesterday_data['orders'].sum()) / yesterday_data['orders'].sum() * 100) if yesterday_data['orders'].sum() > 0 else 0
else:
    sales_growth = 0
    orders_growth = 0

# 创建KPI卡片
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>💰 今日销售额</h3>
        <h1>¥{total_sales:,.0f}</h1>
        <p>📈 较昨日 {sales_growth:+.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>📦 今日订单数</h3>
        <h1>{total_orders:,}</h1>
        <p>📈 较昨日 {orders_growth:+.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>🔄 转化率</h3>
        <h1>{avg_conversion:.2f}%</h1>
        <p>🎯 行业平均: 3.2%</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='kpi-card'>
        <h3>🎯 平均客单价</h3>
        <h1>¥{avg_aov:.0f}</h1>
        <p>📈 较昨日 +5.2%</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ========== 主分析区域 ==========
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 销量排行", 
    "🔬 A/B测试", 
    "💰 价格分析", 
    "📈 趋势分析",
    "📋 详细数据"
])

# ========== 标签页1: 销量排行 ==========
with tab1:
    st.header("🏆 多维度销量排行系统")
    
    # 排行类型选择
    rank_type = st.radio("选择排行类型", 
                        ["总销量排行", "品类销量排行", "产品销量排行"], 
                        horizontal=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if rank_type == "总销量排行":
            # 国家销量排行
            st.subheader("🌍 国家销量排行")
            country_rank = filtered_df.groupby('country')['sales_amount'].sum().sort_values(ascending=False).reset_index()
            
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
            
        elif rank_type == "品类销量排行":
            # 品类销量排行
            st.subheader("📦 品类销量排行")
            category_rank = filtered_df.groupby('category')['sales_amount'].sum().sort_values(ascending=False).reset_index()
            
            # 使用饼图展示品类分布
            fig_category = px.pie(
                category_rank,
                values='sales_amount',
                names='category',
                title='品类销售额占比',
                hole=0.3
            )
            st.plotly_chart(fig_category, use_container_width=True)
            
        elif rank_type == "产品销量排行":
            # 产品销量排行
            st.subheader("🔥 热销商品排行")
            
            # 获取筛选条件下的产品数据
            filtered_products = product_df[
                (product_df['date'].dt.date >= start_date) & 
                (product_df['date'].dt.date <= end_date) &
                (product_df['country'].isin(selected_countries if selected_countries else all_countries)) &
                (product_df['category'].isin(selected_categories if selected_categories else all_categories))
            ]
            
            product_rank = filtered_products.groupby(['category', 'product'])['sales_amount'].sum().reset_index()
            product_rank = product_rank.sort_values('sales_amount', ascending=False).head(20)
            
            fig_product = px.bar(
                product_rank,
                x='sales_amount',
                y='product',
                color='category',
                orientation='h',
                title='热销商品TOP20',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_product.update_layout(height=500)
            st.plotly_chart(fig_product, use_container_width=True)
    
    with col2:
        st.subheader("🥇 实时排行榜")
        
        if rank_type == "总销量排行":
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
            st.subheader("🔍 品类详情")
            selected_category = st.selectbox(
                "选择品类查看产品排行",
                category_rank['category'].tolist()
            )
            
            if selected_category:
                # 显示该品类下的产品排行
                category_products = product_df[product_df['category'] == selected_category]
                product_rank_cat = category_products.groupby('product')['sales_amount'].sum().sort_values(ascending=False).reset_index()
                
                st.write(f"**{selected_category} 产品排行:**")
                for i, (product, sales) in enumerate(zip(product_rank_cat['product'].head(5), 
                                                        product_rank_cat['sales_amount'].head(5)), 1):
                    st.markdown(f"""
                    <div class='ranking-item'>
                        <strong>{i}. {product}</strong>
                        <span style='float: right; color: #3498db;'>¥{sales:,.0f}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        elif rank_type == "产品销量排行":
            st.subheader("🔍 产品详情")
            if not product_rank.empty:
                selected_product = st.selectbox(
                    "选择产品查看详情",
                    product_rank['product'].head(10).tolist()
                )
                
                if selected_product:
                    product_info = product_df[product_df['product'] == selected_product]
                    if not product_info.empty:
                        avg_price = product_info['price'].mean()
                        total_sales = product_rank[product_rank['product'] == selected_product]['sales_amount'].values[0]
                        
                        st.markdown(f"""
                        <div style='background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <h4>{selected_product}</h4>
                            <p><strong>品类:</strong> {product_info.iloc[0]['category']}</p>
                            <p><strong>平均价格:</strong> ¥{avg_price:.2f}</p>
                            <p><strong>总销量:</strong> ¥{total_sales:,.0f}</p>
                            <p><strong>排名:</strong> #{product_rank[product_rank['product'] == selected_product].index[0] + 1}</p>
                        </div>
                        """, unsafe_allow_html=True)

# ========== 标签页2: A/B测试分析 ==========
with tab2:
    st.header("🔬 A/B测试实验分析")
    
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
                
                # 找出最佳变体
                best_variant = max(results.items(), key=lambda x: x[1]['avg_conversion'])[0]
                best_conversion = results[best_variant]['avg_conversion']
                
                st.success(f"🎉 **推荐变体: {best_variant}**")
                st.info(f"转化率: {best_conversion:.2f}%")

# ========== 标签页3: 价格分析 ==========
with tab3:
    st.header("💰 价格弹性与优化分析")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 产品选择
        st.subheader("📦 选择分析产品")
        
        # 获取热门产品
        top_products = product_df.groupby('product')['sales_amount'].sum().nlargest(10).index.tolist()
        selected_product = st.selectbox("选择产品", top_products)
        
        if selected_product:
            # 分析价格弹性
            analysis = price_analyzer.analyze_product_elasticity(selected_product)
            
            if analysis:
                st.subheader("📊 分析结果")
                
                st.metric(
                    label="平均价格弹性",
                    value=f"{analysis['avg_elasticity']:.2f}",
                    delta="弹性需求" if analysis['is_elastic'] else "非弹性需求"
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

# ========== 标签页4: 趋势分析 ==========
with tab4:
    st.header("📈 销售趋势分析")
    
    # 销售额趋势
    st.subheader("💰 销售额趋势")
    
    daily_sales = filtered_df.groupby('date')['sales_amount'].sum().reset_index()
    
    fig_trend = px.line(
        daily_sales,
        x='date',
        y='sales_amount',
        title='日销售额趋势',
        labels={'sales_amount': '销售额 (¥)', 'date': '日期'},
        line_shape='spline'
    )
    
    fig_trend.update_traces(line=dict(width=3))
    fig_trend.update_layout(
        hovermode='x unified',
        height=400,
        xaxis_title="日期",
        yaxis_title="销售额 (¥)",
        template="plotly_white"
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

# ========== 标签页5: 详细数据 ==========
with tab5:
    st.header("📋 详细数据")
    
    # 数据查看选项
    data_view = st.radio("选择数据视图", ["销售数据", "产品数据", "A/B测试数据"], horizontal=True)
    
    if data_view == "销售数据":
        st.dataframe(filtered_df, use_container_width=True, height=400)
    elif data_view == "产品数据":
        filtered_products = product_df[
            (product_df['date'].dt.date >= start_date) & 
            (product_df['date'].dt.date <= end_date)
        ]
        st.dataframe(filtered_products, use_container_width=True, height=400)
    elif data_view == "A/B测试数据":
        st.dataframe(ab_df, use_container_width=True, height=400)

# ========== 页脚 ==========
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🚀 <strong>跨境电商春季大促智能作战室 v2.0</strong></p>
    <p>📅 数据更新时间: {}</p>
    <p>💡 数据来源: 第一步生成的模拟数据文件</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
