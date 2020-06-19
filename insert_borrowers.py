import config

import random
import requests
from pymongo import MongoClient

client = MongoClient(config.connection_string)
db = client["library"]
borrowers = db["borrowers"]

for _ in range(int(input("Number of borrowers to add: "))):
    borrower_info = requests.get(
        f"https://api.namefake.com/").json()

    # Remove title
    if ". " in borrower_info["name"]:
        name = borrower_info["name"].split(". ")[1]
    else:
        name = borrower_info["name"]

    username = name.replace(" ", "").lower() + str(random.randint(10, 99))

    borrowers.insert_one({"name": name,
                          "username": username,
                          "phone": "+659" + str(random.randint(1000000, 9999999))})
    print(f"Inserted borrower \"{name}\"!")

for doc in borrowers.find({}):
    print(doc)

client.close()
