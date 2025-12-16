import streamlit as st
import pandas as pd
import numpy as np
import os
import altair as alt
import streamlit.components.v1 as components

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="FinSight", layout="wide")

# --------------------------------------------------
# GLOBAL DARK THEME
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f172a;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }

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

    h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
    }

    h2, h3 {
        color: #f8fafc;
        font-weight: 600;
    }

    div[style*="background:#ffffff"] {
        background-color: #020617 !important;
        border: 1px solid #1e293b;
    }

    p {
        color: #cbd5f5;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
if not os.path.exists("transactions.csv"):
    df = pd.DataFrame(columns=["date", "category", "description", "amount"])
    df.to_csv("transactions.csv", index=False)
else:
    df = pd.read_csv("transactions.csv", on_bad_lines="skip", engine="python")

if not df.empty:
    # Robust date parsing (prevents crashes)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Drop rows with invalid dates
    df = df.dropna(subset=["date"])

    df["month"] = df["date"].dt.strftime("%Y-%m")

else:
    df["month"] = []

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


menu = st.sidebar.radio("Navigate", ["Dashboard", "Transactions"])

available_months = sorted(df["month"].unique())
selected_month = st.sidebar.selectbox("Select Month", available_months) if available_months else None
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

    income = filtered_df.loc[filtered_df["amount"] > 0, "amount"].sum()
    expenses = filtered_df.loc[filtered_df["amount"] < 0, "amount"].sum()
    balance = income + expenses

    # ---------- METRIC CARDS ----------
    components.html(
    f"""
    <div style="display:flex; gap:20px; margin-bottom:30px;">
        <div style="
            flex:1;
            background:#020617;
            padding:24px;
            border-radius:14px;
            border:1px solid #1e293b;
            box-shadow:0 6px 16px rgba(0,0,0,0.4);
        ">
            <p style="margin:0; color:#cbd5f5;">Income</p>
            <h2 style="margin:8px 0; color:#f8fafc;">₹{income:,.0f}</h2>
        </div>

        <div style="
            flex:1;
            background:#020617;
            padding:24px;
            border-radius:14px;
            border:1px solid #1e293b;
            box-shadow:0 6px 16px rgba(0,0,0,0.4);
        ">
            <p style="margin:0; color:#cbd5f5;">Expenses</p>
            <h2 style="margin:8px 0; color:#f8fafc;">₹{abs(expenses):,.0f}</h2>
        </div>

        <div style="
            flex:1;
            background:#020617;
            padding:24px;
            border-radius:14px;
            border:1px solid #1e293b;
            box-shadow:0 6px 16px rgba(0,0,0,0.4);
        ">
            <p style="margin:0; color:#cbd5f5;">Balance</p>
            <h2 style="margin:8px 0; color:#f8fafc;">₹{balance:,.0f}</h2>
        </div>
    </div>
    """,
    height=170
)


    # ---------- NUMPY INSIGHT ----------
    expense_values = df.loc[df["amount"] < 0, "amount"].values
    if expense_values.size > 0:
        st.info(f"📉 Highest single expense: ₹{abs(expense_values.min()):,.0f}")

    st.subheader("Overview")
    st.write("Your financial summary based on recorded transactions.")

    # ---------- SMART INSIGHT ----------
    expense_df = filtered_df.loc[filtered_df["amount"] < 0].copy()

    if not expense_df.empty:
        category_totals = expense_df.groupby("category")["amount"].sum().abs()
        top_category = category_totals.idxmax()
        top_amount = category_totals.max()

        st.markdown(
            f"""
            <div style="
                background:#020617;
                padding:16px;
                border-radius:12px;
                border:1px solid #1e293b;
                margin-bottom:20px;
            ">
                🧠 Highest spending category this month:
                <strong>{top_category}</strong> (₹{top_amount:,.0f})
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------- DONUT CHART ----------
    st.markdown(
        """
        <div style="padding:24px; border-radius:16px;
                    box-shadow:0 6px 16px rgba(0,0,0,0.05); margin-top:20px;">
        """,
        unsafe_allow_html=True
    )

    st.subheader("Spending by Category")

    if not expense_df.empty:
        chart_data = expense_df.groupby("category", as_index=False)["amount"].sum()
        chart_data["amount"] = chart_data["amount"].abs()

        donut = (
            alt.Chart(chart_data)
            .mark_arc(innerRadius=80)
            .encode(
                theta=alt.Theta("amount:Q"),
                color=alt.Color("category:N", legend=alt.Legend(title="Category")),
                tooltip=["category", alt.Tooltip("amount:Q", format=",.0f")]
            )
            .properties(height=320)
        )

        st.altair_chart(donut, use_container_width=True)
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
        category = st.selectbox("Category", ["Income", "Food", "Transport", "Shopping", "Bills", "Other"])
        description = st.text_input("Description")
        amount = st.number_input("Amount (use negative for expenses)", value=0)

        if st.form_submit_button("Add Transaction"):

    # AUTO-CONVERT EXPENSES TO NEGATIVE
            if category != "Income" and amount > 0:
                amount = -amount

            pd.DataFrame([{
                "date": date,
                "category": category,
                "description": description,
                "amount": amount
            }]).to_csv(
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
    st.markdown("<br>", unsafe_allow_html=True)

    st.download_button(
        label="⬇ Download Transactions as CSV",
        data=df.to_csv(index=False),
        file_name="finsight_transactions.csv",
        mime="text/csv"
    )
    st.markdown("Delete a Transaction")

    if not df.empty:
        row_to_delete = st.number_input(
            "Enter row index to delete (see table index)",
            min_value=0,
            max_value=len(df) - 1,
            step=1
        )

        if st.button("Delete Transaction"):
            updated_df = df.drop(index=row_to_delete).reset_index(drop=True)
            updated_df.to_csv("transactions.csv", index=False)

            st.success("Transaction deleted successfully.")
            st.rerun()
    else:
        st.info("No transactions available to delete.")

    st.markdown("Edit a Transaction")

    if not df.empty:
        row_to_edit = st.number_input(
            "Enter row index to edit",
            min_value=0,
            max_value=len(df) - 1,
            step=1,
            key="edit_index"
        )

        selected_row = df.loc[row_to_edit]

        with st.form("edit_transaction_form"):
            edit_date = st.date_input("Date", pd.to_datetime(selected_row["date"]))
            edit_category = st.selectbox(
                "Category",
                ["Income", "Food", "Transport", "Shopping", "Bills", "Other"],
                index=["Income", "Food", "Transport", "Shopping", "Bills", "Other"].index(
                    selected_row["category"]
                )
            )
            edit_description = st.text_input(
                "Description", selected_row["description"]
            )
            edit_amount = st.number_input(
                "Amount", value=float(selected_row["amount"])
            )

            if st.form_submit_button("Update Transaction"):
                df.at[row_to_edit, "date"] = edit_date
                df.at[row_to_edit, "category"] = edit_category
                df.at[row_to_edit, "description"] = edit_description
                df.at[row_to_edit, "amount"] = edit_amount

                # Recompute month after edit
                df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")


                df.to_csv("transactions.csv", index=False)


                st.success("Transaction updated successfully.")
                st.rerun()
    else:
        st.info("No transactions available to edit.")


