import config

import requests
from pymongo import MongoClient

client = MongoClient(config.connection_string)
db = client["library"]
books = db["books"]

while (query := input("Google Book ID: ")) != "":
    book_info = requests.get(
        f"https://www.googleapis.com/books/v1/volumes/{query}").json()["volumeInfo"]
    books.insert_one({"title": book_info["title"],
                      "authors": book_info["authors"],
                      "isbn": book_info["industryIdentifiers"][-1]["identifier"],
                      "page_count": book_info["pageCount"]})

    print(f"Inserted book \"{book_info['title']}\"!")

for doc in books.find({}):
    print(doc)

client.close()
