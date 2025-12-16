import streamlit as st
import pandas as pd
import numpy as np
import os
import altair as alt

st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: #f6f7fb;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #1f2933;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* Headings */
    h1, h2, h3 {
        color: #111827;
        font-weight: 600;
    }

    /* Subtle divider */
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.set_page_config(
    page_title="FinSight",
    layout="wide"
)

# ---------- LOAD DATA ----------
# ---------- SAFE CSV LOAD ----------
if not os.path.exists("transactions.csv"):
    df = pd.DataFrame(columns=["date", "category", "description", "amount"])
    df.to_csv("transactions.csv", index=False)
else:
    df = pd.read_csv(
    "transactions.csv",
    on_bad_lines="skip",
    engine="python"
)


# ---------- DATE PROCESSING ----------
if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%Y-%m")
else:
    df["month"] = []

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

    if not expense_df.empty:
        chart_data = (
            expense_df.groupby("category", as_index=False)["amount"]
            .sum()
        )
        chart_data["amount"] = chart_data["amount"].abs()

        chart = (
            alt.Chart(chart_data)
            .mark_bar(
                color="#4f46e5",
                cornerRadiusTopLeft=6,
                cornerRadiusTopRight=6
            )
            .encode(
                x=alt.X("category:N", title=""),
                y=alt.Y("amount:Q", title="Amount Spent"),
                tooltip=["category", "amount"]
            )
            .properties(height=320)
        )

        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No expenses for this month")




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
