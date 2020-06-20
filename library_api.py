import config
from templates import *

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient(config.connection_string)
db = client["library"]


def get_book(book_id: ObjectId) -> dict:
    """Gets a book from the collection

    Args:
        book_id(ObjectId)
    """

    cursor = db.books.find_one({"_id": book_id})
    if cursor == None:
        return cursor
    return {**book_template, **cursor}


def insert_book(book: dict):
    """Inserts a book to the collection

    Args:
        book(dict):
            title(str)
            authors(list)
            isbn(str)
            page_count(int)
    """

    to_insert = book
    db.books.insert_one(to_insert)


def delete_book(book_id: ObjectId):
    """Deletes a book from the collection

    Args:
        book_id(ObjectId)
    """

    db.books.delete_one({"_id": book_id})


def update_book(book_id: ObjectId, book: dict):
    """Updates a book from the collection

    Args:
        book_id(ObjectId)
        book(dict):
            title(str)
            authors(list)
            isbn(str)
            page_count(int)
    """

    # db.books.update_one({"_id": book_id}, {"$set": book})

    # To allow removing fields
    db.books.replace_one({"_id": book_id}, book)


def remove_attributes_book(book_id: ObjectId, attributes: list):
    """Removes attributes from a book in the collection

    Args:
        book_id(ObjectId)
        book(dict):
            title(str)
            authors(list)
            isbn(str)
            page_count(int)
    """

    # Set null:
    # remove_attributes = {attribute: None for attribute in attributes}
    # db.books.update_one({"_id": book_id}, {"$set": remove_attributes})

    remove_attributes = {attribute: "" for attribute in attributes}
    db.books.update_one({"_id": book_id}, {"$unset": remove_attributes})


def get_borrower(borrower_id: ObjectId) -> dict:
    """Gets a borrower from the collection

    Args:
        book_id(ObjectId)
    """

    cursor = db.borrowers.find_one({"_id": borrower_id})
    if cursor == None:
        return None
    return {**borrower_template, **cursor}


def insert_borrower(borrower: dict):
    """Inserts a borrower to the collection

    Args:
        borrower(dict):
            name(str)
            username(str)
            phone(str)
    """

    db.borrowers.insert_one(borrower)


def delete_borrower(borrower_id: ObjectId):
    """Deletes a borrower from the collection

    Args:
        borrower_id(ObjectId)
    """

    db.borrowers.delete_one({"_id": borrower_id})


def update_borrower(borrower_id: ObjectId, borrower: dict):
    """Updates a borrower from the collection

    Args:
        borrower_id(ObjectId)
        borrower(dict):
            name(str)
            username(str)
            phone(str)
    """

    # db.borrowers.update_one({"_id": borrower_id}, {"$set": borrower})

    # To allow removing fields
    db.borrowers.replace_one({"_id": borrower_id}, borrower)


def checkout_book(borrower_id: ObjectId, book_id: ObjectId) -> int:
    """Checks out a book

    Args:
        borrower_id(ObjectId)
        book_id(ObjectId)

    Returns:
        -1: Book not in library
        0: Book already checked out
        1: Book successfully checked out
    """

    book = db.books.find_one({"_id": book_id})

    if book == None:
        return -1
    elif "borrower" in book:
        if book["borrower"] != None:
            return 0

    db.books.update_one({"_id": book_id}, {"$set": {"borrower": borrower_id}})
    return 1


def return_book(book_id: ObjectId) -> int:
    """Returns a book

    Args:
        book_id(ObjectId)

    Returns:
        -1: Book not in library
        0: Book already returned
        1: Book successfully returned
    """

    book = db.books.find_one({"_id": book_id})

    if book == None:
        return -1
    elif "borrower" in book:
        if book["borrower"] == None:
            return 0

    db.books.update_one({"_id": book_id}, {"$set": {"borrower": None}})
    return 1


def validate_username(username: str):
    """Validates username

    Args:
        username(str)
    """

    if db.borrowers.find_one({"username": username}) == None:
        return False
    return db.borrowers.find_one({"username": username})["_id"]


# if __name__ == "__main__":
#     print(get_book(ObjectId("5eeccbcbcf92ea05a4a61b74")))
#     client.close()
