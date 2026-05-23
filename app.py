from flask import session, redirect, url_for
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from flask import Flask, render_template, request
from dotenv import load_dotenv
import joblib
import numpy as np
import os
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("financial_risk.db")
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

loan_model = joblib.load(os.path.join(MODEL_DIR, "loan_model.pkl"))
fraud_model = joblib.load(os.path.join(MODEL_DIR, "fraud_model.pkl"))
credit_model = joblib.load(os.path.join(MODEL_DIR, "credit_model.pkl"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/loan", methods=["GET", "POST"])
def loan():
    result = None
    risk_score = None

    if request.method == "POST":
        age = int(request.form["age"])
        income = int(request.form["income"])
        loan_amount = int(request.form["loan_amount"])
        credit_history = int(request.form["credit_history"])
        existing_debt = int(request.form["existing_debt"])
        employment_years = int(request.form["employment_years"])

        features = np.array([
            [
                age,
                income,
                loan_amount,
                credit_history,
                existing_debt,
                employment_years
            ]
        ])

        prediction = loan_model.predict(features)[0]
        probability = loan_model.predict_proba(features)[0][1]

        risk_score = round((1 - probability) * 100, 2)

        if prediction == 1:
            result = "Loan Approved ✅ Low Risk"
        else:
            result = "Loan Rejected ❌ High Risk"

        # DATABASE SAVE
        conn = get_db_connection()

        conn.execute("""
        INSERT INTO loan_records
        (age, income, loan_amount, credit_history,
        existing_debt, employment_years, result, risk_score)

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            age,
            income,
            loan_amount,
            credit_history,
            existing_debt,
            employment_years,
            result,
            risk_score
        ))

        conn.commit()
        conn.close()

    return render_template(
        "loan.html",
        result=result,
        risk_score=risk_score
    )


@app.route("/fraud", methods=["GET", "POST"])
def fraud():
    result = None
    fraud_probability = None

    if request.method == "POST":
        amount = int(request.form["amount"])
        hour = int(request.form["hour"])
        location_risk = int(request.form["location_risk"])
        device_risk = int(request.form["device_risk"])
        failed_attempts = int(request.form["failed_attempts"])

        features = np.array([[amount, hour, location_risk, device_risk, failed_attempts]])

        prediction = fraud_model.predict(features)[0]
        probability = fraud_model.predict_proba(features)[0][1]

        fraud_probability = round(probability * 100, 2)

        if prediction == 1:
            result = "Suspicious Transaction Detected ⚠️"
        else:
            result = "Transaction Looks Safe ✅"

        conn = get_db_connection()
        conn.execute("""
        INSERT INTO fraud_records
        (amount, hour, location_risk, device_risk, failed_attempts, result, fraud_probability)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (amount, hour, location_risk, device_risk, failed_attempts, result, fraud_probability))
        conn.commit()
        conn.close()

    return render_template("fraud.html", result=result, fraud_probability=fraud_probability)

@app.route("/credit-score", methods=["GET", "POST"])
def credit_score():
    score = None
    category = None

    if request.method == "POST":
        income = int(request.form["income"])
        repayment = int(request.form["repayment"])
        debt = int(request.form["debt"])
        credit_history = int(request.form["credit_history"])
        late_payments = int(request.form["late_payments"])

        features = np.array([[income, repayment, debt, credit_history, late_payments]])

        score = int(credit_model.predict(features)[0])
        score = max(300, min(900, score))

        if score >= 750:
            category = "Excellent Credit Profile ✅"
        elif score >= 650:
            category = "Good Credit Profile 👍"
        elif score >= 550:
            category = "Average Risk Profile ⚠️"
        else:
            category = "Poor Credit Profile ❌"

        conn = get_db_connection()
        conn.execute("""
        INSERT INTO credit_records
        (income, repayment, debt, credit_history, late_payments, score, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (income, repayment, debt, credit_history, late_payments, score, category))
        conn.commit()
        conn.close()

    return render_template("credit_score.html", score=score, category=category)

@app.route("/dashboard")
def dashboard():
    stats = {
        "total_applications": 1248,
        "approved_loans": 842,
        "fraud_alerts": 37,
        "high_risk_users": 126,
        "avg_credit_score": 684
    }

    recent_alerts = [
        {"type": "Fraud Alert", "user": "TXN-90821", "risk": "High", "amount": 98500},
        {"type": "Loan Risk", "user": "APP-22104", "risk": "Medium", "amount": 450000},
        {"type": "Credit Drop", "user": "USR-77512", "risk": "High", "amount": 0},
        {"type": "Suspicious Login", "user": "USR-11290", "risk": "Low", "amount": 0}
    ]

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_alerts=recent_alerts
    )


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        customer_name = request.form["customer_name"]
        risk_type = request.form["risk_type"]
        risk_score = request.form["risk_score"]
        decision = request.form["decision"]

        reports_dir = os.path.join(BASE_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        file_path = os.path.join(reports_dir, "AI_Risk_Report.pdf")

        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        c.setFillColor(colors.HexColor("#0b2545"))
        c.rect(0, 0, width, height, fill=True)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(60, height - 70, "AI Financial Risk Intelligence Report")

        c.setFont("Helvetica", 11)
        c.drawString(60, height - 95, f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}")

        c.setStrokeColor(colors.HexColor("#00eaff"))
        c.line(60, height - 115, width - 60, height - 115)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(60, height - 160, "Customer Risk Summary")

        c.setFont("Helvetica", 13)
        c.drawString(60, height - 200, f"Customer Name: {customer_name}")
        c.drawString(60, height - 230, f"Risk Type: {risk_type}")
        c.drawString(60, height - 260, f"AI Risk Score: {risk_score}%")
        c.drawString(60, height - 290, f"Final Decision: {decision}")

        c.setFont("Helvetica-Bold", 16)
        c.drawString(60, height - 350, "AI Recommendation")

        c.setFont("Helvetica", 12)

        if float(risk_score) >= 70:
            recommendation = "High risk detected. Manual review and strict verification recommended."
        elif float(risk_score) >= 40:
            recommendation = "Medium risk detected. Additional document verification recommended."
        else:
            recommendation = "Low risk profile. Application can proceed with standard checks."

        text = c.beginText(60, height - 385)
        text.setFillColor(colors.white)
        text.textLines(recommendation)
        c.drawText(text)

        c.setStrokeColor(colors.HexColor("#00eaff"))
        c.rect(50, 120, width - 100, 90)

        c.setFont("Helvetica-Bold", 13)
        c.drawString(70, 180, "Disclaimer")
        c.setFont("Helvetica", 10)
        c.drawString(70, 160, "This report is generated by an AI-based demo risk intelligence system.")
        c.drawString(70, 145, "Final financial decisions should include human review and compliance checks.")

        c.save()

        return send_file(file_path, as_attachment=True)

    return render_template("report.html")

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    user_question = None
    bot_reply = None

    if request.method == "POST":
        user_question = request.form["question"].lower()

        if "loan" in user_question and "reject" in user_question:
            bot_reply = "Your loan may be rejected due to low income, high loan amount, poor credit history, or high existing debt."

        elif "loan" in user_question and "approve" in user_question:
            bot_reply = "Loan approval depends on income, credit history, debt level, employment stability, and repayment capacity."

        elif "fraud" in user_question:
            bot_reply = "A transaction is marked suspicious when amount is unusually high, device risk is high, location risk is high, or failed attempts are repeated."

        elif "credit" in user_question or "score" in user_question:
            bot_reply = "Credit score is calculated using income, repayment score, debt, credit history, and late payments."

        elif "risk" in user_question:
            bot_reply = "Risk score shows how risky a customer or transaction is. Higher score means more manual review is needed."

        else:
            bot_reply = "I can explain loan approval, fraud detection, credit score, and AI risk decisions."

    return render_template(
        "chatbot.html",
        user_question=user_question,
        bot_reply=bot_reply
    )
@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
       return redirect(url_for("login"))


    conn = get_db_connection()

    users = conn.execute("SELECT * FROM users").fetchall()
    applications = conn.execute("SELECT * FROM applications").fetchall()
    fraud_logs = conn.execute("SELECT * FROM fraud_logs").fetchall()

    loan_records = conn.execute("SELECT * FROM loan_records ORDER BY id DESC").fetchall()
    fraud_records = conn.execute("SELECT * FROM fraud_records ORDER BY id DESC").fetchall()
    credit_records = conn.execute("SELECT * FROM credit_records ORDER BY id DESC").fetchall()

    conn.close()

    return render_template(
        "admin.html",
        users=users,
        applications=applications,
        fraud_logs=fraud_logs,
        loan_records=loan_records,
        fraud_records=fraud_records,
        credit_records=credit_records
    )
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)