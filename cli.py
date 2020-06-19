import config
from library_api import *

from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId

import colorama
from termcolor import cprint
from PyInquirer import style_from_dict, Token, prompt, Separator


client = MongoClient(config.connection_string)
db = client["library"]

colorama.init()
cprint("nosequel 1.0", color="blue")

main_menu = [
    {
        "type": "list",
        "name": "action",
        "message": "What do you want to do?",
        "choices": [
            "Log in/out",
            {
                "name": "Checkout a book",
                "disabled": "Not logged in"
            },
            {
                "name": "Return a book",
                "disabled": "Not logged in"
            },
            Separator(),
            "Add a book",
            "Modify a book",
            "Delete books",
            "Remove attributes from a book",
            Separator(),
            "Add a borrower",
            "Modify a borrower",
            "Delete borrowers",
            Separator(),
            "Exit"
        ]
    },
]
search_menu = [{
    "type": "input",
    "name": "query",
    "message": "Search query (add \"sortby:<field>\" to sort)",
}]

continue_ = True

while continue_:
    # Main menu
    action = prompt(main_menu, style=config.style)
    collection = "books" if "book" in action["action"] else "borrowers"

    # TODO: log in/out, borrow, return

    # Add
    if "Add" in action["action"]:
        if collection == "books":
            info_menu = [{
                "type": "input",
                "name": "title",
                "message": "Book title", },
                {
                "type": "input",
                "name": "isbn",
                "message": "ISBN", },
                {
                "type": "input",
                "name": "page_count",
                "message": "Page count",
            }]
            new_info = prompt(info_menu, style=config.style)
            try:
                new_info["page_count"] = int(new_info["page_count"])
            except ValueError:
                raise ValueError("Page count must be type int!")

            new_authors = []
            new_author = 0
            author_count = 0
            while new_author != "":
                author_menu = [{
                    "type": "input",
                    "name": "author",
                    "message": f"New author {str(author_count+1)} (enter to finish)",
                }]

                new_author = prompt(author_menu, style=config.style)["author"]
                if new_author != "":
                    new_authors.append(new_author)
                    author_count += 1

            insert_book({"authors": new_authors, **new_info})
            print(f"Inserted {new_info['title']}")
        elif collection == "borrowers":
            info_menu = [{
                "type": "input",
                "name": "name",
                "message": "Name", },
                {
                "type": "input",
                "name": "username",
                "message": "Username", },
                {
                "type": "input",
                "name": "phone",
                "message": "Phone",
            }]

            new_info = prompt(info_menu, style=config.style)
            insert_borrower(new_info)
            print(f"Inserted {new_info['name']}")
        continue

    # Modify, delete, remove attributes
    search = prompt(search_menu, style=config.style)  # TODO: sort

    cursor = db[collection].find({"$text": {"$search": search["query"]}})
    if " sortby:" in search["query"]:
        sort_by = search["query"].split(" sortby:")[1]
        search["query"] = search["query"].split(" sortby:")[0]
        cursor = cursor.sort(sort_by, ASCENDING)
        print(f"Sort \"{sort_by}\" applied!")

    if (search_results := list(cursor)) == []:
        print("No results!")
        continue

    if collection == "books":
        search_results = [
            {"name": f"{search_result['title']} ({', '.join(search_result['authors'])})",
             "value": search_result["_id"]}
            for search_result in search_results]
    elif collection == "borrowers":
        search_results = [
            {"name": f"{search_result['name']} ({search_result['username']})",
             "value": search_result["_id"]}
            for search_result in search_results]

    if "Modify" in action["action"] or "Remove attributes" in action["action"]:
        results_menu_type = "list"
    elif "Delete" in action["action"]:
        results_menu_type = "checkbox"

    results_menu = [
        {
            "type": results_menu_type,
            "name": "selected",
            "message": "Search results",
            "choices": search_results
        }]
    selected = prompt(results_menu, style=config.style)

    if "Modify" in action["action"]:
        if collection == "books":
            book = get_book(selected["selected"])
            info_menu = [{
                "type": "input",
                "name": "title",
                "message": "Updated book title",
                "default": book["title"]},
                {
                "type": "input",
                "name": "isbn",
                "message": "Updated ISBN",
                "default": book["isbn"]},
                {
                "type": "input",
                "name": "page_count",
                "message": "Updated page count",
                "default": str(book["page_count"])
            }]
            new_info = prompt(info_menu, style=config.style)
            try:
                new_info["page_count"] = int(new_info["page_count"])
            except ValueError:
                raise ValueError("Page count must be type int!")

            new_authors = []
            new_author = 0
            author_count = 0
            while new_author != "":
                author_menu = [{
                    "type": "input",
                    "name": "author",
                    "message": f"New author {str(author_count+1)} (enter to finish)",
                }]
                if author_count < len(book["authors"]):
                    author_menu[0]["default"] = book["authors"][author_count]

                new_author = prompt(author_menu, style=config.style)["author"]
                if new_author != "":
                    new_authors.append(new_author)
                    author_count += 1

            updated_book = {"authors": new_authors, **new_info}
            update_book(book["_id"], updated_book)
            print(f"Updated {str(book['_id'])}")
        elif collection == "borrowers":
            borrower = get_borrower(selected["selected"])
            info_menu = [{
                "type": "input",
                "name": "name",
                "message": "Updated name",
                "default": borrower["name"]},
                {
                "type": "input",
                "name": "username",
                "message": "Updated username",
                "default": borrower["username"]},
                {
                "type": "input",
                "name": "phone",
                "message": "Updated phone",
                "default": borrower["phone"]
            }]
            new_info = prompt(info_menu, style=config.style)

            update_borrower(borrower["_id"], new_info)
            print(f"Updated {str(borrower['_id'])}")
        continue
    elif "Delete" in action["action"]:
        for element in selected["selected"]:
            if collection == "books":
                delete_book(element)
            elif collection == "borrowers":
                delete_borrower(element)
            print(f"Deleted {str(element)}")
        continue
    elif "Remove attributes" in action["action"]:
        attributes_menu = [
            {
                "type": "checkbox",
                "name": "selected",
                "message": "Attributes to remove",
                "choices": [{"name": "Title", "value": "title"},
                            {"name": "Authors", "value": "authors"},
                            {"name": "ISBN", "value": "isbn"},
                            {"name": "Page count", "value": "page_count"}]
            }]
        new_info = prompt(attributes_menu, style=config.style)["selected"]
        remove_attributes_book(selected["selected"], new_info)
        print(f"Updated {str(selected['selected'])}")
        continue

    # print(selected)

# while validate_username(username := input("Username: ")) == False:
#     print("oi")
