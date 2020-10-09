import config
from templates import *
from library_api import *

from pymongo import ASCENDING

import colorama
from termcolor import cprint
from PyInquirer import style_from_dict, Token, prompt, Separator

colorama.init()
cprint("Nosequel - Loh Yu Chen (21) 3L", color="blue")

logged_in = False


def get_main_menu(logged_in):
    require_login = [
        {
            "name": "Checkout books",
        },
        {
            "name": "Return books",
        },
    ]
    if not logged_in:
        for action in require_login:
            action["disabled"] = "Not logged in"

    return [
        {
            "type": "list",
            "name": "action",
            "message": "What do you want to do?",
            "choices": [
                "Log in/out",
                *require_login,
                Separator(),
                "Add a book",
                "Modify a book",
                "Delete books",
                "Remove attributes from a book",
                Separator(),
                "Add a borrower",
                "Modify a borrower",
                "Delete borrowers",
                "Track borrowers' number of books borrowed",
                Separator(),
                "Exit",
            ],
        },
    ]


search_menu = [
    {
        "type": "input",
        "name": "query",
        "message": 'Search query (add "sortby:<field>" to sort)',
    }
]
login_menu = [
    {
        "type": "input",
        "name": "username",
        "message": "Username",
    }
]

continue_ = True

while continue_:
    # Main menu
    action = prompt(get_main_menu(logged_in), style=config.style)
    collection = "books" if "book" in action["action"] else "borrowers"

    if "Exit" in action["action"]:
        continue_ = False
        continue

    # Log in
    if "Log in" in action["action"]:
        if logged_in == False:
            username = prompt(login_menu, style=config.style)["username"]
            if not (_id := validate_username(username)):
                print("Invalid username!")
            else:
                logged_in = _id
                print(f"Logged in as {str(_id)}!")
        else:
            logged_in = False
        continue

    # Track
    if "Track" in action["action"]:
        username = prompt(login_menu, style=config.style)["username"]
        if not (user_id := validate_username(username)):
            print("Invalid username!")
        else:
            print(f"Number of books borrowed: {len(get_borrowed_books(user_id))}")
        continue

    # Return
    if "Return" in action["action"]:
        if (search_results := get_borrowed_books(logged_in)) != []:
            search_results = [get_book(loan["book_id"]) for loan in search_results]
            old_search_results = []
            for search_result in search_results:
                # Missing values --> None
                old_search_results.append({**book_template, **search_result})
            search_results = [
                {
                    "name": f"{search_result['title'] if search_result['title'] != None else null_field} "
                    + f"({', '.join(search_result['authors']) if type(search_result['authors']) == list else null_field})",
                    "value": search_result["_id"],
                }
                for search_result in old_search_results
            ]
            results_menu = [
                {
                    "type": "checkbox",
                    "name": "selected",
                    "message": "Select books to return",
                    "choices": [
                        {"name": "Go back", "value": "Go back"},
                        Separator(),
                        *search_results,
                    ],
                }
            ]

            to_return = prompt(results_menu, style=config.style)["selected"]

            if "Go back" in to_return:
                continue

            for book in to_return:
                return_book(book)
                print(f"Returned {str(book)}")
        else:
            print("No books on loan!")
        continue

    # Add
    if "Add" in action["action"]:
        if collection == "books":  # Add book
            info_menu = [
                {
                    "type": "input",
                    "name": "title",
                    "message": "Book title",
                },
                {
                    "type": "input",
                    "name": "isbn",
                    "message": "ISBN",
                },
                {
                    "type": "input",
                    "name": "page_count",
                    "message": "Page count",
                },
            ]
            new_info = prompt(info_menu, style=config.style)
            try:
                if new_info["page_count"] == "":
                    del new_info["page_count"]  # Create missing field
                else:
                    new_info["page_count"] = int(new_info["page_count"])
            except ValueError:
                raise ValueError("Page count must be type int!")

            new_info = {
                key: value for key, value in new_info.items() if value != ""
            }  # Create missing fields

            # Get authors
            new_authors = []
            new_author = 0
            author_count = 0
            while new_author != "":
                author_menu = [
                    {
                        "type": "input",
                        "name": "author",
                        "message": f"New author {str(author_count+1)} (enter to finish)",
                    }
                ]

                new_author = prompt(author_menu, style=config.style)["author"]
                if new_author != "":
                    new_authors.append(new_author)
                    author_count += 1

            if new_authors != []:
                new_info["authors"] = new_authors

            insert_book(new_info)
            print(f"Inserted {new_info['title'] if 'title' in new_info else 'new book'}")
        elif collection == "borrowers":  # Add borrower
            info_menu = [
                {
                    "type": "input",
                    "name": "name",
                    "message": "Name",
                },
                {
                    "type": "input",
                    "name": "username",
                    "message": "Username",
                },
                {
                    "type": "input",
                    "name": "phone",
                    "message": "Phone",
                },
            ]

            new_info = prompt(info_menu, style=config.style)

            new_info = {
                key: value for key, value in new_info.items() if value != ""
            }  # Create missing fields

            insert_borrower(new_info)
            print(f"Inserted {new_info['name'] if 'name' in new_info else 'new borrower'}")
        continue

    # Modify, delete, remove attributes (require search)
    search = prompt(search_menu, style=config.style)

    cursor = search_function(collection, search["query"])
    if "sortby:" in search["query"]:  # Handle sorts
        sort_by = search["query"].split("sortby:")[1].strip()
        search["query"] = search["query"].split(" sortby:")[0]
        cursor = cursor.sort(sort_by, ASCENDING)
        print(f'Sort "{sort_by}" applied!')

    if (search_results := list(cursor)) == []:
        print("No results!")
        continue

    if collection == "books":
        old_search_results = []
        for search_result in search_results:
            # Missing values --> None
            old_search_results.append({**book_template, **search_result})
        search_results = [
            {
                "name": f"{search_result['title'] if search_result['title'] != None else null_field} "
                + f"({', '.join(search_result['authors']) if type(search_result['authors']) == list else null_field})",
                "value": search_result["_id"],
            }
            for search_result in old_search_results
        ]
        if "Checkout" in action["action"]:
            for index, search_result in enumerate(old_search_results):
                if (borrower_id := is_checked_out(search_result["_id"])) :
                    search_results[index]["disabled"] = f"On loan by {get_username(borrower_id)}"

    elif collection == "borrowers":
        for index, search_result in enumerate(search_results):
            search_results[index] = {**borrower_template, **search_result}
        search_results = [
            {
                "name": f"{search_result['name'] if search_result['name'] != None else null_field} "
                + f"({search_result['username'] if search_result['username'] != None else null_field})",
                "value": search_result["_id"],
            }
            for search_result in search_results
        ]

    if "Modify" in action["action"] or "Remove attributes" in action["action"]:
        results_menu_type = "list"  # Only 1 at a time
    elif "Delete" in action["action"] or "Checkout" in action["action"]:
        results_menu_type = "checkbox"  # Multiple selections

    results_menu = [
        {
            "type": results_menu_type,
            "name": "selected",
            "message": "Search results",
            "choices": [{"name": "Go back", "value": "Go back"}, Separator(), *search_results],
        }
    ]
    selected = prompt(results_menu, style=config.style)

    if selected["selected"] == "Go back":  # "list" type
        continue
    elif type(selected["selected"]) == list:  # "checkbox" type
        if "Go back" in selected["selected"]:
            continue

    # Modify
    if "Modify" in action["action"]:
        if collection == "books":
            book = get_book(selected["selected"])
            info_menu = [
                {
                    "type": "input",
                    "name": "title",
                    "message": "Updated book title",
                    "default": book["title"] if book["title"] != None else "",
                },
                {
                    "type": "input",
                    "name": "isbn",
                    "message": "Updated ISBN",
                    "default": book["isbn"] if book["isbn"] != None else "",
                },
                {
                    "type": "input",
                    "name": "page_count",
                    "message": "Updated page count",
                    "default": str(book["page_count"]) if book["page_count"] != None else "",
                },
            ]
            new_info = prompt(info_menu, style=config.style)
            try:
                if new_info["page_count"] == "":
                    del new_info["page_count"]
                else:
                    new_info["page_count"] = int(new_info["page_count"])
            except ValueError:
                raise ValueError("Page count must be type int!")

            new_info = {key: value for key, value in new_info.items() if value != ""}

            new_authors = []
            new_author = 0
            author_count = 0
            while new_author != "":
                author_menu = [
                    {
                        "type": "input",
                        "name": "author",
                        "message": f"New author {str(author_count+1)} (enter to finish)",
                    }
                ]
                if book["authors"] != None:
                    if author_count < len(book["authors"]):
                        author_menu[0]["default"] = book["authors"][author_count]

                new_author = prompt(author_menu, style=config.style)["author"]
                if new_author != "":
                    new_authors.append(new_author)
                    author_count += 1

            if new_authors != []:
                new_info["authors"] = new_authors

            update_book(book["_id"], new_info)
            print(f"Updated {str(book['_id'])}")
        elif collection == "borrowers":
            borrower = get_borrower(selected["selected"])
            info_menu = [
                {
                    "type": "input",
                    "name": "name",
                    "message": "Updated name",
                    "default": borrower["name"] if borrower["name"] != None else "",
                },
                {
                    "type": "input",
                    "name": "username",
                    "message": "Updated username",
                    "default": borrower["username"] if borrower["username"] != None else "",
                },
                {
                    "type": "input",
                    "name": "phone",
                    "message": "Updated phone",
                    "default": borrower["phone"] if borrower["phone"] != None else "",
                },
            ]
            new_info = prompt(info_menu, style=config.style)

            new_info = {key: value for key, value in new_info.items() if value != ""}

            update_borrower(borrower["_id"], new_info)
            print(f"Updated {str(borrower['_id'])}")
        continue

    # Delete
    elif "Delete" in action["action"]:
        if collection == "books":
            delete_books(selected["selected"])
        elif collection == "borrowers":
            if logged_in in selected["selected"]:
                logged_in = False
            delete_borrowers(selected["selected"])
        print(f"Deleted {len(selected['selected'])} items")
        continue

    # Remove attributes
    elif "Remove attributes" in action["action"]:
        attributes_menu = [
            {
                "type": "checkbox",
                "name": "selected",
                "message": "Attributes to remove",
                "choices": [
                    {"name": "Title", "value": "title"},
                    {"name": "Authors", "value": "authors"},
                    {"name": "ISBN", "value": "isbn"},
                    {"name": "Page count", "value": "page_count"},
                ],
            }
        ]
        new_info = prompt(attributes_menu, style=config.style)["selected"]
        remove_attributes_book(selected["selected"], new_info)
        print(f"Updated {str(selected['selected'])}")
        continue

    # Checkout
    elif "Checkout" in action["action"]:
        for element in selected["selected"]:
            checkout_book(logged_in, element)
            print(f"Checked out {str(element)}")
        continue
