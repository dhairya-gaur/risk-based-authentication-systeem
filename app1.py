from flask import Flask,render_template,request,redirect,session,url_for
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "rba_project_secret"


# -----------------
# DATABASE FUNCTION
# -----------------

def get_user(username,password):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
    )

    user = cursor.fetchone()

    conn.close()

    return user


# -----------------
# EMAIL OTP
# -----------------

def send_otp(email,otp):

    sender_email = "deepakgaur9115@gmail.com"
    app_password = "aewjivkhjmgpmtwu"

    subject = "Risk Based Authentication OTP"

    body = f"""
Your OTP is:

{otp}

Do not share with anyone.
"""

    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = email

    server = smtplib.SMTP('smtp.gmail.com',587)

    server.starttls()
    server.login(sender_email,app_password)

    server.sendmail(
        sender_email,
        email,
        msg.as_string()
    )

    server.quit()


# -----------------
# HOME LOGIN
# -----------------

@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        user=get_user(username,password)

        if not user:
            return "Invalid Credentials"

        session["user"]=user[1]

        # ------------------
        # RISK CALCULATION
        # ------------------

        risk_score=0

        if request.form.get("new_device"):
            risk_score += 40

        if request.form.get("new_location"):
            risk_score += 30

        if request.form.get("failed_attempt"):
            risk_score += 30

        session["risk_score"]=risk_score

        # LOW RISK
        if risk_score < 30:

            session["method"]="Normal Login"

            return redirect("/dashboard")

        # MEDIUM RISK
        elif risk_score < 60:

            session["method"]="Security Question"

            session["question"]=user[4]
            session["answer"]=user[5]

            return redirect("/security")

        # HIGH RISK
        else:

            otp=random.randint(100000,999999)

            session["otp"]=str(otp)

            session["method"]="Email OTP"

            #send_otp(user[3],otp)
            try:
                send_otp(user[3],otp)
                print("email sent successfully")
            except Exception as e:
                print("email error:",e) 
            print("Generated OTP =", otp)

            return redirect("/otp")

    return render_template("login.html")


# -----------------
# SECURITY QUESTION
# -----------------

@app.route("/security",methods=["GET","POST"])
def security():

    if request.method=="POST":

        answer=request.form["answer"].lower()

        if answer==session["answer"].lower():

            return redirect("/dashboard")

        else:

            otp=random.randint(100000,999999)

            session["otp"]=str(otp)

            return redirect("/otp")

    return render_template(
        "security.html",
        question=session["question"]
    )


# -----------------
# OTP
# -----------------

@app.route("/otp",methods=["GET","POST"])
def otp():

    if request.method=="POST":

        entered=request.form["otp"]

        if entered==session["otp"]:

            return redirect("/dashboard")

        else:

            return "Invalid OTP"

    return render_template("otp.html")


# -----------------
# DASHBOARD
# -----------------

@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html",
        user=session["user"],
        risk=session["risk_score"],
        method=session["method"]
    )


if __name__=="__main__":
    app.run(debug=True)