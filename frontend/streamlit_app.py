import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ─── Config ───────────────────────────────────────────
API_BASE = "http://localhost:8000/api"

st.set_page_config(
    page_title="FinSight AI",
    page_icon="💰",
    layout="wide"
)

# ─── Session state init ────────────────────────────────
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "summary" not in st.session_state:
    st.session_state.summary = None

# ─── Header ───────────────────────────────────────────
st.title("💰 FinSight AI")
st.subheader("Your AI-powered personal finance advisor")
st.divider()

# ─── Upload Section ────────────────────────────────────
st.markdown("### 📂 Upload your bank statement")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file and not st.session_state.uploaded:
    with st.spinner("Uploading and categorizing transactions..."):
        try:
            # Send CSV to FastAPI
            response = requests.post(
                f"{API_BASE}/upload/csv",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.uploaded = True
                st.success(f"✅ {data['transactions_count']} transactions uploaded and categorized!")

                # Fetch summary right after upload
                summary_res = requests.get(f"{API_BASE}/analysis/summary")
                if summary_res.status_code == 200:
                    st.session_state.summary = summary_res.json()
            else:
                st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to FastAPI. Make sure uvicorn is running on port 8000.")

st.divider()

# ─── Dashboard (only shows after upload) ──────────────
if st.session_state.summary:
    summary = st.session_state.summary

    # KPI Metrics
    st.markdown("### 📊 Spending Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Income", f"₹{summary['total_income']:,.2f}")
    with col2:
        st.metric("Total Expenses", f"₹{summary['total_expenses']:,.2f}")
    with col3:
        savings = summary['net_savings']
        st.metric("Net Savings", f"₹{savings:,.2f}", delta="positive" if savings > 0 else "negative")
    with col4:
        st.metric("Top Category", summary['top_category'])

    st.divider()

    # Charts row
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🍩 Spending by Category")
        category_data = summary.get("category_breakdown", {})
        if category_data:
            df_cat = pd.DataFrame(
                list(category_data.items()),
                columns=["Category", "Amount"]
            )
            fig = px.pie(
                df_cat, values="Amount", names="Category",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff",
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### 📈 Monthly Trend")
        try:
            trend_res = requests.get(f"{API_BASE}/analysis/monthly")
            if trend_res.status_code == 200:
                trend_data = trend_res.json().get("monthly_trend", [])
                if trend_data:
                    df_trend = pd.DataFrame(trend_data)
                    fig2 = px.bar(
                        df_trend, x="month", y=["income", "expenses"],
                        barmode="group",
                        labels={"value": "Amount (₹)", "month": "Month"},
                        color_discrete_map={"income": "#00ff88", "expenses": "#ff6b35"}
                    )
                    fig2.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#ffffff"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Not enough data for monthly trend.")
        except:
            st.warning("Could not load monthly trend.")

    st.divider()

    # Transactions Table
    st.markdown("### 🧾 Transactions")

    # Filters
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + list(summary.get("category_breakdown", {}).keys())
        )
    with f_col2:
        type_filter = st.selectbox("Filter by Type", ["All", "credit", "debit"])

    # Build query params
    params = {"page": 1, "page_size": 50}
    if category_filter != "All":
        params["category"] = category_filter
    if type_filter != "All":
        params["type"] = type_filter

    try:
        txn_res = requests.get(f"{API_BASE}/analysis/transactions", params=params)
        if txn_res.status_code == 200:
            txn_data = txn_res.json()
            df_txn = pd.DataFrame(txn_data["transactions"])
            if not df_txn.empty:
                st.dataframe(df_txn, use_container_width=True)
                st.caption(f"Showing {len(df_txn)} of {txn_data['total']} transactions")
            else:
                st.info("No transactions match the filter.")
    except:
        st.warning("Could not load transactions.")

    st.divider()

    # Reset button
    if st.button("🔄 Upload a new file"):
        st.session_state.uploaded = False
        st.session_state.summary = None
        st.rerun()

else:
    # Placeholder before upload
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Income", "₹0")
    with col2:
        st.metric("Total Expenses", "₹0")
    with col3:
        st.metric("Net Savings", "₹0")
    st.info("👆 Upload a CSV above to see your financial insights!")
