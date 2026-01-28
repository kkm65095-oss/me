import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# 读取数据
df = pd.read_csv("sales_data.csv")
df["date"] = pd.to_datetime(df["date"])

st.set_page_config(page_title="跨境电商春季大促看板", layout="wide")

st.title("🌸 跨境电商春季大促可视化看板")

# --- 筛选器 ---
st.sidebar.header("筛选条件")
selected_country = st.sidebar.multiselect("选择国家", df["country"].unique(), default=df["country"].unique())
selected_category = st.sidebar.multiselect("选择品类", df["category"].unique(), default=df["category"].unique())
date_range = st.sidebar.date_input("选择日期范围", [df["date"].min(), df["date"].max()])
predict_days = st.sidebar.slider("预测未来天数", 3, 14, 7)

# --- 数据过滤 ---
filtered_df = df[
    (df["country"].isin(selected_country)) &
    (df["category"].isin(selected_category)) &
    (df["date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# --- KPI 卡片 ---
total_sales = filtered_df["sales"].sum()
total_orders = filtered_df["orders"].sum()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("💰 总销售额", f"${total_sales:,.0f}")
col_kpi2.metric("📦 总订单量", f"{total_orders:,}")
col_kpi3.metric("🛒 平均客单价", f"${avg_order_value:,.2f}")

# --- 销售额趋势 + 预测 ---
st.subheader("每日销售额趋势（含预测）")

# 准备数据
sales_by_date = filtered_df.groupby("date")["sales"].sum().reset_index()
sales_by_date["day_num"] = (sales_by_date["date"] - sales_by_date["date"].min()).dt.days

# 建模
X = sales_by_date[["day_num"]]
y = sales_by_date["sales"]
model = LinearRegression()
model.fit(X, y)

# 预测未来
future_days = np.arange(sales_by_date["day_num"].max()+1, sales_by_date["day_num"].max()+1+predict_days)
future_dates = [sales_by_date["date"].max() + pd.Timedelta(days=i) for i in range(1, predict_days+1)]
future_sales = model.predict(future_days.reshape(-1,1))

# 合并数据
forecast_df = pd.DataFrame({"date": future_dates, "sales": future_sales})
plot_df = pd.concat([sales_by_date[["date","sales"]], forecast_df])

# 绘图
fig_sales = px.line(plot_df, x="date", y="sales", title="销售额趋势与预测")
fig_sales.add_scatter(x=forecast_df["date"], y=forecast_df["sales"], mode="lines+markers", name="预测")
st.plotly_chart(fig_sales, use_container_width=True)

# --- 其他图表 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("各国家订单量")
    country_orders = filtered_df.groupby("country")["orders"].sum().reset_index()
    fig_orders = px.bar(country_orders, x="country", y="orders", color="country", title="订单量分布")
    st.plotly_chart(fig_orders, use_container_width=True)

with col2:
    st.subheader("热销品类占比")
    fig_category = px.pie(filtered_df, names="category", values="sales", hole=0.4, title="品类销售额占比")
    st.plotly_chart(fig_category, use_container_width=True)

st.subheader("渠道销售额")
channel_sales = filtered_df.groupby("channel")["sales"].sum().reset_index()
fig_channel = px.bar(channel_sales, x="channel", y="sales", color="channel", title="渠道销售额")
st.plotly_chart(fig_channel, use_container_width=True)
