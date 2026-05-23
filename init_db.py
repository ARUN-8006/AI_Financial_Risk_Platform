import sqlite3

conn = sqlite3.connect("financial_risk.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    risk TEXT,
    score INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id TEXT,
    type TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fraud_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    txn TEXT,
    amount INTEGER,
    risk TEXT
)
""")

cursor.execute("DELETE FROM users")
cursor.execute("DELETE FROM applications")
cursor.execute("DELETE FROM fraud_logs")

cursor.executemany("""
INSERT INTO users (name, risk, score) VALUES (?, ?, ?)
""", [
    ("Rahul Sharma", "Low", 760),
    ("Aman Khan", "High", 510),
    ("Priya Verma", "Medium", 640),
    ("Neha Singh", "Low", 790)
])

cursor.executemany("""
INSERT INTO applications (app_id, type, status) VALUES (?, ?, ?)
""", [
    ("APP-1001", "Loan", "Approved"),
    ("APP-1002", "Loan", "Rejected"),
    ("APP-1003", "Credit Review", "Manual Review")
])

cursor.executemany("""
INSERT INTO fraud_logs (txn, amount, risk) VALUES (?, ?, ?)
""", [
    ("TXN-90821", 98500, "High"),
    ("TXN-55410", 25000, "Low"),
    ("TXN-77219", 125000, "Critical")
])

cursor.execute("""
CREATE TABLE IF NOT EXISTS loan_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER,
    income INTEGER,
    loan_amount INTEGER,
    credit_history INTEGER,
    existing_debt INTEGER,
    employment_years INTEGER,
    result TEXT,
    risk_score REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fraud_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount INTEGER,
    hour INTEGER,
    location_risk INTEGER,
    device_risk INTEGER,
    failed_attempts INTEGER,
    result TEXT,
    fraud_probability REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS credit_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    income INTEGER,
    repayment INTEGER,
    debt INTEGER,
    credit_history INTEGER,
    late_payments INTEGER,
    score INTEGER,
    category TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")