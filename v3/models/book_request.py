class BookRequest:
    def __init__(self, id=None, book_id=None, user_id=None, status="Pending",
                 request_date=None, approval_date=None, notes=None):
        self.id = id
        self.book_id = book_id
        self.user_id = user_id
        self.status = status
        self.request_date = request_date
        self.approval_date = approval_date
        self.notes = notes
