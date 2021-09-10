import operator
import string
import random
import datetime

from flask import Flask, render_template, request, session, redirect
import bcrypt
import requests
import json
from common.database import Database
from models.contests import Contest
from models.golfers import Golfer
from models.lineups import Lineup
from models.users import User

application = Flask(__name__)
application.secret_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


@application.route("/")
def home_page():
    response = json.loads(requests.get("http://api.ipstack.com/check?access_key=2fe74d1492a0ae71f6423ec9150b3a08&fields=region_code&output=json").text)["region_code"]
    golf = Contest.find_by_sport("PGA")
    golf = filter(lambda x: x.Start_Date > datetime.date.today(), golf)
    golf = filter(lambda x: x.Start_Date <= datetime.date.today() + datetime.timedelta(days=21), golf)
    golf = sorted(golf,key=operator.attrgetter('Start_Date'))
    if session.get('email') is None:        
        return render_template("home.html", golf=golf)
    else:
        balance = User.get_balance(session['username'])
        return render_template("home_login.html", username=session['username'], balance=balance, golf=golf)


@application.route("/upcoming")
def upcoming_lineups():
    username = session['username']
    upcoming = Lineup.get_contests_username(username)
    upcoming = list(filter(lambda x: x.Start_Date > datetime.date.today(), upcoming))
    upcoming = sorted(upcoming,key=operator.attrgetter('Start_Date'))
    balance = User.get_balance(session['username'])
    if len(upcoming) == 0:
        text = "You Do Not Have Any Upcoming Contests"
    else:
        text = ""
    if session.get('email') is None:        
        return render_template("nologin.html", type="Upcoming")
    else:
        return render_template("upcoming.html", text=text, username=session['username'], balance=balance,
                               upcoming=upcoming)


@application.route("/live")
def live_lineups():
    username = session['username']
    live = Lineup.get_contests_username(username)
    live = filter(lambda x: x.Start_Date <= datetime.date.today(), live)
    live = list(filter(lambda x: x.End_Date >= datetime.date.today(), live))
    live = sorted(live, key=operator.attrgetter('Start_Date'))
    balance = User.get_balance(session['username'])
    if len(live) == 0:
        text = "You Do Not Have Any Live Contests"
    else:
        text = ""
    if session.get('email') is None:        
        return render_template("nologin.html", type="Live")
    else:
        return render_template("live.html", username=session['username'], text=text, balance=balance,
                               live=live)


@application.route("/completed")
def previous_lineups():
    username = session['username']
    completed = Lineup.get_contests_username(username)
    completed = filter(lambda x: x.End_Date >= datetime.date.today() - datetime.timedelta(days=14), completed)
    completed = list(filter(lambda x: x.End_Date <= datetime.date.today(), completed))
    completed = sorted(completed, key=operator.attrgetter('Start_Date'))
    balance = User.get_balance(session['username'])
    if len(completed) == 0:
        text = "You Do Not Have Contests From The Last 14 Days"
    else:
        text = ""
    if session.get('email') is None:        
        return render_template("nologin.html", type="Completed")
    else:
        return render_template("completed.html", username=session['username'], text=text, balance=balance,
                               completed=completed)

@application.route("/updatelineup/<string:lineup_id>", methods=['POST'])
def update_lineup(lineup_id):
    golfer_1 = request.form['golfer_1']
    golfer_2 = request.form['golfer_2']
    golfer_3 = request.form['golfer_3']
    golfer_4 = request.form['golfer_4']
    golfer_5 = request.form['golfer_5']
    tiebreak = request.form['two-round']

    if Lineup.validate_lineup(golfer_1, golfer_2, golfer_3, golfer_4, golfer_5) is not True:
        text = "Choose Five Different Golfers"
        golfers = Golfer.find_golfers()
        golfers = sorted(golfers, key=Golfer.get_name)
        selected = []
        for i in golfers:
            if i.Golfer_Name == golfer_1:
                selected.append("selected")
            else:
                selected.append("")
        selected2 = []
        for i in golfers:
            if i.Golfer_Name == golfer_2:
                selected2.append("selected")
            else:
                selected2.append("")
        selected3 = []
        for i in golfers:
            if i.Golfer_Name == golfer_3:
                selected3.append("selected")
            else:
                selected3.append("")
        selected4 = []
        for i in golfers:
            if i.Golfer_Name == golfer_4:
                selected4.append("selected")
            else:
                selected4.append("")
        selected5 = []
        for i in golfers:
            if i.Golfer_Name == golfer_5:
                selected5.append("selected")
            else:
                selected5.append("")
        golfers1 = zip(golfers, selected)
        golfers2 = zip(golfers, selected2)
        golfers3 = zip(golfers, selected3)
        golfers4 = zip(golfers, selected4)
        golfers5 = zip(golfers, selected5)
        balance = User.get_balance(session['username'])
        return render_template("lineup_update.html", tiebreak=tiebreak,golfers=golfers1, golfers2=golfers2, golfers3=golfers3,
                               golfers4=golfers4, golfers5=golfers5,
                               username=session['username'], balance=balance, text=text, lineup_id = lineup_id)
    else:
        Lineup.update_lineup(lineup_id, golfer_1, golfer_2, golfer_3, golfer_4,
                                 golfer_5, tiebreak)
        session["contest_id"] = ""
        return redirect('/')

@application.route("/deletelineup/<string:lineup_id>")
def delete_lineup(lineup_id):
    Lineup.delete_lineup(lineup_id)
    return redirect("/upcoming")


@application.route("/editlineup/<string:lineup_id>")
def edit_lineup(lineup_id):
    lineup = Lineup.get_lineup(lineup_id)
    tiebreak = lineup[0].Tiebreak
    golfers = Golfer.find_golfers()
    golfers = sorted(golfers, key=Golfer.get_name)
    selected = []
    for i in golfers:
        if i.Golfer_Name == lineup[0].Golfer_1:
            selected.append("selected")
        else:
            selected.append("")
    selected2 = []
    for i in golfers:
        if i.Golfer_Name == lineup[0].Golfer_2:
            selected2.append("selected")
        else:
            selected2.append("")
    selected3 = []
    for i in golfers:
        if i.Golfer_Name == lineup[0].Golfer_3:
            selected3.append("selected")
        else:
            selected3.append("")
    selected4 = []
    for i in golfers:
        if i.Golfer_Name == lineup[0].Golfer_4:
            selected4.append("selected")
        else:
            selected4.append("")
    selected5 = []
    for i in golfers:
        if i.Golfer_Name == lineup[0].Golfer_5:
            selected5.append("selected")
        else:
            selected5.append("")
    golfers1 = zip(golfers, selected)
    golfers2 = zip(golfers, selected2)
    golfers3 = zip(golfers, selected3)
    golfers4 = zip(golfers, selected4)
    golfers5 = zip(golfers, selected5)
    balance = User.get_balance(session['username'])
    return render_template("lineup_update.html", tiebreak=tiebreak, golfers=golfers1, golfers2=golfers2, golfers3=golfers3,
                           golfers4=golfers4, golfers5=golfers5, balance=balance, lineup_id = lineup_id)

@application.before_first_request
def initialize_database():
    Database.initialize()


@application.route("/login")
def login_page():
    return render_template("login.html", text="")


@application.route("/register")
def register_page():
    return render_template("register.html", text="")


@application.route("/loginvalid", methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password'].encode("utf-8")
    hashed = User.get_by_email(email).password

    if bcrypt.checkpw(password, hashed):
        User.login(email)
        user = User.get_by_email(email)
        session['username'] = user.username
        return redirect('/')
    else:
        session['email'] = None
        return render_template("login.html", text="Incorrect username or password")


@application.route("/registeruser", methods=['POST'])
def register():
    email = request.form['email']
    username = request.form['username']
    name = request.form['name']
    password = bcrypt.hashpw(request.form['password'].encode("utf-8"), bcrypt.gensalt())

    if User.login_valid(email, password) is not True:
        User.register(email, username, name, password)
        User.login(email)
        session['username'] = username
        balance = User.get_balance(session['username'])
        golf = Contest.find_by_sport("PGA")
        golf = filter(lambda x: x.Start_Date > datetime.date.today(), golf)
        return render_template("home_login.html", username=session['username'], balance=balance, golf=golf)
    else:
        session['email'] = None
        return render_template("login.html", text="Incorrect username or password")


@application.route("/contests/<string:contest_id>")
def lineup_entry(contest_id):
    session["contest_id"] = contest_id
    golfers = Golfer.find_golfers()
    golfers = sorted(golfers, key=Golfer.get_name)
    balance = User.get_balance(session['username'])
    return render_template("lineup_entry.html", golfers=golfers, contest_id=session["contest_id"],
                           username=session['username'], balance=balance)


@application.route("/contest_entries/<string:contest_id>")
def contest_entries(contest_id):
    lineups = Lineup.get_entries(contest_id)
    lineups = sorted(lineups, key=operator.attrgetter("Score"))
    contest = Contest.get_from_mongo(contest_id)
    balance = User.get_balance(session['username'])
    return render_template("contest_entries.html", lineups=lineups, contest=contest, username=session['username'],
                           balance=balance)


@application.route("/enterlineup", methods=['POST'])
def enter_lineup():
    golfer_1 = request.form['golfer_1']
    golfer_2 = request.form['golfer_2']
    golfer_3 = request.form['golfer_3']
    golfer_4 = request.form['golfer_4']
    golfer_5 = request.form['golfer_5']
    tiebreak = request.form['two-round']

    if Lineup.validate_lineup(golfer_1, golfer_2, golfer_3, golfer_4, golfer_5) is not True:
        text = "Choose Five Different Golfers"
        golfers = Golfer.find_golfers()
        golfers = sorted(golfers, key=Golfer.get_name)
        balance = User.get_balance(session['username'])
        return render_template("lineup_entry.html", golfers=golfers, contest_id=session["contest_id"],
                               username=session['username'], balance=balance, text=text)
    else:
        buy_in = Contest.get_contest_buyin(session["contest_id"])
        buy_in = int(buy_in)
        balance = User.get_balance(session['username'])
        if balance >= buy_in:
            User.remove_funds(session["username"], buy_in)
            Lineup.create_lineup(session["contest_id"], session["username"], golfer_1, golfer_2, golfer_3, golfer_4,
                             golfer_5, tiebreak)
            session["contest_id"] = ""
            return redirect('/')
        else:
            text = "Insufficient Funds Please Add Funds to Enter Contest"
            golfers = Golfer.find_golfers()
            golfers = sorted(golfers, key=Golfer.get_name)
            balance = User.get_balance(session['username'])
            return render_template("lineup_entry.html", golfers=golfers, contest_id=session["contest_id"],
                                   username=session['username'], balance=balance, text=text)


@application.route("/addfunds")
def add_funds():
    balance = User.get_balance(session['username'])
    return render_template("add_funds.html", username=session['username'], balance=balance)


@application.route("/addfunds/<int:buy_in>")
def add_funds_amount(buy_in):
    User.add_funds(session['username'], buy_in)
    return redirect("/")

@application.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('email', None)
   return redirect("/")


if __name__ == "__main__":
    application.run()
