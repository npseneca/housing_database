import pymongo

from flask import Flask
from flask import request, jsonify
from flask import send_from_directory
from flask_cors import CORS

import os

from openai import OpenAI

with open('secrets.env') as f:
    secrets = f.readlines()


for secret in secrets:
    name, password = secret.split('=')
    name, password = name.strip(), password.strip()
    os.environ[name] = password


# intialize OpenAI client

openAiClient = OpenAI(
    api_key = os.environ.get("openaiKey"),
    organization = os.environ.get("orgId")
)


# Database structure example

# { "k_6_rating": "elem_rating", "7_9_rating": "middle_rating", "10_12_rating": "hs_rating" }
TABLE = """detail_url,price,square_feet,beds,bathrooms,zipcode,year_built,days_on_market,elem_rating,middle_rating,hs_rating
https://www.zillow.com/homedetails/843-S-Walker-Way-St-George-UT-84770/440360262_zpid/,558990.0,2340.0,3.0,3.0,84770,2024.0,49.0,-1,-1,4
"""

#replace with the right url, database, and collection
myclient = pymongo.MongoClient("mongodb+srv://npseneca:xnPc5jSVrOoaur0t@cs452.gtgjg.mongodb.net/?retryWrites=true&w=majority&appName=cs452")
mydb = myclient['testDB']
mycul = mydb['test']

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/list", methods = ["Post", "GET"])
def Push():
    content = request.get_json()
    mycul.insert_one(content)
    return "Push initiated"

#TODO: implement search function which uses ChatGPT
@app.route("/search", methods = ["Post", "GET"])
def Search():
    try: 
        with open('log.txt', 'a') as f:
            print(request, file=f)
        q = request.args.get('q')

        q = getChatGptResponse(q)
        

        query = {"zipcode": 20131}
        
        results = mycul.find(query, {"_id": 0, "detail_url": 1}).limit(5)
        
        listings = list(results)
        
        return jsonify(listings), 200
    except Exception as e:
        return f"Error: {e}"
    
# OpenAI helper functions
def getChatGptResponse(content):
    instructions = "Give me a MongoDB select statement that answers the question. Only respond with MongoDB syntax. If there is an error do not expalin it! Here's an example of the collection:\n" + TABLE
    content = instructions + content
    stream = openAiClient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
        stream=True,
    )

    responseList = []
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            responseList.append(chunk.choices[0].delta.content)

    result = "".join(responseList)
    return result

if __name__ == "__main__":
    app.run()
