import operator
import string
import random
import datetime

from flask import Flask, render_template, request, session, redirect
import bcrypt
from common.database import Database
from models.contests import Contest
from models.golfers import Golfer
from models.lineups import Lineup
from models.users import User

application = Flask(__name__)
application.secret_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


@application.route("/")
def home_page():
    golf = Contest.find_by_sport("PGA")
    golf = filter(lambda x: x.Start_Date > datetime.date.today(), golf)
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
        if session['balance'] >= buy_in:
            User.remove_funds(session["username"], buy_in)
            Lineup.create_lineup(session["contest_id"], session["username"], golfer_1, golfer_2, golfer_3, golfer_4,
                             golfer_5, tiebreak)
            session["contest_id"] = ""
            golf = Contest.find_by_sport("PGA")
            golf = filter(lambda x: x.Start_Date > datetime.date.today(), golf)
            balance = User.get_balance(session['username'])
            return render_template("home_login.html", username=session['username'], balance=balance, golf=golf)
        else:
            text = "Insufficient Funds Please Add Funds to Enter Contest"
            golfers = Golfer.find_golfers()
            golfers = sorted(golfers, key=Golfer.get_name)
            balance = User.get_balance(session['username'])
            return render_template("lineup_entry.html", golfers=golfers, contest_id=session["contest_id"],
                                   username=session['username'], balance=balance, text=text)


@application.route("/addfunds")
def add_funds():
    return render_template("add_funds.html", username=session['username'], balance=session['balance'])


@application.route("/addfunds/<int:buy_in>")
def add_funds_amount(buy_in):
    User.add_funds(session['username'], buy_in)
    return redirect("/")


if __name__ == "__main__":
    application.run(port=4500)
