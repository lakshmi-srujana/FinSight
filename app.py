import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="FinSight",
    layout="wide"
)

# ---------- LOAD DATA ----------
df = pd.read_csv("transactions.csv")

# ---------- SIDEBAR ----------
st.sidebar.title("💰 FinSight")
menu = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Transactions"]
)

# ---------- MAIN ----------
st.title("FinSight Dashboard")

if menu == "Dashboard":
    income = df[df["amount"] > 0]["amount"].sum()
    expenses = df[df["amount"] < 0]["amount"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Income", f"₹{income}")
    col2.metric("Total Expenses", f"₹{abs(expenses)}")

elif menu == "Transactions":
    st.subheader("All Transactions")
    st.dataframe(df)
