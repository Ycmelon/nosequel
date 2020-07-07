# nosequel

![GitHub licence](https://img.shields.io/github/license/Ycmelon/nosequel?color=orange)
![Python version](https://img.shields.io/badge/Python-3.8-orange.svg)

MongoDB library app

## Screenshots

![Demo image](.github/demo.png)

## Features

### Books

-	Add book (title, authors, isbn, page_count) to library
-	Delete book from library 
-	Edit book information
-	Remove specific attributes from book

### Borrowers

-	Add borrower's (name, username, phone) to library 
-	Delete borrowers from library 
-	Edit borrower information 
- Allow borrowers to checkout/return books (if available)
-	Track number of books checked out by a given user
- Track which user has checked out a book

### Browsing

-	Search by title, authors, or ISBN
-	Sort by title, authors, ISBN or page count
-	Search by name, username 

## Quirks

- For update and insert, `field: ""` will not be inserted (no field in document)
- Missing fields or `field: null` will show up as "\<null\>"

## Installation

- Clone this respository
- Rename `config_template.py` to `config.py` and update values
- [requirements.txt](/requirements.txt)

## Usage

Run `cli.py`

### Sorting

In any search query, append `sortby:<field>` to sort (fields: `title`, `authors`, `isbn`, `page_count`)

## License

[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)
