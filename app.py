########  imports  ##########
from flask import Flask, jsonify, request, render_template
from datetime import date
from pymongo import MongoClient
import json
import dns
import certifi
from bson.objectid import ObjectId
import os
import requests
from dotenv import load_dotenv

load_dotenv()
mongo_URL = os.getenv('mongo_URL')
api_key = os.getenv('IEX_KEY')

client = MongoClient(
    mongo_URL, tlsCAFile=certifi.where())
db = client['testStock']
mysymbols = db['symbols']
myportfolio = db['portfolio']
# mydict = {"myPortfolio": {"name": "Peter", "address": "Lowstreet 27"}}
# myportfolio.insert_one(mydict)


stocksdata = {}

app = Flask(__name__)
#############################


@app.route('/')
def home_page():
    return render_template('portfolio.html')


# get latest symbols on load if needed(once a day)
target = None


@app.route('/symbols', methods=['GET', 'POST'])
def get_symbols():
    # GET request
    if request.method == 'GET':
        default = mysymbols.find_one(
            {"_id": ObjectId("61cd43711d883807429ffe25")})
        # print(default['dateAdded'])
        # if item is outdated then update
        if default['dateAdded'] == str(date.today()):
            print('samedate, no api change')
            default['_id'] = str(default['_id'])
            return jsonify(default)
        else:
            print('update new symbol data')
            get_url = "https://cloud.iexapis.com/stable/ref-data/symbols?token=" + api_key
            allSymbols = requests.get(get_url).json()
            symbolsOnly = []
            for i in allSymbols:
                z = {"name": i['name'],
                     "symbol": i['symbol']}
                symbolsOnly.append(z)
            # print(symbolsOnly)
            target = {"dateAdded": str(date.today()),
                      "symbolData": symbolsOnly}
            mysymbols.replace_one(
                {"_id": ObjectId("61cd43711d883807429ffe25")}, target)
            return jsonify(target)

# getselected stock


@app.route('/getselected/<stock>', methods=['GET'])
def get_selected(stock):
    if request.method == 'GET':
        url = "https://cloud.iexapis.com/stable/stock/" + \
            stock + "/quote?token=" + api_key
        data = requests.get(url).json()
        return jsonify(data)

# get batch


@app.route('/getbatch/<batch>', methods=['GET'])
def getbatch(batch):
    if request.method == 'GET':
        url = "https://cloud.iexapis.com/stable/stock/market/batch?types=quote&symbols=" + \
            batch + \
            "&token=" + \
            api_key
        print("url is : ")
        print(url)
        data = requests.get(url).json()
        return jsonify(data)


# get selected stock historical


@app.route('/getselectedhistorical/<stock>', methods=['GET'])
def get_selected_historical(stock):
    if request.method == 'GET':
        url2 = "https://cloud.iexapis.com/stable/stock/" + \
            stock + \
            "/chart/3m?chartCloseOnly=true&token=" + \
            api_key
        historical_data = requests.get(url2).json()
        # print(historical_data)
        return jsonify(historical_data)

# post portfolio


@app.route('/portfolio', methods=['POST', 'GET'])
def post_portfolio():
    # post
    if request.method == 'POST':
        data = request.json
        # del data['_id']
        # data2 = {"myStocks": data}
        myportfolio.replace_one(
            {"_id": ObjectId("61ce9fe0a9804bf0f217b8cb")},   {"myPortfolio": data})
        # print(data2)
        return "Success", 200
    # get
    elif request.method == 'GET':
        default = myportfolio.find_one(
            {"_id": ObjectId("61ce9fe0a9804bf0f217b8cb")})
        default['_id'] = str(default['_id'])
        print()
        return jsonify(default['myPortfolio'])


#########  run app  #########
# app.run(debug=True)
# if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0')
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
