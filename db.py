# module imports
import firebase_admin
from firebase_admin import firestore, credentials
from google.oauth2 import service_account
from firebase_admin import auth
import datetime

# database credentials
creds = credentials.Certificate("dec_creds.json")

# firebase initialization
app = firebase_admin.initialize_app(creds)
db = firestore.client()
current_year = int(datetime.datetime.today().strftime("%Y"))

# get user from database
def get_user(email, name=None):
    ref = db.collection("users").stream()
    for usr in ref:
        usr = usr.to_dict()
        try:
            if usr["email"] == email:
                return usr # return user if exists
        except Exception as e:
            pass

    return new_user(email, name) # return user object

# create new user in database
def new_user(email, name):
    ref = db.collection("users").document(email)

    # initialize data
    data = {
        "email": email,
        "name": name,
        "incomes": [],
        "expenses": [],
        "balance": 0,
        "months": [0 for i in range(13)], #index is 0 is all past income and expense while 1-12 is months of the current year
        "netIncome":[0 for i in range(13)], #net income for each month
        "income_types": {"Cash": 0, "Check": 0, "Wire": 0, "Card": 0},
        "expense_types": {"Cash": 0, "Check": 0, "Wire": 0, "Card": 0}
        }

    ref.set(data) # update in database
    return data

# update incomes
def update_incomes(email, incomes):
    ref = db.collection("users").document(email)

    # initialize values
    data = {}
    types = {"Cash": 0, "Check": 0, "Wire": 0, "Card":0}

    # update local incomes
    for income in incomes:
        data[incomes[income][0]] = {
            'type': incomes[income][1],
            'amt': incomes[income][2],
            'date': incomes[income][3]
            }
        types[incomes[income][1]] += 1

    # update in database
    ref.update({"incomes": data, "income_types": types})
    
# update expenses
def update_expenses(email, expenses):
    ref = db.collection("users").document(email)

    # initialize values
    data = {}
    types = {"Cash": 0, "Check": 0, "Wire": 0, "Card": 0}

    # update local expenses
    for expense in expenses:
        data[expenses[expense][0]]=  {
            'type': expenses[expense][1],
            'amt': expenses[expense][2],
            'date': expenses[expense][3]
            }
        types[expenses[expense][1]] += 1
    
    # update in database
    ref.update({"expenses": data, "expense_types": types})
    
# updata balance
def update_balance(email):
    ref = db.collection("users").document(email)
    usr = get_user(email)
    incomes = usr['incomes']

    months = [0 for i in range(13)] # 0: all past years & 1 - 12: current month income

    # calculates total incomes
    for i in incomes:
        curr_amount = float(incomes[i]["amt"])

        # income dates
        date = [int(d) for d in incomes[i]["date"].split("-")]

        # current income month
        yearOfTransaction = date[0]
        
        if yearOfTransaction == 2025:
            # current month expense
            curr_month = date[1]
            months[curr_month] = months[curr_month] + curr_amount
        else:
            # calculate last year income
            months[0] += curr_amount


        
    expenses = usr['expenses']
    # calculate total expenses
    for i in expenses:
        curr_amount = float(expenses[i]["amt"]) 

        # expense dates
        date = [int(d) for d in expenses[i]["date"].split("-")]

        # current expense year
        yearOfTransaction = date[0]
        
        if yearOfTransaction == current_year:
            # current month expense
            curr_month=date[1]
            months[curr_month] = months[curr_month] - curr_amount
        else:
            # previous year expenses
            months[0] -= curr_amount
    

    netIncome = months.copy()
    
    for i in range(1,len(months)):
        months[i] += months[i-1]
        
    
    # december balance = net balance
    bal = months[12]

    data = {
        "balance": bal,
        "months": months,
        "netIncome":netIncome,
        }

    # update in database
    ref.update(data)
