from helpers import apology, login_required, lookup, usd
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from tempfile import mkdtemp
from flask_session import Session
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from cs50 import SQL
from datetime import datetime
import os
import re


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

    # Fetch the necessary data to display
    user_data = db.execute(
        f"SELECT symbol, name, price, shares FROM holdings WHERE user_id = {session['user_id']}")

    cash = db.execute(f"SELECT cash from users WHERE id = {session['user_id']}")[
        0]['cash']

    # Calculate user total money
    total = cash
    for row in user_data:
        total += (row['price'] * row['shares'])

    # Display index page with the necessary data
    return render_template("index.html", data=user_data, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("symbol") or not request.form.get("shares"):
            return jsonify(msg="Missing entries", code=400, redirect=False)

        # Receive API response in data
        data = lookup(request.form.get("symbol"))
        amount = int(request.form.get("shares"))

        # Check API response for enterd symbol
        if data is not None:

            # Fethc user money
            user_cash = db.execute(
                f"SELECT cash FROM users WHERE id = {session['user_id']}")

            # Calculate the total cost
            cost = data['price'] * amount

            # Check if the user can afford the cost
            if cost <= user_cash[0]['cash']:

                # Get the current time & date
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

                # Insert the new transaction
                db.execute(
                    "INSERT INTO transactions (user_id, symbol, price, shares, occurred_at) VALUES (?, ?, ?, ?, ?)",
                    session['user_id'], data['symbol'], data['price'], amount, dt_string
                )

                # Check if user has shares of the same stocks
                current_amount = db.execute(
                    f"SELECT shares FROM holdings WHERE user_id = ? AND symbol = ?",
                    session['user_id'], data['symbol'])

                # Insert new stock data to the user holdings table
                if len(current_amount) == 0:
                    db.execute(
                        "INSERT INTO holdings (user_id, symbol, name,  price, shares) VALUES (?, ?, ?, ?, ?)",
                        session['user_id'], data['symbol'], data["name"], data['price'], amount
                    )

                # Update user's number of shares of the stock
                else:
                    db.execute(f"UPDATE holdings SET shares = ? where user_id = ? AND symbol = ?",
                               current_amount[0]['shares'] + amount, session['user_id'], data['symbol'])

                # Withdraw the cost from user's money
                db.execute(
                    f"UPDATE users SET cash = ? where id = ?",
                    user_cash[0]['cash'] - cost, session['user_id']
                )

                # Redirect the user to the Homepage
                return redirect("/")

            else:
                return jsonify(msg="Not enough money", code=400, redirect=False)

        else:
            return jsonify(msg="Wrong symbol", code=400, redirect=False)

    else:
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Fetch all user's taransactions to display
    user_data = db.execute(
        f"SELECT symbol, price, shares, occurred_at FROM transactions WHERE user_id = {session['user_id']}")

    return render_template("history.html", data=user_data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return jsonify(msg="Must provide username", code=400, redirect=False)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return jsonify(msg="Must provide password", code=400, redirect=False)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return jsonify(msg="Invalid username and/or password", code=400, redirect=False)

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
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Receive API response in data
        data = lookup(request.form.get("symbol"))

        # Check API response for enterd symbol
        if data is not None:
            msg = f"A share of {data['name']},({data['symbol']}) costs {usd(data['price'])}"
            return jsonify(msg=msg, code=200)

        else:
            return jsonify(msg="Wrong symbol", code=400)

    else:
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return jsonify(msg="Must provide username", code=400, redirect=False)

        # Query database for username match
        elif not len(db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))) == 0:
            return jsonify(msg="Username is already taken", code=400, redirect=False)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return jsonify(msg="Must provide password", code=400, redirect=False)

        # Ensure password is strong enough
        elif not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', request.form.get("password")):
            return jsonify(msg="Weak password must contain: At least 8 characters, uppercase letters: A-Z, lowercase letters: a-z, numbers: 0-9, any of the special characters: @#$%^&+=", code=400, redirect=False)

        # Ensure password's fields matches
        elif not (request.form.get("passwordCheck") == request.form.get("password")):
            return jsonify(msg="Password mismatch", code=400, redirect=False)

        # Insert the new user's data to the DataBase
        id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                        request.form.get("username"), generate_password_hash(request.form.get("password")))

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

    # Fetch for user's stocks symbols
    db_response = db.execute(
        f"SELECT symbol, shares FROM holdings WHERE user_id = {session['user_id']}")

    # Parse Query response
    stocks = []
    stocks_dict = {}
    for row in db_response:
        stocks.append(row['symbol'])
        stocks_dict[row['symbol']] = row['shares']

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check for user's input
        if not request.form.get("symbol") or not request.form.get("shares"):
            return jsonify(msg="Missing entries", code=400, redirect=False)

        # Validate stock name & number of shares
        if request.form.get("symbol") not in stocks or int(request.form.get("shares")) > stocks_dict[request.form.get("symbol")]:
            return jsonify(msg="Not vaild operation", code=400, redirect=False)

        # Receive API response in data to get the current price
        data = lookup(request.form.get("symbol"))

        # Get the current time & date
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        # Insert the new transaction
        db.execute(
            "INSERT INTO transactions (user_id, symbol, price, shares, occurred_at) VALUES (?, ?, ?, ?, ?)",
            session['user_id'], data['symbol'], data['price'],
            int(request.form.get("shares")) * -1, dt_string
        )

        # Check for user's number of current shares
        current_amount = db.execute(
            "SELECT shares FROM holdings WHERE user_id = ? AND symbol = ?",
            session['user_id'], data['symbol'])

        # Update user's number of shares of the stock
        db.execute(f"UPDATE holdings SET shares = ? where user_id = ? AND symbol = ?",
                   current_amount[0]['shares'] - int(request.form.get("shares")), session['user_id'], data['symbol'])

        # Fetch user's cash
        user_cash = db.execute(
            f"SELECT cash FROM users WHERE id = {session['user_id']}")

        # Calculate the price of sold stocks
        gained = data['price'] * int(request.form.get("shares"))

        # Deposit the price to user's cash
        db.execute(
            "UPDATE users SET cash = ? where id = ?",
            user_cash[0]['cash'] + gained, session['user_id']
        )

        # Redirect the user to the Homepage
        return redirect("/")

    else:
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
