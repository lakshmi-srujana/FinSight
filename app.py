import streamlit as st
import pandas as pd
import numpy as np
import os
import altair as alt
import streamlit.components.v1 as components

# --------------------------------------------------
# PAGE CONFIG (must be first Streamlit call)
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* =======================
       APP BACKGROUND
       ======================= */
    .stApp {
        background-color: #0f172a;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #e5e7eb;
    }

    /* =======================
       SIDEBAR
       ======================= */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] div[role="radiogroup"] * {
        color: #e5e7eb !important;
    }

    section[data-testid="stSidebar"] h1 {
        font-weight: 700;
    }

    /* =======================
       SELECT MONTH (DARK)
       ======================= */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #020617 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #e5e7eb !important;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] svg {
        fill: #e5e7eb !important;
    }

    /* =======================
       HEADINGS
       ======================= */
    h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
    }

    h2, h3 {
        color: #f8fafc;
        font-weight: 600;
    }

    /* =======================
       CARDS & CONTAINERS
       ======================= */
    div[style*="background:#ffffff"] {
        background-color: #020617 !important;
        border: 1px solid #1e293b;
    }

    /* =======================
       PARAGRAPH TEXT
       ======================= */
    p {
        color: #cbd5f5;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# LOAD DATA (SAFE FOR CLOUD)
# --------------------------------------------------
if not os.path.exists("transactions.csv"):
    df = pd.DataFrame(columns=["date", "category", "description", "amount"])
    df.to_csv("transactions.csv", index=False)
else:
    df = pd.read_csv(
        "transactions.csv",
        on_bad_lines="skip",
        engine="python"
    )

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%Y-%m")
else:
    df["month"] = []

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.title("FinSight")

menu = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Transactions"]
)

available_months = sorted(df["month"].unique())
selected_month = (
    st.sidebar.selectbox("Select Month", available_months)
    if len(available_months) > 0
    else None
)

filtered_df = df[df["month"] == selected_month] if selected_month else df

# --------------------------------------------------
# MAIN
# --------------------------------------------------
st.title("FinSight Dashboard")
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ==================================================
# DASHBOARD
# ==================================================
if menu == "Dashboard":

    income = filtered_df[filtered_df["amount"] > 0]["amount"].sum()
    expenses = filtered_df[filtered_df["amount"] < 0]["amount"].sum()
    balance = income + expenses  # expenses already negative

    # ---------- METRIC CARDS ----------
    components.html(
        f"""
        <div style="display:flex; gap:20px; margin-bottom:30px;">
            <div style="flex:1; background:#ffffff; padding:24px;
                        border-radius:14px;
                        box-shadow:0 6px 16px rgba(0,0,0,0.06);">
                <p style="color:#6b7280; margin:0;">Income</p>
                <h2 style="margin:8px 0;">₹{income:,.0f}</h2>
            </div>

            <div style="flex:1; background:#ffffff; padding:24px;
                        border-radius:14px;
                        box-shadow:0 6px 16px rgba(0,0,0,0.06);">
                <p style="color:#6b7280; margin:0;">Expenses</p>
                <h2 style="margin:8px 0;">₹{abs(expenses):,.0f}</h2>
            </div>

            <div style="flex:1; background:#ffffff; padding:24px;
                        border-radius:14px;
                        box-shadow:0 6px 16px rgba(0,0,0,0.06);">
                <p style="color:#6b7280; margin:0;">Balance</p>
                <h2 style="margin:8px 0;">₹{balance:,.0f}</h2>
            </div>
        </div>
        """,
        height=160
    )

    # ---------- NUMPY INSIGHT ----------
    expense_values = df[df["amount"] < 0]["amount"].values
    if len(expense_values) > 0:
        st.info(f"📉 Highest single expense: ₹{abs(np.min(expense_values)):,.0f}")

    st.subheader("Overview")
    st.write("Your financial summary based on recorded transactions.")

 # ---------- SPENDING BY CATEGORY ----------
    st.markdown(
        """
        <div style="
            background:#ffffff;
            padding:24px;
            border-radius:16px;
            box-shadow:0 6px 16px rgba(0,0,0,0.05);
            margin-top:20px;
        ">
        """,
        unsafe_allow_html=True
    )

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
            .mark_arc(innerRadius=80)
            .encode(
                theta=alt.Theta("amount:Q", stack=True),
                color=alt.Color(
                    "category:N",
                    scale=alt.Scale(scheme="tableau10"),
                    legend=alt.Legend(title="Category")
                ),
                tooltip=[
                    alt.Tooltip("category:N", title="Category"),
                    alt.Tooltip("amount:Q", title="Amount", format=",.0f")
                ]
            )
            .properties(
                height=320,
                background="#ffffff"
            )
        )

        st.altair_chart(chart, use_container_width=True)


    else:
        st.info("No expenses for this month")

    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# TRANSACTIONS
# ==================================================
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
            new_df = pd.DataFrame([{
                "date": date,
                "category": category,
                "description": description,
                "amount": amount
            }])

            new_df.to_csv(
                "transactions.csv",
                mode="a",
                header=False,
                index=False,
                lineterminator="\n"
            )

            st.success("Transaction added successfully!")
            st.rerun()

    st.subheader("All Transactions")
    st.dataframe(df, use_container_width=True)