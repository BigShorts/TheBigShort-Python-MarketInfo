from flask import Flask
from yahoolib import *

# file for the Flask server code to run the "yahoolib.py" functions

app = Flask(__name__)


# app routing code below
@app.route('/')
def test():
    return "Hello World!"


@app.route('/index/<index_name>/<return_type>')
def get_index(index_name, return_type):
    return load_index(index_name, return_type)


@app.route('/indexes/<exchange>')
def get_indexes(exchange):
    return load_indexes(exchange)


@app.route('/exchange/<exchange>/<return_type>')
def get_exchange(exchange, return_type):
    return load_exchange(exchange, return_type)


# called when profile needs force update
@app.route('/profile/<ticker>')
def profile(ticker):
    return f"Profile for {ticker}"


@app.route('/trigger')
def trigger():
    return get_nasdaq()

