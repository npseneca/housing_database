import pymongo

from flask import Flask
from flask import request, jsonify
from flask import send_from_directory
from flask_cors import CORS

import os
import json

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

FIELDS = """detail_url,price,square_feet,beds,bathrooms,zipcode,year_built,days_on_market,elem_rating,middle_rating,hs_rating
"""

#replace with the right url, database, and collection
myclient = pymongo.MongoClient("mongodb+srv://smamos:KU5GeuKV44XbPBT@cs452.ptnf0.mongodb.net/?retryWrites=true&w=majority&appName=cs452")
mydb = myclient['final_project']
mycul = mydb['houses']

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
        q = sanitizeForMongoQuery(q)
        print("Sanitized: ", q)

        query = {}
        query.update(q)
        
        results = mycul.find(query, {"_id": 0, "detail_url": 1}).limit(5)

        listings = list(results)
        print(listings)
        
        return jsonify(listings), 200
    except Exception as e:
        print(e)
        return f"Error searching: {e}"
    
# OpenAI helper functions
def getChatGptResponse(content):
    instructions = "Give me a MongoDB select statement in JSON format that answers the query. \
    If there is an error do not explain it! \
    Do not include comments. \
    This collection does not have any indexes. \
    Do not try to use geographic operations such as $near\
    Only use fields in this list (all of which are type number, except detail_url):\n" + FIELDS

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


def sanitizeForMongoQuery(value):
    """ Sample response
    ```json
    {"beds":2.0,"bathrooms":2.0}
    ```
    """
    try:
        if len(value) == 3:
            q = value.split()[1]
        else:
            q = ''.join(value.split()[1:-1])
        value = json.loads(q)

    except Exception as e:
        print("Error sanitizing: ", e)

    return value

if __name__ == "__main__":
    app.run()
