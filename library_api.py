import config
from templates import *

from pymongo import MongoClient
from bson.objectid import ObjectId

from functools import lru_cache

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

    db.books.insert_one(book)


def delete_books(book_ids: list):
    """Deletes many books from the collection

    Args:
        book_ids(list):
            ObjectId
    """

    db.books.delete_many({"_id": {"$in": book_ids}})
    db.loans.update_many({"book_id": {"$in": book_ids}},
                         {"$set": {"returned": True}})


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


def delete_borrowers(borrower_ids: list):
    """Deletes many borrowers from the collection

    Args:
        borrower_ids(list):
            ObjectId
    """

    db.borrowers.delete_many({"_id": {"$in": borrower_ids}})
    db.loans.update_many(
        {"borrower_id": {"$in": borrower_ids}}, {"$set": {"returned": True}})


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


def checkout_book(borrower_id: ObjectId, book_id: ObjectId):
    """Checks out a book

    Args:
        borrower_id(ObjectId)
        book_id(ObjectId)
    """

    db.loans.insert_one({"borrower_id": borrower_id,
                         "book_id": book_id, "returned": False})


def return_book(book_id: ObjectId):
    """Returns a book

    Args:
        book_id(ObjectId)
    """

    book = db.loans.update_one({"book_id": book_id, "returned": False}, {
                               "$set": {"returned": True}})


def validate_username(username: str):
    """Validates username

    Args:
        username(str)

    Returns:
        bool
        str
    """

    if db.borrowers.find_one({"username": username}) == None:
        return False
    return db.borrowers.find_one({"username": username})["_id"]


@lru_cache
def get_username(borrower_id: ObjectId) -> str:
    """Gets username

    Args:
        borrower_id(str)

    Returns:
        str
    """

    cursor = db.borrowers.find_one({"_id": borrower_id})
    return cursor["username"] if "username" in cursor else str(borrower_id)


def is_checked_out(book_id: ObjectId):
    """Checks whether a book is checked out

    Args:
        book_id(ObjectId)

    Returns:
        bool: Not checked out
        ObjectId: User ID of borrower
    """

    loan = db.loans.find_one({"book_id": book_id, "returned": False})
    if loan == None:
        return False
    return loan["borrower_id"]


def get_borrowed_books(borrower_id: ObjectId) -> list:
    """Gets currently borrowed books

    Args:
        borrower_id(ObjectId)

    Returns:
        list
    """

    return list(db.loans.find({"borrower_id": borrower_id, "returned": False}))


def search_function(collection: str, query: str):
    """Performs a search

    Args:
        collection(str):
            borrowers
            books
        query(str)

    Returns:
        cursor
    """

    return db[collection].find({"$text": {"$search": query}})
