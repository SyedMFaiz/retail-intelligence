import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Retail Intelligence Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
}
header, footer {visibility: hidden;}

.block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
}

.kpi-card {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 15px;
    border: 1px solid rgba(255,255,255,0.1);
    text-align: center;
    transition: 0.3s;
}
.kpi-card:hover {
    transform: translateY(-4px);
    background: rgba(255,255,255,0.1);
}

.alert-box {
    background: rgba(255, 75, 75, 0.2);
    border-left: 5px solid #ff4b4b;
    padding: 8px;
    border-radius: 6px;
    margin-bottom: 8px;
    font-size: 0.85rem;
}
/* Custom Thin Scrollbar for Alerts */
.scroll-container {
    max-height: 280px; 
    overflow-y: auto;
    padding-right: 10px;
}
.scroll-container::-webkit-scrollbar {
    width: 6px;
}
.scroll-container::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}
.scroll-container::-webkit-scrollbar-thumb {
    background: #00d4ff;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA GENERATION ----------------
@st.cache_data
def generate_data():
    np.random.seed(42)

    branches = ["Karachi", "Lahore", "Islamabad"]
    categories = ["Electronics", "Apparel", "Home", "Grocery", "Beauty"]

    dates = pd.date_range(end=datetime.today(), periods=60)

    rows = []

    for date in dates:
        for branch in branches:
            for cat in categories:
                sales = np.random.randint(2000, 8000)
                cost = sales * np.random.uniform(0.6, 0.85)
                stock = np.random.randint(10, 150)

                rows.append([
                    date, branch, cat, sales, cost, stock
                ])

    df = pd.DataFrame(rows, columns=[
        "Date", "Branch", "Category",
        "Sales", "Cost", "Stock"
    ])

    df["Profit"] = df["Sales"] - df["Cost"]
    df["Margin"] = (df["Profit"] / df["Sales"]) * 100

    return df

df = generate_data()

# ---------------- HEADER ----------------
# col_title, col_filter = st.columns([4,1])
col_title, col_category, col_branch = st.columns([3,1,1])

with col_title:
    st.markdown("## NEXUS <span style='color:#00d4ff;'>RETAIL</span>", unsafe_allow_html=True)
    st.caption("Executive Command Center")

with col_branch:
    selected_branch = st.selectbox(
        "Branch",
        ["All"] + list(df["Branch"].unique())
    )

with col_category:
    selected_category = st.selectbox(
        "Category",
        ["All"] + list(df["Category"].unique())
    )

# ---------------- FILTER DATA ----------------
filtered = df

if selected_branch != "All":
    filtered = df[df["Branch"] == selected_branch]

if selected_category != "All":
    filtered = filtered[filtered["Category"] == selected_category]


# ---------------- KPI CALCULATIONS ----------------
total_revenue = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
avg_margin = filtered["Margin"].mean()
avg_ticket = filtered["Sales"].mean()

# Week-over-week comparison
last_week = filtered[filtered["Date"] >= filtered["Date"].max() - timedelta(days=7)]["Sales"].sum()
prev_week = filtered[
    (filtered["Date"] < filtered["Date"].max() - timedelta(days=7)) &
    (filtered["Date"] >= filtered["Date"].max() - timedelta(days=14))
]["Sales"].sum()

if prev_week > 0:
    growth = ((last_week - prev_week) / prev_week) * 100
else:
    growth = 0

# ---------------- KPI ROW ----------------
k1, k2, k3, kg = st.columns([1.5, 1.5, 1.5, 1.5])

# Performance Gauge
def draw_performance_gauge(column, score):
    with column:
        # Constrain score
        val = min(max(score + 50, 0), 100)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={'font': {'size': 20, 'color': "white"}, 'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#00ffcc"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 1,
                'bordercolor': "rgba(255,255,255,0.2)"
            }
        ))
        fig_gauge.update_layout(
            height=130, # Smaller height keeps it on one line
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

def kpi(col, label, value, delta=None, prefix=""):
    color = "#00ffcc" if delta and delta > 0 else "#ff4b4b"
    arrow = "▲" if delta and delta > 0 else "▼"
    formatted_prefix = f"<span style='font-size: 0.75rem; opacity: 0.8;'>{prefix}</span> " if prefix else ""

    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <p style="font-size:0.85rem;color:#bdc3c7;">{label} {f"<span style='color:{color};font-size:0.75rem;'>{arrow} {abs(delta):.1f}% WoW</span>" if delta else ""}</p>
            <h3 style="margin:0;">{formatted_prefix}{value}</h3>
        </div>
        """, unsafe_allow_html=True)

kpi(k1, "Total Revenue", f"{total_revenue:,.0f}", delta=growth, prefix='PKR')
kpi(k2, "Total Profit", f"{total_profit:,.0f}", prefix="PKR")
kpi(k3, "Avg Margin", f"{avg_margin:.1f}%")
# kpi(k4, "Avg Ticket Size", f"PKR. {avg_ticket:,.0f}")
draw_performance_gauge(kg, growth)

st.html('<br>')

# ---------------- MAIN GRID ----------------
col_left, col_right = st.columns([2,1])

# ---- LEFT: Tabs for Drill Down ----
with col_left:
    tab1, tab2 = st.tabs(["📊 Category Sales", "📈 Sales Trend"])

    with tab1:
        cat_perf = filtered.groupby("Category")["Sales"].sum().reset_index()

        fig_bar = px.bar(
            cat_perf,
            x="Category",
            y="Sales",
            color="Sales",
            color_continuous_scale="Viridis",
            template="plotly_dark",
            height=320
        )

        fig_bar.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig_bar, use_container_width=True)


    with tab2:
        trend = filtered.groupby("Date")["Sales"].sum().reset_index()

        fig_line = px.line(
            trend,
            x="Date",
            y="Sales",
            template="plotly_dark",
            height=320
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_line, use_container_width=True)

# ---- RIGHT: Alerts + Gauge ----
with col_right:
    st.markdown("### 🔔 Stock Alerts")

    low_stock = filtered[filtered["Stock"] < 30]

    if not low_stock.empty:
        scroll_container = '<div class="scroll-container">'
        
        for _, row in low_stock.head(5).iterrows():
            # Color code based on severity
            # 1. Determine Colors based on 3 tiers
            if row['Stock'] < 20:
                # CRITICAL - RED
                alert_color = "rgba(255, 75, 75, 0.2)"
                border_color = "#ff4b4b"
            elif 15 <= row['Stock'] < 25:
                # WARNING - AMBER
                alert_color = "rgba(255, 165, 0, 0.2)"
                border_color = "#ffa500"
            else:
                # HEALTHY - GREEN
                alert_color = "rgba(0, 255, 204, 0.15)"
                border_color = "#00ffcc"
            
            scroll_container += f"""
            <div class="alert-box" style="background: {alert_color}; border-left: 5px solid {border_color};">
                <div style="display: flex; justify-content: space-between;">
                    <strong>{row['Category']}</strong>
                    <span style="font-weight:bold; color:{border_color}">{row['Stock']} left</span>
                </div>
                <div style="font-size: 0.75rem; opacity: 0.8;">{row['Branch']} Branch</div>
            </div>
            """

        scroll_container += '</div>' # Close container
        st.html(scroll_container)
    else:
        st.success("All stock levels healthy")
