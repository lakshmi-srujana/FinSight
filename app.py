import streamlit as st
import pandas as pd
import numpy as np

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
    balance = income - abs(expenses)

    col1, col2, col3 = st.columns(3)

    col1.metric("💼 Income", f"₹{income}")
    col2.metric("💸 Expenses", f"₹{abs(expenses)}")
    col3.metric("💰 Balance", f"₹{balance}")

    st.divider()
        # ---------- NUMPY INSIGHT ----------
    expense_values = df[df["amount"] < 0]["amount"].values

    if len(expense_values) > 0:
        max_expense = np.min(expense_values)
        st.info(f"📉 Highest single expense: ₹{abs(max_expense)}")

    st.subheader("Overview")
    st.write("Your financial summary based on recorded transactions.")
    st.subheader("Spending by Category")
    expense_df = df[df["amount"] < 0]
    category_summary = (
        expense_df.groupby("category")["amount"]
        .sum()
        .abs()
    )

    st.bar_chart(category_summary)


elif menu == "Transactions":
    st.subheader("All Transactions")
    st.dataframe(df)
