import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ────────────────────────────────────────────
st.set_page_config(page_title="Budget Dashboard", page_icon="💸", layout="wide")
st.title("💸 Personal Budget Dashboard")

conn = sqlite3.connect("budget.db")

# ── Month filter ───────────────────────────────────────────
# Lets the user pick which month to view
# Everything below this will update based on the selection
month = st.selectbox("Select Month", ["FEB 26", "MAR 26", "APR 26"])

st.divider()

# ── KPI Row ────────────────────────────────────────────────
# ? is a placeholder — (month,) passes the selected month safely into the query
total_income = conn.execute("SELECT ROUND(SUM(amount), 2) FROM income WHERE month = ?", (month,)).fetchone()[0]
total_spent = conn.execute("SELECT ROUND(SUM(amount), 2) FROM expenses WHERE month = ?", (month,)).fetchone()[0]
net = round(total_income - total_spent, 2)

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"${total_income:,.2f}")
col2.metric("Total Spent", f"${total_spent:,.2f}")
col3.metric("Net Cash Flow", f"${net:,.2f}", delta=f"${net:,.2f}")

st.divider()

# ── Spending by Category ───────────────────────────────────
st.subheader("Spending by Category")
cat_df = pd.read_sql("""
    SELECT category, ROUND(SUM(amount), 2) AS total
    FROM expenses
    WHERE month = ?
    GROUP BY category
    ORDER BY total DESC
""", conn, params=(month,))

fig1 = px.bar(cat_df, x="category", y="total", color="category",
              labels={"total": "Amount Spent ($)", "category": "Category"},
              color_discrete_sequence=px.colors.qualitative.Pastel)
fig1.update_layout(showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ── Budget vs Actual ───────────────────────────────────────
# LEFT JOIN means: show all budget categories even if there
# are no expenses logged for that category yet
st.subheader("Budget vs Actual")
budget_df = pd.read_sql("""
    SELECT b.category, b.ideal_budget,
        ROUND(SUM(e.amount), 2) AS actual_spent
    FROM budget_targets b
    LEFT JOIN expenses e ON b.category = e.category AND e.month = ?
    WHERE b.month = ?
    GROUP BY b.category
""", conn, params=(month, month))
budget_df["ideal_budget"] = budget_df["ideal_budget"].fillna(0)

fig2 = go.Figure()
fig2.add_trace(go.Bar(name="Budget", x=budget_df["category"], y=budget_df["ideal_budget"],
                      marker_color="lightblue"))
fig2.add_trace(go.Bar(name="Actual", x=budget_df["category"], y=budget_df["actual_spent"],
                      marker_color="salmon"))
fig2.update_layout(barmode="group", xaxis_title="Category", yaxis_title="Amount ($)")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Weekly Spending ────────────────────────────────────────
# strftime('%W') extracts the week number from the date
# We relabel them Week 1, Week 2 etc. so it looks clean
st.subheader("Weekly Spending")
week_df = pd.read_sql("""
    SELECT strftime('%W', date) AS week, ROUND(SUM(amount), 2) AS total
    FROM expenses
    WHERE month = ?
    GROUP BY week
    ORDER BY week
""", conn, params=(month,))
week_df["week"] = ["Week " + str(i+1) for i in range(len(week_df))]

fig3 = px.line(week_df, x="week", y="total", markers=True,
               labels={"total": "Amount Spent ($)", "week": ""},
               color_discrete_sequence=["#7C83FD"])
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Top 5 Biggest Expenses ─────────────────────────────────
st.subheader("Top 5 Biggest Expenses")
top_df = pd.read_sql("""
    SELECT description, category, ROUND(amount, 2) AS amount, date
    FROM expenses
    WHERE month = ?
    ORDER BY amount DESC
    LIMIT 5
""", conn, params=(month,))
st.dataframe(top_df, use_container_width=True)

conn.close()