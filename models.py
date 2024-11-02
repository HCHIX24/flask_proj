from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Books(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    available_copies = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Book {self.title}>"
    

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.name}>"
    
class Borrows(db.Model):
    __tablename__ = 'borrows'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    return_date = db.Column(db.DateTime, nullable=True)

    book = db.relationship('Books', backref='borrowed_by')
    user = db.relationship('Users', backref='borrowed_books')

    def __repr__(self):
        return f"<Borrow book_id={self.book_id} user_id={self.user_id}>"
    