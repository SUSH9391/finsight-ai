import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ─── Config ───────────────────────────────────────────
API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="FinSight AI",
    page_icon="💰",
    layout="wide"
)

# ─── Session state init ────────────────────────────────
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# ─── Auth helpers ──────────────────────────────────────
def auth_headers():
    if st.session_state.jwt_token:
        return {"Authorization": f"Bearer {st.session_state.jwt_token}"}
    return {}

# ─── Sidebar: Login / Register ─────────────────────────
with st.sidebar:
    st.title("🔐 FinSight AI")

    if st.session_state.jwt_token:
        st.success(f"Logged in as\n**{st.session_state.user_email}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.jwt_token = None
            st.session_state.user_email = None
            st.rerun()
    else:
        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", use_container_width=True, key="btn_login"):
                try:
                    res = requests.post(
                        f"{API_BASE}/auth/login",
                        data={"username": login_email, "password": login_password},
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                    if res.status_code == 200:
                        token_data = res.json()
                        st.session_state.jwt_token = token_data["access_token"]
                        st.session_state.user_email = login_email
                        st.success("✅ Logged in!")
                        st.rerun()
                    else:
                        try:
                            detail = res.json().get("detail", "Login failed")
                        except Exception:
                            detail = res.text or f"HTTP {res.status_code}"
                        st.error(f"❌ {detail}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend.")

        with tab_register:
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            if st.button("Register", use_container_width=True, key="btn_register"):
                try:
                    res = requests.post(
                        f"{API_BASE}/auth/register",
                        json={"full_name": reg_name, "email": reg_email, "password": reg_password}
                    )
                    if res.status_code == 200:
                        st.success("✅ Account created! Please log in.")
                    else:
                        try:
                            detail = res.json().get("detail", "Registration failed")
                        except Exception:
                            detail = res.text or f"HTTP {res.status_code}"
                        st.error(f"❌ {detail}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend.")

# ─── Main content: require login ──────────────────────
if not st.session_state.jwt_token:
    st.title("💰 FinSight AI")
    st.subheader("Your AI-powered personal finance advisor")
    st.info("👈 Please **login or register** in the sidebar to get started.")
    st.stop()

# ─── Header ───────────────────────────────────────────
st.title("💰 FinSight AI")
st.subheader("Your AI-powered personal finance advisor")
st.divider()

# ─── Upload Section ────────────────────────────────────
st.markdown("### 📂 Upload your bank statement")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    with st.spinner("Uploading and categorizing transactions..."):
        try:
            response = requests.post(
                f"{API_BASE}/upload/csv",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                headers=auth_headers()
            )

            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ {data['transactions_count']} transactions uploaded and categorized!")
                st.rerun()
            else:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                except Exception:
                    error_detail = response.text or f"HTTP {response.status_code}"
                st.error(f"❌ Upload failed: {error_detail}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to FastAPI. Make sure uvicorn is running on port 8000.")

st.divider()

# ─── Always fetch fresh data ──────────────────────────
def fetch_summary():
    try:
        res = requests.get(f"{API_BASE}/analysis/summary", headers=auth_headers())
        if res.status_code == 200:
            return res.json()
        return None
    except:
        return None

summary = fetch_summary()

if summary:
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

    # Embed transactions after upload
    if st.button("🔄 Embed for Chat (run after upload)"):
        try:
            res = requests.post(f"{API_BASE}/chat/embed", headers=auth_headers())
            st.success(res.json()['message'])
        except:
            st.error("Embed failed - no auth or no transactions")

    # Chat Component
    st.markdown("### 🤖 AI Chat")
    try:
        from components.chat_component import chat_interface
        chat_interface(API_BASE, st.session_state.jwt_token)
    except ImportError:
        st.info("Chat component ready - Phase 5 integration next!")

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
            trend_res = requests.get(f"{API_BASE}/analysis/monthly", headers=auth_headers())
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

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + list(summary.get("category_breakdown", {}).keys()) if summary else ["All"]
        )
    with f_col2:
        type_filter = st.selectbox("Filter by Type", ["All", "credit", "debit"])

    params = {"page": 1, "page_size": 50}
    if category_filter != "All":
        params["category"] = category_filter
    if type_filter != "All":
        params["type"] = type_filter

    try:
        txn_res = requests.get(f"{API_BASE}/analysis/transactions", params=params, headers=auth_headers())
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

    if st.button("🔄 Upload a new file"):
        st.session_state.uploaded = False
        st.session_state.summary = None
        st.rerun()

else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Income", "₹0")
    with col2:
        st.metric("Total Expenses", "₹0")
    with col3:
        st.metric("Net Savings", "₹0")
    st.info("👆 Upload a CSV above to see your financial insights!")
