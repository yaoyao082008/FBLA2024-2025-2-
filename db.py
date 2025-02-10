import firebase_admin
from firebase_admin import firestore, credentials
from google.oauth2 import service_account
from firebase_admin import auth
import datetime

creds= credentials.Certificate("dec_creds.json")

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
    return new_user(email, name)

def new_user(email, name):
    ref = db.collection("users").document(email)

    data = {
        "email": email,
        "name": name,
        "incomes": [],
        "expenses": [],
        "balance": 0,
        "months": [0 for i in range(12)],
        "income_types": {"Cash": 0, "Check": 0, "Wire": 0, "Card": 0},
        "expense_types": {"Cash": 0, "Check": 0, "Wire": 0, "Card": 0}
        }

    ref.set(data)
    return data

def update_incomes(email, incomes):
    #name, type, amt, date
    ref = db.collection("users").document(email)
    data = {}
    types = {"Cash": 0, "Check": 0, "Wire": 0, "Card":0}
    print(types)
    for income in incomes:
        data[incomes[income][0]] = {
            'type': incomes[income][1],
            'amt': incomes[income][2],
            'date': incomes[income][3]
            }
        types[incomes[income][1]] += 1

    
    ref.update({"incomes": data, "income_types": types})
    

def update_expenses(email, expenses):
    #name, type, amt, date
    ref = db.collection("users").document(email)
    data = {}
    types = {"Cash": 0, "Check": 0, "Wire": 0, "Card": 0}
    for expense in expenses:
        data[expenses[expense][0]]=  {
            'type': expenses[expense][1],
            'amt': expenses[expense][2],
            'date': expenses[expense][3]
            }
        types[expenses[expense][1]] += 1
            
    ref.update({"expenses": data, "expense_types": types})
    

def update_balance(email):
    ref = db.collection("users").document(email)
    usr = get_user(email)
    incomes = usr['incomes']


    months = [0 for i in range(13)] #indexes 1 - 12 represent current months' income while index 0 is all past years income
    #finds total income
    for i in incomes:
        curr_amount = float(incomes[i]["amt"])
        #dates incomes by month , [YYYY,M,D] where YYYY is index 0
        date = [int(d) for d in incomes[i]["date"].split("-")]
        #current month of the transaction
        yearOfTransaction=date[0]
        
        if yearOfTransaction == 2025:
            #current month of transaction
            curr_month = date[1]
            months[curr_month] = months[curr_month] + curr_amount
        else:
            #tally up last years income
            months[0] += curr_amount


        
    expenses = usr['expenses']
    #finds total expenses
    for i in expenses:
        #transaction amount
        curr_amount = float(expenses[i]["amt"])        
        #dates expenses by month
        date = [int(d) for d in expenses[i]["date"].split("-")]
        #if date[0] == current_year:
        yearOfTransaction=date[0]
        
        if yearOfTransaction == 2025:
            #current month of transaction
            curr_month=date[1]
            months[curr_month] = months[curr_month] - curr_amount
        else:
            #tally up last years expenses(negative)
            months[0] -= curr_amount
    
    netIncome = months.copy()
    
    for i in range(1,len(months)):
        months[i] += months[i-1]
        
    
    #balance in december is equal to current balance
    bal = months[12]

    data = {
        "balance": bal,
        "months": months,
        "netIncome":netIncome,
        }

    #print(months)
    ref.update(data)
