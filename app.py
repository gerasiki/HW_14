from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['DEBUG'] = True


def connect_db(query):
    connection = sqlite3.connect('netflix.db')
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connection.close()
    return result


@app.route("/movie/<title>")
def get_by_title(title):
    query = f"""SELECT 
                    title
                    , country
                    , release_year
                    , listed_in AS genre
                    , description                    FROM netflix
                    WHERE title LIKE '%{title}%'
                    ORDER BY release_year DESC"""
    try:
        response = connect_db(query)[0]
        movie_dict = {
            'title': response[0],
            'country': response[1],
            'release_year': response[2],
            'genre': response[3],
            'description': response[4].strip()

        }
        return jsonify(movie_dict)
    except IndexError:
        return 'Фильм не найден'


@app.route("/movie/<int:start>/to/<int:end>")
def get_by_period(start, end):
    query = f"""SELECT 
                        title
                        , release_year
                    FROM netflix
                    WHERE release_year BETWEEN {start} AND {end}
                    ORDER BY release_year
                    LIMIT 100"""
    response = connect_db(query)
    movie_list = []
    for movie in response:
        movie_list.append({'title': movie[0], 'release_year': movie[1]})
    if len(movie_list) >= 1:
        return jsonify(movie_list)
    else:
        return 'Фильмы не найдены'


@app.route("/movie/rating/<group>")
def get_by_rating(group):
    ratings = {'children': ['G'], 'family': ['G', 'PG', 'PG-13'], 'adult': ['R', 'NC-17']}
    if group in ratings:
        rating = '", "'.join(ratings[group])
        rating = f'"{rating}"'
    else:
        return 'Фильмы не найдены'

    query = f"""SELECT title
                            , rating 
                            , description
                    FROM netflix 
                    WHERE rating IN ({rating})"""
    response = connect_db(query)
    movie_list = []
    for movie in response:
        movie_list.append({'title': movie[0], 'rating': movie[1], 'description': movie[2].strip()})
    if len(movie_list) >= 1:
        return jsonify(movie_list)
    else:
        return 'Фильмы не найдены'


@app.route("/genre/<genre>")
def get_film_by_genre(genre):
    query = f"""SELECT title
                    , description 
                    FROM netflix
                    WHERE listed_in LIKE '%{genre}%'
                    ORDER BY release_year DESC
                    LIMIT 10"""
    response = connect_db(query)
    movie_list = []
    for movie in response:
        movie_list.append({'title': movie[0], 'description': movie[1].strip()})
    if len(movie_list) >= 1:
        return jsonify(movie_list)
    else:
        return 'Фильмы не найдены'


def get_two_actors(actor_1, actor_2):
    query = f"""
                    SELECT "cast"
                    FROM netflix
                    WHERE "cast" LIKE '%{actor_1}%' 
                    AND "cast" LIKE '%{actor_2}%'
                """
    response = connect_db(query)
    cast_list = []
    for actors in response:
        cast_list.extend(actors[0].split(', '))
    cast_result = []
    for actor in cast_list:
        if actor not in [actor_1, actor_2]:
            if cast_list.count(actor) > 2:
                cast_result.append(actor)
    cast_result = set(cast_result)
    return cast_result


# print(get_two_actors('Jack Black', 'Dustin Hoffman'))

def get_movie(type_, year, genre):
    query = f"""
                SELECT title
                , description 
                FROM netflix
                WHERE "type" = '{type_}'
                AND release_year = '{year}'
                AND listed_in LIKE '%{genre}%'
                """
    response = connect_db(query)
    movie_list = []
    for movie in response:
        movie_list.append({'title': movie[0], 'description': movie[1].strip()})
    return movie_list

# print(get_movie('Movie', 2016, 'Horror'))


if __name__ == '__main__':
    app.run()
