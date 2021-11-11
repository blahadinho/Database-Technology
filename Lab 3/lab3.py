from bottle import get, post, run, request, response
import sqlite3

db = sqlite3.connect("movies.sqlite")

@get('/ping')
def get_ping():
	response.status = 200
	return 'pong'


@post('/reset')
def reset_database():
	c = db.cursor()
	c.execute('DELETE FROM theaters')
	c.execute('DELETE FROM customers')
	c.execute('DELETE FROM movies')
	c.execute('DELETE FROM tickets')
	c.execute('DELETE FROM performances')
	c.execute(
		"""
		INSERT INTO theaters(t_name, capacity)
		VALUES
			('Kino',10),
			('Regal',16),
			('Skandia',100);
		""")


@get('/theaters')
def get_theaters():
	c = db.cursor()
	c.execute(
		"""
		SELECT *
		FROM theaters
		"""
	)
	found = [{'t_name': t_name, 'capacity': capacity} for t_name, capacity in c]
	response.status = 200
	return {'data': found}


@get('/users/<username>/tickets')
def get_customers(username):
	c = db.cursor()
	c.execute(
		"""
		WITH nbr_tickets AS (
			SELECT performance_id, count() as nbr_of_tickets
			FROM tickets
			JOIN performances
			USING (performance_id)
			GROUP BY u_name, performance_id
			HAVING u_name = ?
		)
		SELECT  start_date, start_time, t_name, title, production_year, nbr_of_tickets
		FROM    nbr_tickets
		JOIN    performances
		USING   (performance_id)
		JOIN    movies
		USING   (IMDB_key)
		""",
		[username]
	)
	found = [{"date": start_date, "startTime": start_time, "theater": t_name, "title": title, "year": year, "nbrOfTickets": nbrOfTickets}
	         for start_date, start_time, t_name, title, year, nbrOfTickets in c]
	response.status = 200
	return {"data": found}


@get('/movies')
def get_movies():

	c = db.cursor()
	query = """
		SELECT  IMDB_key, title, production_year
		FROM    movies
		WHERE   1 = 1
		"""
	params = []
	if request.query.title:
		query += " AND title = ? "
		params.append(request.query.title)
	if request.query.year:
		query += " AND production_year = ? "
		params.append(request.query.year)
	c.execute(query, params)

	found = [{"imdbKey": imdbKey, "title": title, "year": year}
			  for imdbKey, title, year in c]
	response.status = 200
	return {"data": found}


@get('/movies/<imdb_key>')
def get_movies(imdb_key):

	c = db.cursor()
	c.execute(
		"""
		SELECT  IMDB_key, title, production_year
		FROM    movies
		WHERE   IMDB_key = ?
		""", [imdb_key]
	)

	found = [{"imdbKey": imdbKey, "title": title, "year": year}
			  for imdbKey, title, year in c]
	response.status = 200
	return {"data": found}


@get('/performances')
def get_performances():
	c = db.cursor()
	c.execute(
		"""
		WITH tickets_count AS (
			SELECT performance_id, count() AS taken_seats
			FROM tickets
			GROUP BY performance_id
		),
			tickets_count_full AS (
			SELECT performances.performance_id, COALESCE(taken_seats,0) AS seats_taken
			FROM performances
			LEFT JOIN tickets_count
				ON performances.performance_id = tickets_count.performance_id
			
		)
		SELECT  performance_id, t_name, start_date, start_time, title, production_year, (capacity-seats_taken) AS remainingSeats
		FROM    performances
		JOIN movies 
		USING (IMDB_key)
		JOIN theaters
		USING  (t_name)
		JOIN tickets_count_full
		USING (performance_id)
		"""
	)

	found = [{"performanceId": performance_id, "date": start_date, "startTime": start_time, "title": title,
				"year": production_year, "theater": t_name, "remainingSeats": remainingSeats}
				for performance_id, t_name, start_date, start_time, title, production_year, remainingSeats in c]
	response.status = 200
	return {"data": found}


@post('/users')
def create_user():
	user = request.json
	c = db.cursor()
	try:
		c.execute(
			"""
			INSERT INTO customers(u_name, f_name, p_word)
			VALUES (?,?,?)
			""",
			[user['username'], user['fullName'], hash(user['pwd'])]
		)
		response.status = 201
		db.commit()
		return '/users/' + user['username']
	except sqlite3.IntegrityError:
		response.status = 400
		return ''


@post('/movies')
def create_movie():
	movie = request.json
	c = db.cursor()
	try:
		c.execute(
			"""
			INSERT INTO movies(IMDB_key, title, production_year)
			VALUES (?,?,?)
			""",
			[movie['imdbKey'], movie['title'], movie['year']]
		)
		response.status = 201
		db.commit()
		return '/movies/' + movie['imdbKey']
	except sqlite3.IntegrityError:
		response.status = 400
		return ''


@post('/performances')
def create_performances():
	performance = request.json
	c = db.cursor()
	try:
		c.execute(
			"""
			INSERT INTO performances(t_name, start_date, start_time, IMDB_key)
			VALUES (?,?,?,?)
			""",
			[performance['theater'], performance['date'], performance['time'], performance['imdbKey']]
		)
		c.execute(
			"""
			SELECT performance_id
			FROM performances
			WHERE rowid = last_insert_rowid()
			"""
		)
		db.commit()
		response.status = 201
		return '/performances/' + c.fetchall()[0][0]
	except sqlite3.IntegrityError:
		response.status = 400
		return 'No such movie or theater'


@post('/tickets')
def post_tickets():
	ticket = request.json
	c = db.cursor()

	c.execute(
		"""
		WITH tickets_count AS (
			SELECT performance_id, count() AS taken_seats
			FROM tickets
			GROUP BY performance_id
		),
			tickets_count_full AS (
			SELECT performances.performance_id, COALESCE(taken_seats,0) AS seats_taken
			FROM performances
			LEFT JOIN tickets_count
				ON performances.performance_id = tickets_count.performance_id
		)
		SELECT  performance_id, (capacity-seats_taken) AS remainingSeats
		FROM    performances
		JOIN movies 
		USING (IMDB_key)
		JOIN theaters
		USING  (t_name)
		JOIN tickets_count_full
		USING (performance_id)
		WHERE performance_id = ?
		""",
		[ticket['performanceId']]
	)

	ticket_nbrs = [{"remainingSeats": remainingSeats, "performance_id": performance_id} for performance_id,remainingSeats in c]

	if len(ticket_nbrs) == 0:
		response.status = 400
		return 'Error'

	if ticket_nbrs[0]['remainingSeats'] <= 0:
		response.status = 400
		return 'No tickets left'

	try:
		c.execute(
			""" 
			SELECT u_name
			FROM customers
			WHERE u_name = ? AND p_word = ? 
			""",
			[ticket['username'], hash(ticket['pwd'])]
		)
	# Måste jag ha ett found-statement här?
	except sqlite3.IntegrityError:
		response.status = 401
		return "Wrong user credentials"

	if len(c.fetchall()[0]) == 0:
		response.status = 401
		return "Wrong user credentials"

	try:
		c.execute(
			""" 
			INSERT
			INTO tickets(u_name, performance_id)
			VALUES (?, ?)
			 """,
			[ticket['username'], ticket['performanceId']]

		)
		c.execute(
			"""
			SELECT ticket_id
			FROM tickets
			WHERE rowid = last_insert_rowid()
			"""
		)
		response.status = 201
		return '/tickets/' + c.fetchall()[0][0]

	except sqlite3.IntegrityError:
		response.status = 400
		return 'Error'


def hash(msg):
	import hashlib
	return hashlib.sha256(msg.encode('utf-8')).hexdigest()


run(host='localhost', port=7007)
