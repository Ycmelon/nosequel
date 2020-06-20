# nosequel

![GitHub licence](https://img.shields.io/github/license/Ycmelon/nosequel?color=orange)
![Python version](https://img.shields.io/badge/Python-3.8-orange.svg)

MongoDB library app

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
-	Search by name, username 
- Allow borrowers to checkout/return books (if available)
-	Track number of books checked out by a given user
- Track which user has checked out a book

### Browsing

-	Search by title, authors, or ISBN
-	Sort by title, authors, ISBN or page count

## Quirks

- For update and insert, `field: ""` will not be inserted (no field in document)
- Missing fields or `field: null` will show up as "\<null\>"

## Installation

- Clone this respository
- Rename `config_template.py` to `config.py` and update values
- [requirements.txt](/requirements.txt)

## Usage

Run `cli.py`

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)
