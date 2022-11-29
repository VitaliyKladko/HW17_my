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

    movie = db.relationship("Movie")


# сериализация модели Director
class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


# сериализация модели Genre
class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


# сериализация модели Movie
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Str()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.Nested(GenreSchema)
    director_id = fields.Int()
    director = fields.Nested(DirectorSchema)


api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


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

    def post(self):

        with db.session.begin():
            new_movie_data = request.json
            new_movie = Movie(**new_movie_data)
            db.session.add(new_movie)
            return '', 201


@movie_ns.route('/<int:mid>/')
class MovieViews(Resource):

    def get(self, mid):
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            movie_serialization = movie_schema.dump(movie)
            return movie_serialization, 200
        except NoResultFound as e:
            return {'error': f'{e}'}, 404

    def put(self, mid):
        try:
            update_elements = request.json
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            movie.title = update_elements.get('title')
            movie.description = update_elements.get('description')
            movie.trailer = update_elements.get('trailer')
            movie.year = update_elements.get('year')
            movie.rating = update_elements.get('rating')
            movie.genre_id = update_elements.get('genre_id')
            movie.director_id = update_elements.get('director_id')
            db.session.commit()
            return '', 204
        except NoResultFound as e:
            return {'error': f'{e}'}, 404

    def patch(self, mid):
        try:
            with db.session.begin():
                new_element_data = request.json
                movie = db.session.query(Movie).filter(Movie.id == mid).one()

                if 'title' in new_element_data:
                    movie.title = new_element_data['title']
                    return '', 204

                if 'description' in new_element_data:
                    movie.description = new_element_data['description']
                    return '', 204

                if 'trailer' in new_element_data:
                    movie.trailer = new_element_data['trailer']
                    return '', 204

                if 'year' in new_element_data:
                    movie.year = new_element_data['year']
                    return '', 204

                if 'year' in new_element_data:
                    movie.year = new_element_data['year']
                    return '', 204

                if 'rating' in new_element_data:
                    movie.rating = new_element_data['rating']
                    return '', 204

                if 'genre_id' in new_element_data:
                    movie.genre_id = new_element_data['genre_id']
                    return '', 204

                if 'director_id' in new_element_data:
                    movie.director_id = new_element_data['director_id']
                    return '', 204
        except NoResultFound as e:
            return {'error': f'{e}'}, 404

    def delete(self, mid):
        try:
            with db.session.begin():
                movie = db.session.query(Movie).filter(Movie.id == mid).one()
                db.session.delete(movie)
                return '', 204
        except NoResultFound as e:
            return {'error': f'{e}'}, 404


@director_ns.route('/')
class DirectorsViews(Resource):

    def get(self):
        all_directors = db.session.query(Director).all()
        return directors_schema.dump(all_directors), 200

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

    def get(self, dir_id):
        try:
            director = db.session.query(Director).filter(Director.id == dir_id).one()
            return director_schema.dump(director), 200
        except NoResultFound as e:
            return {'error': f'{e}'}, 404

    def patch(self, dir_id):
        try:
            with db.session.begin():
                new_element_data = request.json
                director = db.session.query(Director).filter(Director.id == dir_id).one()

                if 'name' in new_element_data:
                    director.name = new_element_data['name']
                    return '', 204

        except NoResultFound as e:
            return {'error': f'{e}'}, 404


@genre_ns.route('/')
class GenresViews(Resource):

    def get(self):
        all_genres = db.session.query(Genre).all()
        return genres_schema.dump(all_genres), 201

    def post(self):
        with db.session.begin():
            genre_json = request.json
            new_genre = Genre(**genre_json)
            db.session.add(new_genre)
            return '', 201


@genre_ns.route('/<int:gen_id>/')
class GenreViews(Resource):

    def get(self, gen_id):
        try:
            genre_film = db.session.query(Movie).join(Genre).filter(Genre.id == gen_id)
            return movies_schema.dump(genre_film), 200
        except NoResultFound as e:
            return {'error': f'{e}'}, 404

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

    def patch(self, gen_id):
        try:
            with db.session.begin():
                new_element_data = request.json
                genre = db.session.query(Genre).filter(Genre.id == gen_id).one()

                if 'name' in new_element_data:
                    genre.name = new_element_data['name']
                    return '', 204

        except NoResultFound as e:
            return {'error': f'{e}'}, 404


if __name__ == '__main__':
    app.run(debug=True)
