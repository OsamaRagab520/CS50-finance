# C$50 Finance
### Description
Finance, a web app via which you can manage portfolios of stocks.
Not only will this tool allow you to check real stocks’ actual prices and portfolios’ values,
it will also let you buy (okay, “buy”) and sell (okay, “sell”) stocks by querying [**IEX**](https://iextrading.com/developer/) for stocks’ prices.

### Code style
All backend code follows [**PEP8 style guidelines**](https://www.python.org/dev/peps/pep-0008/)

## Getting Started
### Configuring
You’ll need to register for an API key in order to be able to query IEX’s data. To do so, follow these steps:

- Visit [**iexcloud.io/cloud-login#/register/**](https://iexcloud.io/cloud-login#/register/).
- Select the “Individual” account type, then enter your email address and a password, and click “Create account”.
- Once registered, scroll down to “Get started for free” and click “Select Start” to choose the free plan.
- Once you’ve confirmed your account via a confirmation email, visit [**https://iexcloud.io/console/tokens.**](https://iexcloud.io/console/tokens)
- Copy the key that appears under the Token column (it should begin with `pk_`).
- In a terminal window, execute:
`export API_KEY=value`
where `value` is that (pasted) value, without any space immediately before or after the `=`. You also may wish to paste that value in a text document somewhere, in case you need it again later.

### Pre-requisites and Local Development
Developers using this project should already have Python3, pip and sqlite installed on their local machines.\
From inside the 'cs50-finance' folder run `pip install -r requirements.txt`. All required packages are included in the requirements file.
To run the application locally run the following command:

    flask run

The application is run on `http://127.0.0.1:5000/` by default.

### Project Structure
    ├── cs50-finance/
        ├── static/
        |    ├── styles.css
        |    ├── faveicon.ico
        ├── env/
        ├── templates/
        |    ├── apology.html
        |    ├── buy.html
        |    ├── history.html
        |    ├── index.html
        |    ├── layout.html
        |    ├── login.html
        |    ├── quote.html
        |    ├── register.html
        |    ├── sell.html
        ├── helpers.py
        ├── app.py
        ├── requirements.txt
        ├── finance.db

This structure has three top-level folders:
- The *static* which contains static files such as styles, faveicon & images
- The *env* folder contains the Python virtual environment.
- The *templates* folder where views (html files) exist.

There are also a few new files:
- *app.py* where the flask application lives.
- *helpers.py* contains helper functions.
- *requirements.txt* lists the package dependencies to regenerate identical virtual environments.
- *finance.db* which is the sqlite database file

## ERD
symbol attribute could be factored out to convert the relation to 2NF.

![ERD](https://github.com/osamaragab520/cs50-finance/blob/master/static/erd.png)

## Acknowledgements & Final words
This is the part of cs50 course problem set. Of course there will be imperfections, flaws that might need some more work.
