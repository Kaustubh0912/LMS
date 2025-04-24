class Book:
    def __init__(self, id=None, title=None, book_id=None, author=None, status="Available",
                 issuer_id=None, course_code=None, issue_date=None, return_date=None):
        self.id = id
        self.title = title
        self.book_id = book_id
        self.author = author
        self.status = status
        self.issuer_id = issuer_id
        self.course_code = course_code
        self.issue_date = issue_date
        self.return_date = return_date
