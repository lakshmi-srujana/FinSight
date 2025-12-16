import streamlit as st

st.set_page_config(
    page_title="FinSight",
    layout="wide"
)

# ---------- SIDEBAR ----------
st.sidebar.title("💰 FinSight")
menu = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Transactions", "Statistics"]
)

# ---------- MAIN AREA ----------
st.title("FinSight Dashboard")
st.caption("A simple Python-based finance tracker")

if menu == "Dashboard":
    col1, col2, col3 = st.columns(3)

    col1.metric("Monthly Budget", "₹45,000")
    col2.metric("Income", "₹52,000")
    col3.metric("Expenses", "₹36,000")

    st.divider()
    st.subheader("Welcome 👋")
    st.write("This is your dashboard overview.")

elif menu == "Transactions":
    st.subheader("Transactions")
    st.write("Transactions page coming soon 🚧")

elif menu == "Statistics":
    st.subheader("Statistics")
    st.write("Statistics page coming soon 📊")
