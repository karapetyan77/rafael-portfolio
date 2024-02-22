import sqlite3


def add_book(book_details):
    with sqlite3.connect('the_book_catalog.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO books (
                       title,
                       author,
                       year_published,
                       genre,
                       rating
                       )
                       VALUES (?, ?, ?, ?, ?)""",
                       book_details)


def update_book(book_id, updated_details):
    with sqlite3.connect('the_book_catalog.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""UPDATE books SET
                       title=?,
                       author=?,
                       year_published=?,
                       genre=?,
                       rating=?
                       WHERE id=?""",
                       (*updated_details, book_id))


def delete_book(book_id):
    with sqlite3.connect('the_book_catalog.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id=?", (book_id,))


def get_the_book(book_id):
    with sqlite3.connect('the_book_catalog.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM books WHERE id=?", (book_id,))
        row = cursor.fetchone()

    if row:
        print(row)
    else:
        print(f"Book with ID {book_id} not found in the catalog.")


def get_all_books():
    with sqlite3.connect('the_book_catalog.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        rows = cursor.fetchall()

    for row in rows:
        print(row)


if __name__ == "__main__":

    def input_details():
        title = input("Title: ")
        author = input("Author: ")
        year_published = int(input("Year published: "))
        genre = input("Genre: ")
        while True:
            rating = int(input("Rating (1-5): "))
            if 1 <= rating <= 5:
                break
            print("Invalid rating! Please enter a value between 1 and 5.")
        return title, author, year_published, genre, rating

    def print_commands():
        print()
        print("1. Add book")
        print("2. Update book's details")
        print("3. Delete book")
        print("4. See all books")
        print("5. Exit")

    choice = 0
    while choice != 5:
        print_commands()
        choice = int(input("Choose here: "))
        match choice:
            case 1:
                print("Enter book details:")
                book_details = input_details()
                add_book(book_details)
                print("Book added to the catalog.")
            case 2:
                id = int(input("Choose the id of a book: "))
                get_the_book(id)
                print("Enter the new details for a book:")
                updated_details = input_details()
                update_book(id, updated_details)
                print("The book's details are updated.")
            case 3:
                id = int(input("Choose the id of a book: "))
                get_the_book(id)
                delete_book(id)
                print("The book has been deleted.")
            case 4:
                get_all_books()
            case _:
                break

    print("List of Books:")
    get_all_books()
