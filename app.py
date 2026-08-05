from flask import Flask, request, render_template, redirect, session
from db import getConnection
from autoGenration import genrateTransactionId, genrateAccNo

app = Flask(__name__)

app.secret_key = "BankManagementSystem123"


# HOME
@app.route("/")
def home():
    return render_template("index.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customer")
    totalCustomers = cursor.fetchone()[0]


    cursor.execute("SELECT COUNT(*) FROM transactions")
    totalTransactions = cursor.fetchone()[0]


    cursor.execute("SELECT SUM(balance) FROM customer")
    totalBalance = cursor.fetchone()[0]


    if totalBalance is None:
        totalBalance = 0


    cursor.execute("""
        SELECT
        transactionid,
        transactiontype,
        accno,
        balancebeforeT,
        balanceafterT,
        transactiondate,
        transactiontime
        FROM transactions
        ORDER BY sno DESC
        LIMIT 5
    """)

    recentTransactions = cursor.fetchall()


    conn.close()


    return render_template(
        "dashboard.html",
        totalCustomers=totalCustomers,
        totalTransactions=totalTransactions,
        totalBalance=totalBalance,
        recentTransactions=recentTransactions
    )



# CREATE CUSTOMER PAGE
@app.route("/createCustomer")
def createCustomerFun():

    return render_template("createCustomer.html")



# INSERT CUSTOMER
@app.route("/insertData", methods=["POST"])
def insertData():

    data = request.form


    cname = data["name"]
    cmobile = data["mobile"]
    cemail = data["email"]
    cbalance = data["balance"]


    caccno = genrateAccNo()

    password = "Test@123"



    conn = getConnection()

    cmd = conn.cursor()



    cmd.execute("""
        INSERT INTO customer
        (
        cname,
        cmobile,
        cemail,
        accno,
        balance,
        password
        )

        VALUES
        (%s,%s,%s,%s,%s,%s)

    """,
    (
        cname,
        cmobile,
        cemail,
        caccno,
        cbalance,
        password
    ))


    conn.commit()

    conn.close()


    return redirect("/dashboard")



# EDIT CUSTOMER

@app.route("/editCustomer/<caccno>")
def editCustomer(caccno):

    conn = getConnection()

    cmd = conn.cursor(dictionary=True)


    cmd.execute("""
        SELECT *
        FROM customer
        WHERE accno=%s
    """,(caccno,))


    customer = cmd.fetchone()


    conn.close()


    return render_template(
        "editCustomer.html",
        customer=customer
    )



# UPDATE CUSTOMER

@app.route("/updateCustomer", methods=["POST"])
def updateCustomer():

    data=request.form


    caccno=data["caccno"]

    cname=data["uname"]

    mobile=data["umobile"]

    email=data["uemail"]

    password=data["upassword"]



    conn=getConnection()

    cmd=conn.cursor()


    cmd.execute("""
        UPDATE customer
        SET
        cname=%s,
        cmobile=%s,
        cemail=%s,
        password=%s

        WHERE accno=%s

    """,
    (
        cname,
        mobile,
        email,
        password,
        caccno
    ))


    conn.commit()

    conn.close()


    return redirect("/dashboard")
# DELETE CUSTOMER

@app.route("/deleteCustomer/<caccno>")
def deleteCustomer(caccno):

    conn = getConnection()

    cmd = conn.cursor()


    cmd.execute(
        "DELETE FROM customer WHERE accno=%s",
        (caccno,)
    )


    conn.commit()

    conn.close()


    return redirect("/dashboard")



# ADMIN DASHBOARD CUSTOMER LIST

@app.route("/adminDashboard")
def viewAllCustomers():

    conn = getConnection()

    cmd = conn.cursor(dictionary=True)


    cmd.execute("""
        SELECT
        sno,
        cname,
        cmobile,
        cemail,
        accno,
        balance

        FROM customer
    """)


    data = cmd.fetchall()


    conn.close()


    return render_template(
        "adminDashboard.html",
        data=data
    )



# ADMIN LOGIN

@app.route("/adminLogin", methods=["POST"])
def adminLogin():

    data=request.form


    username=data["username"]

    password=data["password"]


    conn=getConnection()

    cmd=conn.cursor()


    cmd.execute("""
        SELECT *
        FROM admin
        WHERE username=%s
        AND password=%s

    """,
    (
        username,
        password
    ))


    result=cmd.fetchone()


    conn.close()



    if result:

        session["admin"]=username

        return redirect("/dashboard")


    else:

        return render_template(
            "index.html",
            message="Invalid Username or Password"
        )




# MAKE TRANSACTION PAGE

@app.route("/makeTransaction")
def makeTransaction():

    return render_template(
        "transaction.html"
    )





# DEPOSIT / WITHDRAW

@app.route("/transaction", methods=["POST"])
def transaction():


    data=request.form


    tranType=data["t_type"]

    accno=data["caccno"]

    amount=float(data["amount"])



    tid=genrateTransactionId()



    conn=getConnection()

    cmd=conn.cursor(dictionary=True)



    cmd.execute(
        "SELECT balance FROM customer WHERE accno=%s",
        (accno,)
    )


    result=cmd.fetchone()



    if result is None:

        conn.close()

        return "Account Not Found"



    oldBalance=float(result["balance"])



    if tranType=="deposit":

        newBalance=oldBalance+amount



    elif tranType=="withdraw":


        if amount>oldBalance:

            conn.close()

            return "Insufficient Balance"



        newBalance=oldBalance-amount



    cmd=conn.cursor()



    cmd.execute("""
        UPDATE customer
        SET balance=%s
        WHERE accno=%s

    """,
    (
        newBalance,
        accno
    ))



    cmd.execute("""
        INSERT INTO transactions
        (
        transactionid,
        transactiontype,
        accno,
        balancebeforeT,
        balanceafterT
        )

        VALUES
        (%s,%s,%s,%s,%s)

    """,
    (
        tid,
        tranType,
        accno,
        oldBalance,
        newBalance
    ))



    conn.commit()

    conn.close()



    return redirect("/dashboard")





# VIEW TRANSACTIONS

@app.route("/viewTransactions")
def viewTransactions():


    conn=getConnection()


    cmd=conn.cursor(dictionary=True)



    cmd.execute("""
        SELECT
        transactionid,
        transactiontype,
        accno,
        balancebeforeT,
        balanceafterT,
        transactiondate,
        transactiontime

        FROM transactions

        ORDER BY sno DESC

    """)



    transactions=cmd.fetchall()



    conn.close()



    return render_template(
        "viewTransactions.html",
        transactions=transactions
    )





if __name__=="__main__":

    app.run(debug=True)    