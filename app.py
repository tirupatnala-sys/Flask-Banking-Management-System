from flask import Flask, request, render_template, redirect
from db import getConnection
from autoGenration import genrateTransactionId, genrateAccNo

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/createCustomer")
def createCustomerFun():
    return render_template("createCustomer.html")


@app.route("/editCustomer/<caccno>", methods=["GET", "POST"])
def editCustomer(caccno):

    conn = getConnection()
    cmd = conn.cursor(dictionary=True)

    cmd.execute("""
        SELECT cname, cmobile, cemail, accno, password
        FROM customer
        WHERE accno=%s
    """, (caccno,))

    data = cmd.fetchone()
    conn.close()

    return render_template("editCustomer.html", customer=data)


@app.route("/makeTransaction")
def makeTransaction():
    return render_template("transaction.html")


@app.route("/insertData", methods=["POST"])
def insertData():

    data = request.form

    cname = data["name"]
    cmobile = data["mobile"]
    cemail = data["email"]
    caccno = genrateAccNo()
    cbalance = data["balance"]
    password = "Test@123"

    conn = getConnection()
    cmd = conn.cursor()

    cmd.execute("""
        INSERT INTO customer
        (cname, cmobile, cemail, accno, balance, password)
        VALUES
        (%s,%s,%s,%s,%s,%s)
    """, (cname, cmobile, cemail, caccno, cbalance, password))

    conn.commit()
    conn.close()

    return redirect("/adminDashboard")


@app.route("/deleteCustomer/<caccno>", methods=["GET","POST"])
def deleteCustomer(caccno):

    conn = getConnection()
    cmd = conn.cursor()

    cmd.execute("DELETE FROM customer WHERE accno=%s", (caccno,))

    conn.commit()
    conn.close()

    return redirect("/adminDashboard")


@app.route("/updateCustomer", methods=["POST"])
def updateCustomer():

    data = request.form

    caccno = data["caccno"]
    uname = data["uname"]
    umobile = data["umobile"]
    uemail = data["uemail"]
    upassword = data["upassword"]

    conn = getConnection()
    cmd = conn.cursor(dictionary=True)

    cmd.execute("""
        SELECT cname, cmobile, cemail, password
        FROM customer
        WHERE accno=%s
    """, (caccno,))

    d = cmd.fetchone()

    if uname == "":
        uname = d["cname"]

    if umobile == "":
        umobile = d["cmobile"]

    if uemail == "":
        uemail = d["cemail"]

    if upassword == "":
        upassword = d["password"]

    cmd = conn.cursor()

    cmd.execute("""
        UPDATE customer
        SET
        cname=%s,
        cmobile=%s,
        cemail=%s,
        password=%s
        WHERE accno=%s
    """, (uname, umobile, uemail, upassword, caccno))

    conn.commit()
    conn.close()

    return redirect("/adminDashboard")
@app.route("/adminDashboard", methods=["GET", "POST"])
def viewAllCustomers():

    conn = getConnection()
    cmd = conn.cursor(dictionary=True)

    cmd.execute("""
        SELECT sno,cname,cmobile,cemail,accno,balance
        FROM customer
    """)

    result = cmd.fetchall()
    conn.close()

    return render_template("adminDashboard.html", data=result)


@app.route("/adminLogin", methods=["POST"])
def adminLogin():

    data = request.form

    username = data["username"]
    password = data["password"]

    conn = getConnection()
    cmd = conn.cursor()

    cmd.execute("""
        SELECT *
        FROM admin
        WHERE username=%s AND password=%s
    """, (username, password))

    result = cmd.fetchone()
    conn.close()

    if result:
        return redirect("/adminDashboard")
    else:
        return render_template(
            "index.html",
            message="Invalid Username or Password"
        )


@app.route("/transaction", methods=["POST"])
def transaction():

    data = request.form

    tranType = data["t_type"]
    caccno = data["caccno"]
    amount = float(data["amount"])

    tid = genrateTransactionId()

    conn = getConnection()
    cmd = conn.cursor(dictionary=True)

    cmd.execute(
        "SELECT balance FROM customer WHERE accno=%s",
        (caccno,)
    )

    result = cmd.fetchone()

    if result is None:
        conn.close()
        return "Account Number Not Found"

    oldBalance = float(result["balance"])

    if tranType == "deposit":
        newBalance = oldBalance + amount
    else:

        if amount > oldBalance:
            conn.close()
            return "Insufficient Balance"

        newBalance = oldBalance - amount

    cmd = conn.cursor()

    cmd.execute(
        "UPDATE customer SET balance=%s WHERE accno=%s",
        (newBalance, caccno)
    )

    cmd.execute("""
        INSERT INTO transactions
        (transactionid,
        transactiontype,
        accno,
        balancebeforeT,
        balanceafterT)

        VALUES
        (%s,%s,%s,%s,%s)
    """,
    (
        tid,
        tranType,
        caccno,
        oldBalance,
        newBalance
    ))

    conn.commit()
    conn.close()

    return redirect("/adminDashboard")


if __name__ == "__main__":
    app.run(debug=True)    