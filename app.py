import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("missing entries", 403)

        data = lookup(request.form.get("symbol"))
        amount = int(request.form.get("shares"))

        if data is not None:
            user_cash = db.execute(
                f"SELECT cash FROM users WHERE id = {session['user_id']}")
            cost = data['price'] * amount

            if cost <= user_cash[0]['cash']:
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

                db.execute(
                    "INSERT INTO transactions (user_id, symbol, price, shares, occurred_at) VALUES (?, ?, ?, ?, ?)", session[
                        'user_id'], data['symbol'], data['price'], amount, dt_string
                )
                current_amount = db.execute(
                    f"SELECT shares FROM holdings WHERE user_id = ? AND symbol = ?", session['user_id'], data['symbol'])
                if len(current_amount) == 0:
                    db.execute(
                        "INSERT INTO holdings (user_id, symbol, price, shares) VALUES (?, ?, ?, ?)",
                        session['user_id'], data['symbol'], data['price'], amount
                    )
                else:
                    current_amount += amount
                    db.execute(f"UPDATE holdings SET shares = ? where id = ? AND symbol = ?",
                               current_amount, session['user_id'], data['symbol'])

                db.execute(
                    f"UPDATE users SET cash = ? where id = {session['user_id']}",
                    user_cash[0]['cash'] - cost
                )
                return redirect("/")
            else:
                return apology("not enough money", 403)

        else:
            return apology("bad symbol", 403)

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        data = lookup(request.form.get("symbol"))
        if data is not None:
            msg = f"A share of {data['name']}, inc. ({data['symbol']}) costs {usd(data['price'])}"
            return render_template("quote.html", msg=msg)
        else:
            return apology("bad symbol", 403)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not (request.form.get("passwordCheck") == request.form.get("password")):
            return apology("password mismatch", 403)
        # Query database for username
        elif not len(db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))) == 0:
            return apology("username is already taken", 403)

        id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                        request.form.get("username"), generate_password_hash(request.form.get("password")))
        print(id)
        # Remember which user has logged in
        session["user_id"] = id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    buy = db.execute(
        f"SELECT symbol, SUM(shares) FROM buy_txn WHERE id = {session['user_id']} GROUP BY symbol ORDER BY symbol")
    sell = db.execute(
        f"SELECT symbol, SUM(shares) FROM sell_txn WHERE id = {session['user_id']} GROUP BY symbol ORDER BY symbol")
    for i in range(len(buy)):
        buy[i]['symbol']
    total_stocks = {}
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
