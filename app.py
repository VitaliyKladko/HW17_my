# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy.exc import NoResultFound
from sqlalchemy import and_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# сериализация модели Movie
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Str()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


# сериализация модели Director
class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


# сериализация модели Genre
class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()

genre_schema = GenreSchema()


@movie_ns.route('/')
class MoviesViews(Resource):
    def get(self):
        all_movies = db.session.query(Movie).all()

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        page = request.args.get('page')

        if director_id:
            all_movies = db.session.query(Movie).filter(Movie.director_id == director_id).all()

        if genre_id:
            all_movies = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()

        if director_id and genre_id:
            all_movies = db.session.query(Movie).filter(
                and_(Movie.director_id == director_id, Movie.genre_id == genre_id)
            ).all()

        if page:
            if page == '1':
                all_movies = db.session.query(Movie).limit(10)
            elif page == '2':
                all_movies = db.session.query(Movie).limit(10).offset(10)
            else:
                return '', 404

        return movies_schema.dump(all_movies), 200


@movie_ns.route('/<int:mid>/')
class MovieViews(Resource):
    def get(self, mid):
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            movie_serialization = movie_schema.dump(movie)
            return movie_serialization, 200
        except NoResultFound as e:
            return {'error': f'{e}'}, 404


@director_ns.route('/')
class DirectorsViews(Resource):

    def post(self):
        with db.session.begin():
            director_json = request.json
            new_director = Director(**director_json)
            db.session.add(new_director)
            return '', 201


@director_ns.route('/<int:dir_id>/')
class DirectorViews(Resource):

    def delete(self, dir_id):
        try:
            with db.session.begin():
                director = db.session.query(Director).filter(Director.id == dir_id).one()
                db.session.delete(director)
                return '', 204
        except NoResultFound as e:
            return {'error': f'{e}'}, 404

    def put(self, dir_id):
        try:
            with db.session.begin():
                director = db.session.query(Director).filter(Director.id == dir_id).one()
                data_json = request.json
                director.name = data_json['name']
                return '', 204
        except NoResultFound as e:
            return {'error': f'{e}'}, 404


@genre_ns.route('/')
class GenresViews(Resource):

    def post(self):
        with db.session.begin():
            genre_json = request.json
            new_genre = Genre(**genre_json)
            db.session.add(new_genre)
            return '', 201


@genre_ns.route('/<int:gen_id>/')
class GenreViews(Resource):

    def delete(self, gen_id):
        try:
            with db.session.begin():
                genre = db.session.query(Genre).filter(Genre.id == gen_id).one()
                db.session.delete(genre)
                return '', 204
        except NoResultFound as e:
            return {'error': f'{e}'}, 404

    def put(self, gen_id):
        try:
            with db.session.begin():
                genre = db.session.query(Genre).filter(Genre.id == gen_id).one()
                data_json = request.json
                genre.name = data_json['name']
                return '', 204
        except NoResultFound as e:
            return {'error': f'{e}'}, 404


if __name__ == '__main__':
    app.run(debug=True)
