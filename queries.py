import sqlite3

conn = sqlite3.connect("budget.db")

# ── 1. Total income vs total spending ─────────────────────
print("=== INCOME VS SPENDING ===")
print(conn.execute("""
    SELECT 
        (SELECT ROUND(SUM(amount), 2) FROM income) AS total_income,
        (SELECT ROUND(SUM(amount), 2) FROM expenses) AS total_spent
""").fetchall())

# ── 2. Spending by category ────────────────────────────────
print("\n=== SPENDING BY CATEGORY ===")
rows = conn.execute("""
    SELECT category, ROUND(SUM(amount), 2) AS total
    FROM expenses
    GROUP BY category
    ORDER BY total DESC
""").fetchall()
for r in rows: print(r)

# ── 3. Budget vs actual ────────────────────────────────────
print("\n=== BUDGET VS ACTUAL ===")
rows = conn.execute("""
    SELECT 
        b.category,
        b.ideal_budget,
        ROUND(SUM(e.amount), 2) AS actual_spent,
        ROUND(SUM(e.amount) - b.ideal_budget, 2) AS difference
    FROM budget_targets b
    LEFT JOIN expenses e ON b.category = e.category
    GROUP BY b.category
    ORDER BY difference DESC
""").fetchall()
for r in rows: print(r)

# ── 4. Top 5 biggest expenses ──────────────────────────────
print("\n=== TOP 5 BIGGEST EXPENSES ===")
rows = conn.execute("""
    SELECT description, category, ROUND(amount, 2) AS amount, date
    FROM expenses
    ORDER BY amount DESC
    LIMIT 5
""").fetchall()
for r in rows: print(r)

# ── 5. Spending by week ────────────────────────────────────
print("\n=== SPENDING BY WEEK ===")
rows = conn.execute("""
    SELECT 
        strftime('%W', date) AS week,
        ROUND(SUM(amount), 2) AS total
    FROM expenses
    GROUP BY week
    ORDER BY week
""").fetchall()
for r in rows: print(r)

conn.close()