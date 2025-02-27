# module imports
from db import *
from db import get_user
from flask import Flask, render_template, request, session, redirect
from functools import wraps
import datetime
import json

# Initialize
app = Flask(__name__)
app.secret_key = "syIyJRgEcuUQ8XI9iG-fA3slxHTBMmk"
app.permanent_session_lifetime = datetime.timedelta(days=31)

# wrapper function (checks if user is logged in)
def logged_in_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if session.get("user") is None:
            return redirect('/')
        return func(*args, **kwargs)

    return decorator

# index page
@app.route('/')
def home():
    return render_template("index.html", user=session.get("user"))

# login page
@app.route('/login', methods=["POST"])
def login():
    user = json.loads(request.form.get("creds")) # gets user login info
    session["user"] = get_user(user["email"], user["displayName"]) # stores user in browser session
    session['email'] = user['email']
    session.permanent = True
    session.modified = True
    return ""

# dashboard page
@app.route('/dashboard')
@logged_in_required
def dashboard():
    return render_template("transactions.html", user=session.get("user"))

# analyze page
@app.route('/analyze')
@logged_in_required
def analyze():
    return render_template("analyze.html", user=session.get("user"))

# income updates page
@app.route('/update_income_transactions', methods=["POST"])
def update_income_transactions():
    # get all class names, types, and numerical grades
    income_names = request.form.getlist("income_names[]")
    income_types = request.form.getlist("income_types[]")
    income_amounts = request.form.getlist("income_amounts[]")
    income_date = request.form.getlist("income_date[]")

    # on invalid amount return error
    for i in income_amounts:
        i = float(i)
        if i < 0:
            return 400
        
    # on invalid date return current date
    for i in range(len(income_date)):
        if income_date[i] == "":
            income_date[i]=datetime.datetime.today().strftime("%Y-%m-%d")

    # dictionary to store incomes
    incomes = {}

    # update incomes
    for i in range(len(income_names)):
        name = income_names[i]
        incomes[name] = [name, income_types[i], income_amounts[i], income_date[i]]

    # update incomes in database
    update_incomes(session.get("email"), incomes)
    update_balance(session.get("email"))

    # update local user
    session["user"] = get_user(session.get("email"))

    return "" # server success

# update expenses page
@app.route('/update_expense_transactions', methods=["POST"])
def update_expense_transactions():
    # get all class names, types, and numerical grades
    expense_names = request.form.getlist("expense_names[]")
    expense_types = request.form.getlist("expense_types[]")
    expense_amounts = request.form.getlist("expense_amounts[]")
    expense_date = request.form.getlist("expense_date[]")

    # on invalid expense return error
    for i in expense_amounts:
        i = float(i)
        if i < 0:
            return 400
    
    # on invalid expense date return error
    for i in range(len(expense_date)):
        if expense_date[i] == "":
            expense_date[i]=datetime.datetime.today().strftime("%Y-%m-%d")

    expenses = {} # dictionary to store expenses

    # update expenses
    for i in range(len(expense_names)):
        name = expense_names[i]
        expenses[name] = [name, expense_types[i], expense_amounts[i], expense_date[i]]

    # updates expenses in database
    update_expenses(session.get("email"), expenses)
    update_balance(session.get("email"))

    # update local user
    session["user"] = get_user(session.get("email"))

    return "" # server success

# logout link
@app.route('/logout', methods=["POST"])
@logged_in_required
def logout():
    session.clear() # clear browser session
    session.modified = True

    return "" # server success

# run project
if __name__ == "__main__":
    app.run(debug=True)

