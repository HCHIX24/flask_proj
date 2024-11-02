from flask import Flask
from flask_restful import Api
from config import Config
from models import db
from resources import BookResource, UserResource, BorrowResource

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Initialize the API
api = Api(app)

# Register routes
api.add_resource(BookResource, '/books', '/books/<int:book_id>')
api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(BorrowResource, '/borrows', '/borrows/<int:borrow_id>')

# Create the database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
