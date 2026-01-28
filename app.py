import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="跨境电商春季大促智能看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题和说明
st.title("🚀 跨境电商春季大促智能分析看板")
st.markdown("---")

# ========== 1. 模拟数据生成函数（增强版） ==========
@st.cache_data
def generate_enhanced_mock_data():
    """生成增强版模拟数据，包含更多维度"""
    
    np.random.seed(42)
    
    # 基础设置
    countries = ['美国', '英国', '德国', '法国', '日本', '澳大利亚', '加拿大', '韩国', '新加坡', '巴西']
    categories = ['电子产品', '服装', '家居', '美妆', '食品', '玩具', '运动户外', '图书']
    channels = ['搜索引擎', '社交媒体', '直接访问', '广告推广', '邮件营销', '联盟营销']
    user_types = ['新用户', '老用户', 'VIP用户']
    
    # 生成日期范围（最近60天，包含历史对比）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    inventory_data = []
    funnel_data = []
    
    # 模拟去年同期数据（用于对比）
    last_year_factor = 0.7  # 假设去年销售额是今年的70%
    
    for i, date in enumerate(dates):
        is_promo_day = i % 7 == 0  # 每周一天模拟大促日
        is_weekend = date.weekday() >= 5
        
        for country in countries:
            for category in categories:
                # 基础销量设置
                base_config = {
                    '美国': {'电子产品': 5000, '服装': 3000, '家居': 2000, '美妆': 1500},
                    '英国': {'电子产品': 3000, '服装': 2500, '家居': 1800, '美妆': 1200},
                    '日本': {'电子产品': 4000, '服装': 2000, '家居': 1500, '美妆': 2000},
                }
                
                # 获取基础值
                if country in base_config and category in base_config[country]:
                    base = base_config[country][category]
                else:
                    base = np.random.uniform(800, 2000)
                
                # 计算影响因素
                promo_factor = 3.0 if is_promo_day else 1.0
                weekend_factor = 1.3 if is_weekend else 1.0
                trend_factor = 1 + (i / len(dates)) * 0.5  # 逐渐增长趋势
                random_factor = np.random.uniform(0.7, 1.3)
                
                # 计算销售额
                sales = base * promo_factor * weekend_factor * trend_factor * random_factor
                
                # 模拟指标
                orders = int(sales / np.random.uniform(50, 150))
                visitors = int(orders / np.random.uniform(0.02, 0.08))
                
                # 用户类型分布
                user_dist = np.random.dirichlet([3, 5, 2])  # 新:老:VIP
                
                # 渠道分布
                channel_dist = np.random.dirichlet([2, 3, 1, 2, 1, 1])
                
                # 漏斗数据
                funnel_stages = ['浏览', '加购', '下单', '支付']
                funnel_values = [
                    visitors,
                    int(visitors * np.random.uniform(0.3, 0.5)),
                    int(visitors * np.random.uniform(0.05, 0.1)),
                    orders
                ]
                
                # 库存数据
                stock_level = np.random.randint(50, 500)
                safety_stock = 100
                
                data.append({
                    'date': date.date(),
                    'country': country,
                    'category': category,
                    'sales_amount': round(sales, 2),
                    'orders': orders,
                    'visitors': visitors,
                    'conversion_rate': round(orders / visitors * 100, 2) if visitors > 0 else 0,
                    'avg_order_value': round(sales / orders, 2) if orders > 0 else 0,
                    'new_users': int(visitors * user_dist[0]),
                    'returning_users': int(visitors * user_dist[1]),
                    'vip_users': int(visitors * user_dist[2]),
                    'channel_search': round(channel_dist[0] * 100, 1),
                    'channel_social': round(channel_dist[1] * 100, 1),
                    'channel_direct': round(channel_dist[2] * 100, 1),
                    'channel_ad': round(channel_dist[3] * 100, 1),
                    'coupon_used': np.random.choice([0, 1], p=[0.6, 0.4]),
                    'coupon_amount': np.random.uniform(5, 50) if np.random.random() > 0.6 else 0
                })
                
                # 库存数据
                inventory_data.append({
                    'date': date.date(),
                    'country': country,
                    'category': category,
                    'stock_level': stock_level,
                    'safety_stock': safety_stock,
                    'needs_replenishment': stock_level < safety_stock,
                    'daily_sales': orders
                })
                
                # 漏斗数据
                for stage, value in zip(funnel_stages, funnel_values):
                    funnel_data.append({
                        'date': date.date(),
                        'country': country,
                        'category': category,
                        'funnel_stage': stage,
                        'value': value
                    })
    
    df = pd.DataFrame(data)
    
    # 添加去年同期数据（模拟）
    df['sales_last_year'] = df['sales_amount'] * last_year_factor * np.random.uniform(0.9, 1.1)
    df['orders_last_year'] = df['orders'] * last_year_factor * np.random.uniform(0.9, 1.1)
    
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
    
    df['latitude'] = df['country'].apply(lambda x: country_coords.get(x, {}).get('lat', 0))
    df['longitude'] = df['country'].apply(lambda x: country_coords.get(x, {}).get('lon', 0))
    
    inventory_df = pd.DataFrame(inventory_data)
    funnel_df = pd.DataFrame(funnel_data)
    
    return df, inventory_df, funnel_df

# ========== 2. 预警系统类 ==========
class AlertSystem:
    """实时监控预警系统"""
    
    def __init__(self, df):
        self.df = df
        self.alerts = []
        
    def check_alerts(self, thresholds=None):
        """检查所有预警规则"""
        if thresholds is None:
            thresholds = {
                'sales_drop': 0.2,  # 销售额下降20%
                'conversion_low': 1.0,  # 转化率低于1%
                'stock_warning': 0.3,  # 库存低于安全库存30%
                'aov_drop': 0.15,  # 客单价下降15%
            }
        
        self.alerts = []
        
        # 检查销售额异常
        latest_sales = self.df[self.df['date'] == self.df['date'].max()]['sales_amount'].mean()
        prev_sales = self.df[self.df['date'] == self.df['date'].max() - timedelta(days=1)]['sales_amount'].mean()
        
        if prev_sales > 0 and (latest_sales - prev_sales) / prev_sales < -thresholds['sales_drop']:
            self.alerts.append({
                'type': 'warning',
                'title': '⚠️ 销售额异常下降',
                'message': f'销售额较昨日下降{(prev_sales - latest_sales)/prev_sales*100:.1f}%',
                'time': datetime.now().strftime('%H:%M'),
                'priority': 'high'
            })
        
        # 检查转化率
        avg_conversion = self.df[self.df['date'] == self.df['date'].max()]['conversion_rate'].mean()
        if avg_conversion < thresholds['conversion_low']:
            self.alerts.append({
                'type': 'danger',
                'title': '🔴 转化率过低',
                'message': f'当前转化率仅{avg_conversion:.2f}%，低于阈值{thresholds["conversion_low"]}%',
                'time': datetime.now().strftime('%H:%M'),
                'priority': 'high'
            })
        
        # 检查库存（简化版）
        low_stock_categories = self.df.groupby('category')['orders'].sum().nlargest(3)
        for cat in low_stock_categories.index:
            self.alerts.append({
                'type': 'info',
                'title': '📦 热销品类库存关注',
                'message': f'{cat}热销中，建议检查库存',
                'time': datetime.now().strftime('%H:%M'),
                'priority': 'medium'
            })
        
        return self.alerts

# ========== 3. 预测模型（简化版） ==========
def generate_predictions(df, days_to_predict=7):
    """生成销售额预测（使用简单移动平均）"""
    
    # 按日期聚合销售额
    daily_sales = df.groupby('date')['sales_amount'].sum().reset_index()
    
    # 使用移动平均生成预测
    predictions = []
    last_date = daily_sales['date'].max()
    
    # 计算7天移动平均作为趋势
    if len(daily_sales) >= 7:
        ma_trend = daily_sales['sales_amount'].rolling(window=7).mean().iloc[-1]
        
        # 生成未来预测（带增长趋势）
        for i in range(1, days_to_predict + 1):
            pred_date = last_date + timedelta(days=i)
            # 基础预测 + 轻微增长 + 随机波动
            pred_value = ma_trend * (1 + 0.02 * i) * np.random.uniform(0.95, 1.05)
            
            predictions.append({
                'date': pred_date,
                'sales_amount': pred_value,
                'is_prediction': True
            })
    
    # 准备历史+预测数据
    historical = daily_sales.copy()
    historical['is_prediction'] = False
    
    if predictions:
        pred_df = pd.DataFrame(predictions)
        full_data = pd.concat([historical, pred_df], ignore_index=True)
    else:
        full_data = historical
    
    return full_data

# ========== 4. 初始化数据 ==========
df, inventory_df, funnel_df = generate_enhanced_mock_data()
alert_system = AlertSystem(df)

# 保存数据到文件
data_path = "spring_promo_enhanced_data.csv"
df.to_csv(data_path, index=False, encoding='utf-8-sig')

# ========== 5. 侧边栏配置 ==========
with st.sidebar:
    st.title("⚙️ 控制面板")
    
    # 预警设置
    st.header("🔔 预警设置")
    sales_drop_threshold = st.slider("销售额下降阈值(%)", 10, 50, 20)
    conversion_threshold = st.slider("转化率低阈值(%)", 0.5, 5.0, 1.0)
    
    # 目标设置
    st.header("🎯 大促目标设置")
    sales_target = st.number_input("销售额目标(¥)", value=5000000, step=100000)
    orders_target = st.number_input("订单数目标", value=50000, step=1000)
    
    # 日期范围选择
    st.header("📅 日期筛选")
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.date_input(
        "选择日期范围",
        value=(max_date - timedelta(days=14), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 国家选择
    st.header("🌍 国家筛选")
    all_countries = df['country'].unique().tolist()
    selected_countries = st.multiselect(
        "选择国家",
        options=all_countries,
        default=all_countries[:3]
    )
    
    # 品类选择
    st.header("📦 品类筛选")
    all_categories = df['category'].unique().tolist()
    selected_categories = st.multiselect(
        "选择品类",
        options=all_categories,
        default=all_categories[:3]
    )
    
    # 生成报告按钮
    st.header("📋 报告工具")
    if st.button("📄 生成分析报告"):
        st.success("报告生成中...")
        # 这里可以添加报告生成逻辑

# ========== 6. 数据筛选 ==========
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[
        (df['date'] >= start_date) & 
        (df['date'] <= end_date) &
        (df['country'].isin(selected_countries if selected_countries else all_countries)) &
        (df['category'].isin(selected_categories if selected_categories else all_categories))
    ]
else:
    filtered_df = df

# ========== 7. 顶部KPI面板（增强版） ==========
st.header("📈 实时监控面板")

# 计算核心指标
total_sales = filtered_df['sales_amount'].sum()
total_orders = filtered_df['orders'].sum()
avg_conversion = filtered_df['conversion_rate'].mean()
avg_aov = filtered_df['avg_order_value'].mean()

# 计算同比
current_period_sales = filtered_df[filtered_df['date'] >= max_date - timedelta(days=7)]['sales_amount'].sum()
last_period_sales = filtered_df[
    (filtered_df['date'] >= max_date - timedelta(days=14)) & 
    (filtered_df['date'] < max_date - timedelta(days=7))
]['sales_amount'].sum()
week_over_week = ((current_period_sales - last_period_sales) / last_period_sales * 100) if last_period_sales > 0 else 0

# 计算目标完成率
sales_completion = min(total_sales / sales_target * 100, 100) if sales_target > 0 else 0
orders_completion = min(total_orders / orders_target * 100, 100) if orders_target > 0 else 0

# 预警检查
thresholds = {
    'sales_drop': sales_drop_threshold / 100,
    'conversion_low': conversion_threshold
}
alerts = alert_system.check_alerts(thresholds)

# 第一行：核心KPI
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    # 添加预警指示器
    alert_icon = "🔴" if any(a['priority'] == 'high' for a in alerts) else "🟢"
    st.metric(
        label=f"总销售额 {alert_icon}",
        value=f"¥{total_sales:,.0f}",
        delta=f"目标: {sales_completion:.1f}%",
        delta_color="normal" if sales_completion >= 70 else "inverse"
    )

with col2:
    st.metric(
        label="总订单数",
        value=f"{total_orders:,}",
        delta=f"目标: {orders_completion:.1f}%",
        delta_color="normal" if orders_completion >= 70 else "inverse"
    )

with col3:
    conversion_icon = "⚠️" if avg_conversion < conversion_threshold else "✅"
    st.metric(
        label=f"平均转化率 {conversion_icon}",
        value=f"{avg_conversion:.2f}%",
        delta=f"{week_over_week:+.1f}% WoW",
        delta_color="normal" if avg_conversion >= conversion_threshold else "inverse"
    )

with col4:
    st.metric(
        label="平均客单价",
        value=f"¥{avg_aov:.0f}",
        delta="+5.2%"
    )

with col5:
    # 新用户占比
    total_users = filtered_df['new_users'].sum() + filtered_df['returning_users'].sum()
    new_user_ratio = filtered_df['new_users'].sum() / total_users * 100 if total_users > 0 else 0
    st.metric(
        label="新用户占比",
        value=f"{new_user_ratio:.1f}%",
        delta="+2.3%"
    )

# 第二行：目标进度条和预警面板
st.subheader("🎯 目标进度跟踪")

col1, col2 = st.columns(2)

with col1:
    # 销售额目标进度
    st.progress(sales_completion / 100)
    st.caption(f"销售额目标完成度: {sales_completion:.1f}% (¥{total_sales:,.0f} / ¥{sales_target:,.0f})")

with col2:
    # 订单数目标进度
    st.progress(orders_completion / 100)
    st.caption(f"订单数目标完成度: {orders_completion:.1f}% ({total_orders:,} / {orders_target:,})")

# 预警面板
if alerts:
    st.subheader("🚨 实时预警")
    
    high_alerts = [a for a in alerts if a['priority'] == 'high']
    medium_alerts = [a for a in alerts if a['priority'] == 'medium']
    
    if high_alerts:
        for alert in high_alerts:
            st.error(f"**{alert['title']}** - {alert['message']} ({alert['time']})")
    
    if medium_alerts:
        for alert in medium_alerts:
            st.warning(f"**{alert['title']}** - {alert['message']} ({alert['time']})")

st.markdown("---")

# ========== 8. 主标签页区域 ==========
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 销售趋势与预测", 
    "🌍 全球分布", 
    "👥 用户行为", 
    "📦 库存管理", 
    "🎯 营销效果", 
    "📊 品类分析",
    "📋 详细数据"
])

# ========== 标签页1: 销售趋势与预测 ==========
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 销售额趋势与预测")
        
        # 生成预测数据
        pred_data = generate_predictions(filtered_df, days_to_predict=7)
        
        # 创建趋势图
        fig_trend = go.Figure()
        
        # 历史数据
        historical = pred_data[~pred_data['is_prediction']]
        fig_trend.add_trace(go.Scatter(
            x=historical['date'],
            y=historical['sales_amount'],
            mode='lines+markers',
            name='实际销售额',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6)
        ))
        
        # 预测数据
        if any(pred_data['is_prediction']):
            predictions = pred_data[pred_data['is_prediction']]
            fig_trend.add_trace(go.Scatter(
                x=predictions['date'],
                y=predictions['sales_amount'],
                mode='lines+markers',
                name='预测销售额',
                line=dict(color='#ff7f0e', width=3, dash='dash'),
                marker=dict(size=6, symbol='diamond')
            ))
            
            # 添加预测区间（置信带）
            fig_trend.add_trace(go.Scatter(
                x=list(predictions['date']) + list(predictions['date'][::-1]),
                y=list(predictions['sales_amount'] * 1.1) + list(predictions['sales_amount'] * 0.9)[::-1],
                fill='toself',
                fillcolor='rgba(255, 127, 14, 0.2)',
                line=dict(color='rgba(255, 127, 14, 0)'),
                name='预测区间',
                showlegend=True
            ))
        
        fig_trend.update_layout(
            title='销售额趋势与7日预测',
            xaxis_title="日期",
            yaxis_title="销售额 (¥)",
            hovermode='x unified',
            height=500,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        st.subheader("📊 同比环比分析")
        
        # 计算各类对比
        current_week = filtered_df[filtered_df['date'] >= max_date - timedelta(days=7)]
        last_week = filtered_df[
            (filtered_df['date'] >= max_date - timedelta(days=14)) & 
            (filtered_df['date'] < max_date - timedelta(days=7))
        ]
        
        metrics = [
            ("本周销售额", "上周销售额", current_week['sales_amount'].sum(), last_week['sales_amount'].sum()),
            ("本周订单数", "上周订单数", current_week['orders'].sum(), last_week['orders'].sum()),
            ("本周转化率", "上周转化率", current_week['conversion_rate'].mean(), last_week['conversion_rate'].mean()),
            ("本周客单价", "上周客单价", current_week['avg_order_value'].mean(), last_week['avg_order_value'].mean()),
        ]
        
        for current_label, last_label, current_val, last_val in metrics:
            if last_val > 0:
                change = (current_val - last_val) / last_val * 100
                st.metric(
                    label=current_label,
                    value=f"{current_val:,.0f}" if isinstance(current_val, (int, float)) and current_val > 100 else f"{current_val:.2f}",
                    delta=f"{change:+.1f}%",
                    delta_color="normal" if change >= 0 else "inverse"
                )
        
        # 同比分析（简化）
        st.subheader("📅 同比分析")
        st.info("""
        **去年同期对比:**
        - 销售额: +32.5% ↑
        - 订单数: +28.1% ↑  
        - 转化率: +1.2% ↑
        - 新用户: +45.3% ↑
        """)

# ========== 标签页2: 全球分布 ==========
with tab2:
    st.subheader("🌍 全球销售额分布")
    
    # 按国家聚合
    country_sales = filtered_df.groupby(['country', 'latitude', 'longitude']).agg({
        'sales_amount': 'sum',
        'orders': 'sum',
        'conversion_rate': 'mean'
    }).reset_index()
    
    # 气泡地图
    fig_map = px.scatter_geo(
        country_sales,
        lat='latitude',
        lon='longitude',
        size='sales_amount',
        color='sales_amount',
        hover_name='country',
        hover_data={
            'sales_amount': ':.0f',
            'orders': ':.0f',
            'conversion_rate': ':.2f',
            'latitude': False,
            'longitude': False
        },
        title='全球销售额分布热力图',
        projection='natural earth',
        color_continuous_scale='Viridis',
        size_max=40
    )
    
    fig_map.update_layout(
        height=500,
        geo=dict(
            showland=True,
            landcolor='lightgray',
            showcountries=True,
            countrycolor='white',
            showocean=True,
            oceancolor='lightblue'
        ),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # 国家排名和时区热力
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 国家销售额排名")
        
        country_rank = country_sales.sort_values('sales_amount', ascending=True)
        
        fig_bar = px.bar(
            country_rank,
            y='country',
            x='sales_amount',
            orientation='h',
            color='sales_amount',
            text='sales_amount',
            color_continuous_scale='Blues'
        )
        
        fig_bar.update_traces(
            texttemplate='¥%{text:,.0f}',
            textposition='outside'
        )
        
        fig_bar.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="销售额 (¥)",
            yaxis_title="",
            template="plotly_white"
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("🕒 时区销售热度")
        
        # 模拟时区数据
        timezones = ['GMT-5', 'GMT+0', 'GMT+1', 'GMT+8', 'GMT+9']
        sales_by_tz = {tz: np.random.randint(50000, 200000) for tz in timezones}
        
        tz_df = pd.DataFrame({
            'timezone': list(sales_by_tz.keys()),
            'sales': list(sales_by_tz.values()),
            'peak_hour': ['14:00-16:00', '10:00-12:00', '11:00-13:00', '20:00-22:00', '21:00-23:00']
        })
        
        fig_tz = px.bar(
            tz_df,
            x='timezone',
            y='sales',
            color='sales',
            text='sales',
            hover_data=['peak_hour']
        )
        
        fig_tz.update_traces(
            texttemplate='¥%{text:,.0f}',
            textposition='outside'
        )
        
        fig_tz.update_layout(
            height=400,
            title="各时区销售额分布",
            xaxis_title="时区",
            yaxis_title="销售额 (¥)",
            template="plotly_white"
        )
        
        st.plotly_chart(fig_tz, use_container_width=True)

# ========== 标签页3: 用户行为分析 ==========
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 用户类型分布")
        
        # 用户类型数据
        user_data = {
            'type': ['新用户', '老用户', 'VIP用户'],
            'count': [
                filtered_df['new_users'].sum(),
                filtered_df['returning_users'].sum(),
                filtered_df['vip_users'].sum()
            ]
        }
        
        user_df = pd.DataFrame(user_data)
        
        fig_users = px.pie(
            user_df,
            values='count',
            names='type',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        fig_users.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>%{value:,} 用户<br>占比: %{percent}'
        )
        
        fig_users.update_layout(
            height=400,
            title="用户类型分布"
        )
        
        st.plotly_chart(fig_users, use_container_width=True)
    
    with col2:
        st.subheader("🔄 用户转化漏斗")
        
        # 漏斗数据
        funnel_summary = funnel_df.groupby('funnel_stage')['value'].sum().reset_index()
        
        # 确保正确的顺序
        stage_order = ['浏览', '加购', '下单', '支付']
        funnel_summary['funnel_stage'] = pd.Categorical(
            funnel_summary['funnel_stage'], 
            categories=stage_order, 
            ordered=True
        )
        funnel_summary = funnel_summary.sort_values('funnel_stage')
        
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_summary['funnel_stage'],
            x=funnel_summary['value'],
            textinfo="value+percent initial",
            marker=dict(color=['#636efa', '#ef553b', '#00cc96', '#ab63fa'])
        ))
        
        fig_funnel.update_layout(
            height=400,
            title="用户转化漏斗分析",
            showlegend=False
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    # 购买时段分析
    st.subheader("🕒 购买时段热力图")
    
    # 模拟购买时段数据
    hours = list(range(24))
    days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    # 生成模拟数据
    heat_data = []
    for day_idx, day in enumerate(days):
        for hour in hours:
            # 工作日和周末有不同模式
            if day_idx < 5:  # 工作日
                base = 100
                peak_hours = [12, 13, 18, 19, 20]
            else:  # 周末
                base = 150
                peak_hours = [11, 12, 13, 14, 15, 20, 21]
            
            if hour in peak_hours:
                sales = base * np.random.uniform(2, 3)
            else:
                sales = base * np.random.uniform(0.3, 0.8)
            
            heat_data.append({
                'day': day,
                'hour': hour,
                'sales': sales
            })
    
    heat_df = pd.DataFrame(heat_data)
    
    # 创建热力图
    fig_heat = px.density_heatmap(
        heat_df,
        x='hour',
        y='day',
        z='sales',
        color_continuous_scale='YlOrRd',
        nbinsx=24,
        nbinsy=7
    )
    
    fig_heat.update_layout(
        height=400,
        title="一周购买时段热力图",
        xaxis_title="小时",
        yaxis_title="星期",
        xaxis=dict(tickmode='linear', dtick=2)
    )
    
    st.plotly_chart(fig_heat, use_container_width=True)

# ========== 标签页4: 库存管理 ==========
with tab4:
    st.subheader("📦 库存状态监控")
    
    # 库存预警分析
    inventory_status = inventory_df.groupby(['country', 'category']).agg({
        'stock_level': 'mean',
        'safety_stock': 'mean',
        'needs_replenishment': 'sum',
        'daily_sales': 'mean'
    }).reset_index()
    
    # 计算库存周转天数
    inventory_status['days_of_stock'] = inventory_status['stock_level'] / inventory_status['daily_sales']
    inventory_status['stock_ratio'] = inventory_status['stock_level'] / inventory_status['safety_stock']
    
    # 标记需要补货的商品
    inventory_status['status'] = np.where(
        inventory_status['stock_ratio'] < 1,
        '急需补货',
        np.where(inventory_status['stock_ratio'] < 1.5, '需要关注', '库存充足')
    )
    
    # 库存状态表格
    st.dataframe(
        inventory_status.sort_values('stock_ratio'),
        column_config={
            "country": "国家",
            "category": "品类",
            "stock_level": st.column_config.NumberColumn("库存量", format="%d"),
            "safety_stock": st.column_config.NumberColumn("安全库存", format="%d"),
            "days_of_stock": st.column_config.NumberColumn("库存天数", format="%.1f 天"),
            "stock_ratio": st.column_config.NumberColumn("库存比例", format="%.2f"),
            "status": st.column_config.TextColumn("状态")
        },
        use_container_width=True,
        height=400
    )
    
    # 库存可视化
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 库存充足度分析")
        
        status_counts = inventory_status['status'].value_counts()
        
        fig_stock_status = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            color=status_counts.index,
            color_discrete_map={
                '库存充足': '#00cc96',
                '需要关注': '#ffa15a',
                '急需补货': '#ef553b'
            },
            text=status_counts.values
        )
        
        fig_stock_status.update_traces(
            texttemplate='%{text} 个SKU',
            textposition='outside'
        )
        
        fig_stock_status.update_layout(
            height=300,
            title="库存状态分布",
            xaxis_title="状态",
            yaxis_title="SKU数量",
            showlegend=False
        )
        
        st.plotly_chart(fig_stock_status, use_container_width=True)
    
    with col2:
        st.subheader("🔄 补货建议")
        
        # 生成补货建议
        replenishment_needed = inventory_status[
            inventory_status['status'].isin(['急需补货', '需要关注'])
        ].sort_values('stock_ratio')
        
        if not replenishment_needed.empty:
            st.warning("**建议立即补货的商品:**")
            for _, row in replenishment_needed.head(5).iterrows():
                st.write(f"- **{row['category']}** ({row['country']}): 库存 {row['stock_level']:.0f}, 安全库存 {row['safety_stock']:.0f}, 剩余天数 {row['days_of_stock']:.1f}")
        else:
            st.success("✅ 所有商品库存充足")

# ========== 标签页5: 营销效果 ==========
with tab5:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📢 渠道效果分析")
        
        # 渠道数据
        channel_data = {
            'channel': ['搜索引擎', '社交媒体', '直接访问', '广告推广', '邮件营销', '联盟营销'],
            'traffic': [35, 25, 15, 12, 8, 5],  # 流量占比
            'conversion': [3.2, 2.8, 4.1, 2.5, 3.5, 2.2],  # 转化率
            'roi': [4.2, 3.8, 5.1, 2.9, 4.5, 3.1]  # ROI
        }
        
        channel_df = pd.DataFrame(channel_data)
        
        fig_channels = go.Figure()
        
        fig_channels.add_trace(go.Bar(
            x=channel_df['channel'],
            y=channel_df['traffic'],
            name='流量占比(%)',
            marker_color='lightblue'
        ))
        
        fig_channels.add_trace(go.Scatter(
            x=channel_df['channel'],
            y=channel_df['roi'],
            name='ROI',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='red', width=3)
        ))
        
        fig_channels.update_layout(
            title="渠道效果分析",
            yaxis=dict(title='流量占比(%)'),
            yaxis2=dict(
                title='ROI',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=400,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_channels, use_container_width=True)
    
    with col2:
        st.subheader("🎫 优惠券使用情况")
        
        # 优惠券数据
        coupon_data = filtered_df.groupby('date').agg({
            'coupon_used': 'sum',
            'coupon_amount': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        coupon_data['coupon_usage_rate'] = coupon_data['coupon_used'] / coupon_data['orders'] * 100
        
        fig_coupon = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_coupon.add_trace(
            go.Bar(
                x=coupon_data['date'],
                y=coupon_data['coupon_used'],
                name='优惠券使用数',
                marker_color='lightgreen'
            ),
            secondary_y=False
        )
        
        fig_coupon.add_trace(
            go.Scatter(
                x=coupon_data['date'],
                y=coupon_data['coupon_usage_rate'],
                name='使用率(%)',
                line=dict(color='orange', width=3)
            ),
            secondary_y=True
        )
        
        fig_coupon.update_layout(
            title="优惠券使用趋势",
            hovermode='x unified',
            height=400,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig_coupon.update_yaxes(title_text="使用数量", secondary_y=False)
        fig_coupon.update_yaxes(title_text="使用率(%)", secondary_y=True)
        
        st.plotly_chart(fig_coupon, use_container_width=True)
    
    # 营销ROI总结
    st.subheader("💰 营销投入产出总结")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="总营销投入",
            value="¥125,000",
            delta="+15.2%"
        )
    
    with col2:
        st.metric(
            label="营销带来GMV",
            value="¥625,000",
            delta="+22.3%"
        )
    
    with col3:
        st.metric(
            label="整体ROI",
            value="5.0",
            delta="+0.3"
        )

# ========== 标签页6: 品类分析 ==========
with tab6:
    st.subheader("📊 品类销售分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 品类销售额占比
        category_sales = filtered_df.groupby('category')['sales_amount'].sum().reset_index()
        
        fig_pie = px.pie(
            category_sales,
            values='sales_amount',
            names='category',
            title='品类销售额占比',
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>¥%{value:,.0f}<br>占比: %{percent}'
        )
        
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # 品类增长率对比
        # 计算最近7天 vs 前7天的增长
        recent_date = filtered_df['date'].max()
        
        recent_week = filtered_df[filtered_df['date'] >= recent_date - timedelta(days=7)]
        previous_week = filtered_df[
            (filtered_df['date'] >= recent_date - timedelta(days=14)) & 
            (filtered_df['date'] < recent_date - timedelta(days=7))
        ]
        
        recent_by_cat = recent_week.groupby('category')['sales_amount'].sum()
        previous_by_cat = previous_week.groupby('category')['sales_amount'].sum()
        
        growth_data = []
        for cat in recent_by_cat.index:
            if cat in previous_by_cat and previous_by_cat[cat] > 0:
                growth = (recent_by_cat[cat] - previous_by_cat[cat]) / previous_by_cat[cat] * 100
                growth_data.append({
                    'category': cat,
                    'growth_rate': growth,
                    'recent_sales': recent_by_cat[cat]
                })
        
        growth_df = pd.DataFrame(growth_data)
        
        if not growth_df.empty:
            fig_growth = px.bar(
                growth_df.sort_values('growth_rate'),
                y='category',
                x='growth_rate',
                orientation='h',
                color='growth_rate',
                color_continuous_scale='RdYlGn',
                text='growth_rate',
                title='品类增长率对比 (%)'
            )
            
            fig_growth.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            
            fig_growth.update_layout(
                height=400,
                xaxis_title="增长率 (%)",
                yaxis_title="品类",
                showlegend=False
            )
            
            st.plotly_chart(fig_growth, use_container_width=True)

# ========== 标签页7: 详细数据 ==========
with tab7:
    st.subheader("📋 详细数据表")
    
    # 显示数据预览
    st.dataframe(
        filtered_df.sort_values(['date', 'country', 'category']),
        use_container_width=True,
        height=400
    )
    
    # 数据统计摘要
    st.subheader("📊 数据统计摘要")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**按国家汇总:**")
        country_summary = filtered_df.groupby('country').agg({
            'sales_amount': ['sum', 'mean', 'count'],
            'orders': 'sum',
            'conversion_rate': 'mean'
        }).round(2)
        st.dataframe(country_summary, use_container_width=True)
    
    with col2:
        st.write("**按品类汇总:**")
        category_summary = filtered_df.groupby('category').agg({
            'sales_amount': ['sum', 'mean', 'count'],
            'conversion_rate': 'mean',
            'avg_order_value': 'mean'
        }).round(2)
        st.dataframe(category_summary, use_container_width=True)

# ========== 9. 底部信息 ==========
st.markdown("---")
st.markdown("### 📊 数据说明")
st.markdown("""
- **数据来源**: 模拟生成的跨境电商春季大促数据
- **时间范围**: 最近60天，包含模拟的大促高峰期
- **更新频率**: 实时更新（演示为静态数据）
- **货币单位**: 人民币 (¥)
- **数据保存**: 所有数据已保存到 `spring_promo_enhanced_data.csv`
""")

st.markdown("### 🚀 操作指南")
st.markdown("""
1. **侧边栏控制**: 设置预警阈值、目标、筛选条件
2. **预警监控**: 顶部KPI面板显示实时预警状态
3. **趋势预测**: 销售趋势图包含未来7天预测
4. **多维分析**: 使用标签页切换不同分析维度
5. **数据导出**: 侧边栏提供数据下载功能
""")

# ========== 10. 数据下载选项 ==========
st.sidebar.markdown("---")
st.sidebar.header("💾 数据导出")

# 提供数据下载
csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button(
    label="📥 下载筛选后数据 (CSV)",
    data=csv_data,
    file_name=f"spring_promo_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

# 一键生成报告按钮
if st.sidebar.button("📄 一键生成分析报告", type="primary"):
    with st.spinner("正在生成分析报告..."):
        # 模拟报告生成
        st.sidebar.success("报告生成完成！")
        st.sidebar.info("""
        **报告摘要:**
        - 销售额: ¥{:,}
        - 订单数: {:,}
        - 转化率: {:.2f}%
        - 关键发现: 欧美市场增长强劲，电子产品品类表现突出
        """.format(int(total_sales), total_orders, avg_conversion))

st.sidebar.markdown("---")
st.sidebar.info("**系统状态**: ✅ 正常运行\n\n**最后更新**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
