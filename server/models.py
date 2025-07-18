from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-recipes.user', '-_password_hash',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationships
    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')

    # Password setter and getter
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        hashed_password = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')
        self._password_hash = hashed_password

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    # Validations
    @validates('username')
    def validate_username(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Username must be present.")
        return value

# class User(db.Model, SerializerMixin):
#     __tablename__ = 'users'
    
#     serialize_rules = ('-recipes.user', '-_password_hash',)

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String, unique=True, nullable=False)
#     _password_hash = db.Column(db.String, nullable=False)
#     image_url = db.Column(db.String)
#     bio = db.Column(db.String)

#     recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')
    
#     # @hybrid_property
#     # def password_hash(self):
#     #     return self._password_hash
#     @hybrid_property
#     def password_hash(self):
#         raise AttributeError("Password hashes may not be viewed.")


#     @password_hash.setter
#     def password_hash(self, password):
#         # utf-8 encoding and decoding is required in python 3
#         password_hash = bcrypt.generate_password_hash(
#             password.encode('utf-8'))
#         self._password_hash = password_hash.decode('utf-8')

#     def authenticate(self, password):
#         return bcrypt.check_password_hash(
#             self._password_hash, password.encode('utf-8'))
        
#     @validates('username')
#     def validate_username(self, key, value):
#         if not value or value.strip() == "":
#             raise ValueError("Username must be present.")
#         return value



class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='recipes')

    @validates('title')
    def validate_title(self, key, value):
        if not value:
            raise ValueError("Title must be present.")
        return value

    @validates('instructions')
    def validate_instructions(self, key, value):
        if not value or len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters.")
        return value