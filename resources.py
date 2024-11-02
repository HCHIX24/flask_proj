from importlib import resources
from flask_restful import Resource, reqparse
from models import db, Books, Users, Borrows
from flask import jsonify
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Request parsers for book data
book_parser = reqparse.RequestParser()
book_parser.add_argument('title', required=True, help='Title cannot be blank')
book_parser.add_argument('author', required=True, help='Author cannot be blank')
book_parser.add_argument('available_copies', type=int, required=False)
# Request parsers for user data
user_parser = reqparse.RequestParser()
user_parser.add_argument('name', required=True, help='Name cannot be blank')
user_parser.add_argument('email', required=True, help='Email cannot be blank')
# Request parsers for borrow data
borrow_parser = reqparse.RequestParser()
borrow_parser.add_argument('book_id', type=int, required=True)
borrow_parser.add_argument('user_id', type=int, required=True)

# Books Resource
class BookResource(Resource):
    # BookRead
    def get(self, book_id=None):
        if book_id:
            book = Books.query.get(book_id)
            return jsonify(book) if book else {'message': 'Book not found'}, 404
        books = Books.query.all()
        return jsonify([{'id': book.id, 'title': book.title, 'author': book.author, 'copies': book.available_copies} for book in books])
    
    # BookCreate
    def post(self):
        args = book_parser.parse_args()
        book = Books(title=args['title'], author=args['author'], available_copies=args.get('available_copies', 1))
        db.session.add(book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully', 'id': book.id}), 201
    
    # BookUpdate
    def put(self, book_id):
        book = Books.query.get(book_id)
        if not book:
            return {'message': 'Book not found'}, 404
        args = book_parser.parse_args()
        book.title = args['title']
        book.author = args['author']
        book.available_copies = args.get('available_copies', book.available_copies)
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'}), 200
    
    # BookDelete
    def delete(self, book_id):
        book = Books.query.get(book_id)
        if not book:
            return {'message': 'Book not found'}, 404
        db.session.delete(book)
        db.session.commit()
        return '', 204
# Users Resource
class UserResource(Resource):
    # UserRead
    def get(self, user_id=None):
        if user_id:
            user = Users.query.get(user_id)
            if user:
                user_data = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
                logging.debug("Returning user data: %s", user_data)
                return user_data, 200  # Directly returning the dict, Flask-RESTful will serialize it as JSON
            logging.debug("User not found for ID: %s", user_id)
            return {'message': 'User not found'}, 404

        # Fetch all users and serialize them
        users = Users.query.all()
        users_data = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
        logging.debug("Returning all users data: %s", users_data)
        return users_data, 200  # Directly returning the list of dicts

    # Create user
    def post(self):
        args = user_parser.parse_args()
        
        # Check for existing user with the same email
        existing_user = Users.query.filter_by(email=args['email']).first()
        if existing_user:
            return {'message': 'Email already exists.'}, 400
        
        try:
            new_user = Users(name=args['name'], email=args['email'])
            db.session.add(new_user)
            db.session.commit()
            logging.debug("User created successfully: %s", {'id': new_user.id, 'name': new_user.name, 'email': new_user.email})
            return jsonify({'id': new_user.id, 'name': new_user.name, 'email': new_user.email}), 201
            
        except Exception as e:
            logging.error("Error occurred while creating user: %s", str(e), exc_info=True)
            return jsonify({'message': 'An error occurred while creating user.'}), 500

    # UserUpdate
    def put(self, user_id):
        user = Users.query.get(user_id)
        if not user:
            logging.debug("User not found for update with ID: %s", user_id)
            return {'message': 'User not found'}, 404

        args = user_parser.parse_args()
        user.name = args['name']
        user.email = args['email']
        db.session.commit()
        logging.debug("User updated successfully: %s", {'id': user.id, 'name': user.name, 'email': user.email})
        return {
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }, 200

    # UserDelete
    def delete(self, user_id):
        user = Users.query.get(user_id)
        if not user:
            logging.debug("User not found for delete with ID: %s", user_id)
            return jsonify({'message': 'User not found'}), 404
        
        try:
            db.session.delete(user)
            db.session.commit()
            logging.debug("User deleted successfully: %s", user_id)
            return '', 204  # No content response
        
        except Exception as e:
            logging.error("Error occurred while deleting user: %s", str(e), exc_info=True)
            return jsonify({'message': 'An error occurred while deleting user.'}), 500

# Borrow Resource
class BorrowResource(Resource):
    # BorrowRead
    def get(self, borrow_id=None):
        if borrow_id:
            borrow = Borrows.query.get(borrow_id)
            if borrow:
                return {
                    'id': borrow.id,
                    'book_id': borrow.book_id,
                    'user_id': borrow.user_id
                }, 200
            return {'message': 'Borrow not found'}, 404
        borrows = Borrows.query.all()
        return [{'id': borrow.id, 'book_id': borrow.book_id, 'user_id': borrow.user_id} for borrow in borrows], 200

    # BorrowCreate
    def post(self):
        args = borrow_parser.parse_args()
        # Check if book and user exist
        book = Books.query.get(args['book_id'])
        user = Users.query.get(args['user_id'])
        if not book or not user:
            return {'message': 'Book or User not found'}, 404
        
        # Create a new borrow entry
        borrow = Borrows(book_id=args['book_id'], user_id=args['user_id'])
        db.session.add(borrow)
        db.session.commit()
        return {
            'message': 'Borrow created successfully',
            'borrow_id': borrow.id,
            'book_id': borrow.book_id,
            'user_id': borrow.user_id
        }, 201

    # # BorrowUpdate
    # def put(self, borrow_id):
    #     borrow = Borrows.query.get(borrow_id)
    #     if not borrow:
    #         return {'message': 'Borrow not found'}, 404

    #     args = borrow_parser.parse_args()
        # # Update borrow details if needed
        # borrow.book_id = args['book_id']
        # borrow.user_id = args['user_id']
        # db.session.commit()
        
        # return {
        #     'message': 'Borrow updated successfully',
        #     'borrow': {
        #         'id': borrow.id,
        #         'book_id': borrow.book_id,
        #         'user_id': borrow.user_id
        #     }
        # }, 200

    # # BorrowDelete
    # def delete(self, borrow_id):
    #     borrow = Borrows.query.get(borrow_id)
    #     if not borrow:
    #         return {'message': 'Borrow not found'}, 404

    #     db.session.delete(borrow)
    #     db.session.commit()
    #     return '', 204