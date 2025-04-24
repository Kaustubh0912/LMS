class User:
    def __init__(self, id=None, username=None, password=None, is_admin=False, book_limit=3, books_issued=0):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.book_limit = book_limit
        self.books_issued = books_issued
