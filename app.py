import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="FinSight",
    layout="wide"
)

# ---------- LOAD DATA ----------
df = pd.read_csv("transactions.csv")
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.strftime("%Y-%m")


# ---------- SIDEBAR ----------
st.sidebar.title("💰 FinSight")
menu = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Transactions"]
)
# ---------- MONTH SELECTOR ----------
available_months = sorted(df["month"].unique())
selected_month = st.sidebar.selectbox(
    "Select Month",
    available_months
)
filtered_df = df[df["month"] == selected_month]



# ---------- MAIN ----------
st.title("FinSight Dashboard")

if menu == "Dashboard":
    income = filtered_df[filtered_df["amount"] > 0]["amount"].sum()
    expenses = filtered_df[filtered_df["amount"] < 0]["amount"].sum()
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
    expense_df = filtered_df[filtered_df["amount"] < 0]
    category_summary = (
        expense_df.groupby("category")["amount"]
        .sum()
        .abs()
    )

    st.bar_chart(category_summary)



elif menu == "Transactions":
    st.subheader("Add New Transaction")

    with st.form("transaction_form"):
        date = st.date_input("Date")
        category = st.selectbox(
            "Category",
            ["Income", "Food", "Transport", "Shopping", "Bills", "Other"]
        )
        description = st.text_input("Description")
        amount = st.number_input("Amount (use negative for expenses)", value=0)

        submitted = st.form_submit_button("Add Transaction")
        if submitted:
            new_row = {
                "date": date,
                "category": category,
                "description": description,
                "amount": amount
            }

            new_df = pd.DataFrame([new_row])

# Ensure consistent column order
            new_df = new_df[["date", "category", "description", "amount"]]

            new_df.to_csv(
                "transactions.csv",
                mode="a",
                header=False,
                index=False,
                lineterminator="\n"
            )


            st.success("Transaction added successfully! 🔄")
            st.rerun()



    st.divider()
    st.subheader("All Transactions")
    st.dataframe(df)
