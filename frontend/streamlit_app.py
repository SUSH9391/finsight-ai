import streamlit as st

st.set_page_config(
    page_title="FinSight AI",
    page_icon="💰",
    layout="wide"
)

st.title("💰 FinSight AI")
st.subheader("Your AI-powered personal finance advisor")

st.info("🚧 Dashboard under construction — coming soon!")

# Placeholder layout
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Income", value="₹0", delta="")
with col2:
    st.metric(label="Total Expenses", value="₹0", delta="")
with col3:
    st.metric(label="Net Savings", value="₹0", delta="")

st.divider()
st.markdown("### 📂 Upload your bank statement to get started")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")