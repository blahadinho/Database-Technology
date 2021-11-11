from bottle import get, post, run, request, response
import sqlite3
import urllib

db = sqlite3.connect("krusty_kookies.sqlite")

# curl -X GET http://localhost:8888/ping
@get('/ping')
def get_ping():
	response.status = 200
	return 'pong'

# curl -X POST http://localhost:8888/reset
@post('/reset')
def reset():
	c = db.cursor()
	c.execute('DELETE FROM cookies')
	c.execute('DELETE FROM recipe_lines')
	c.execute('DELETE FROM ingredients')
	c.execute('DELETE FROM materials')
	c.execute('DELETE FROM blocked')
	c.execute('DELETE FROM customers')
	c.execute('DELETE FROM deliveries')
	c.execute('DELETE FROM orders')
	c.execute('DELETE FROM order_entries')
	c.execute('DELETE FROM pallets')
	db.commit()
	response.status = 205
	return {'location': '/'} # Här ska det va något annat(?)

# curl -H "Content-Type: application/json" -X POST http://localhost:8888/customers -d "{\"name\": \"Socker bagarna\", \"address\": \"Lund\"}"
@post('/customers')
def customers():
	customer = request.json
	c = db.cursor()

	try: 
		c.execute(
			"""
            INSERT
            INTO    customers(customer_name, address)
            VALUES  (?, ?)
            """,
            [customer['name'], customer['address']]
        )
		response.status = 201
		loc = '/customers/' + urllib.parse.quote(customer['name'])
		db.commit()
		return {'location' : loc}
	except: #sqlite3.IntegrityError: (Ändrade här för att testa om den går in här, innan fick status 500, gav fel i testet)
		response.status = 401
		db.commit()
		return response.status

#curl -X GET http://localhost:8888/customers
@get('/customers')
def get_customers():
	c = db.cursor()
	c.execute(
        """
        SELECT  customer_name, address
        FROM    customers
        """
    )
	found = [{"name": customer_name, "address": address} for customer_name, address, in c]
	response.status = 200
	return {"data": found}

# curl -H "Content-Type: application/json" -X POST http://localhost:8888/cookies -d "{\"name\": \"Havreflarn\", \"recipe\": []{}\"Lund\"}"
@post('/cookies')
def add_cookies():
	cookie = request.json
	c = db.cursor()
	try:

		cookie_name = cookie["name"]
		c.execute(
			"""
			INSERT INTO cookies
			VALUES (?)
			""",
			[cookie_name]
		)

		for line in cookie["recipe"]:

			c.execute(
				"""
				INSERT INTO recipe_lines
				VALUES (?, ?, ?)
				""",
				[line["ingredient"], line["amount"], cookie_name]
			)
		response.status = 201
		loc = '/cookies/' + urllib.parse.quote(cookie_name)
		return {'location' : loc}

	except sqlite3.IntegrityError:
		response.status = 400
		return 'Error'



#curl -X GET http://localhost:8888/cookies
@get('/cookies')
def get_cookies():
	c = db.cursor()
	c.execute(
		"""
		WITH blocked_pallets AS (
			SELECT pallet_id
			FROM pallets
			JOIN blocked
			USING (cookie)
			WHERE pallet_date BETWEEN blocked_from AND blocked_to
			), cookie_pallets AS (
			SELECT cookie, count() AS nbr_pallets
			FROM pallets
			WHERE pallet_id NOT IN blocked_pallets
			GROUP BY cookie
		)
		SELECT cookies.cookie, coalesce(nbr_pallets, 0) AS count_pallets
		FROM cookies
		LEFT JOIN cookie_pallets
		ON cookies.cookie = cookie_pallets.cookie
		"""
	)
	found = [{"name": cookie, "pallets": count_pallets} for cookie, count_pallets in c]
	response.status = 200
	return {"data": found}

#curl -X GET http://localhost:8888/cookies/<cookie_name>/recipe
@get('/cookies/<cookie_name>/recipe')
def get_cookie(cookie_name):
	cookie_name = urllib.parse.urlparse(cookie_name).path
	c = db.cursor()
	c.execute(
		"""
		SELECT ingredient, amount, unit
		FROM recipe_lines
		JOIN ingredients
		USING (ingredient)
		WHERE cookie = ?
		""", [cookie_name] # här ska det stå cookie_name
	)
	if c.rowcount == 0:
		response.status = 404
		return {"data": []}
	found = [{'ingredient': ingredient, 'amount': amount, 'unit': unit} 
			  for ingredient, amount, unit in c]
	response.status = 200
	return {"data": found}




# curl -H "Content-Type: application/json" -X POST http://localhost:1337/ingredients -d "{\"ingredient\": \"Bread Crumbs\", \"unit\": \"g\"}"
@post('/ingredients')
def ingredients():
	ingredient = request.json
	c = db.cursor()

	try: 
		c.execute(
			"""
            INSERT
            INTO    ingredients(ingredient, unit)
            VALUES  (?, ?)
            """,
            [ingredient['ingredient'], ingredient['unit']]
        )
		response.status = 201
        #db.commit()

		loc = '/ingredients/' + urllib.parse.quote(ingredient['ingredient'])
		return {'location' : loc}
	except sqlite3.IntegrityError:
		response.status = 401
		return response.status

#curl -H "Content-Type: application/json" -X POST http://localhost:1337/ingredients/Bread%20Crumbs/deliveries -d "{\"delliveryTime\": \"2021-03-05 10:30:00\", \"quantity\": \"2000\"}"
@post('/ingredients/<ingredient>/deliveries') # osäker på om vi kan ha deliveries här eller om vi ska byta till materials på slutet?
def update_stock(ingredient):
	upd_quantity = request.json
	c = db.cursor()
	
	c.execute(
		'''
		SELECT ingredient
		FROM materials
		WHERE ingredient = ?
		''',
		[urllib.parse.urlparse(ingredient).path]
	)

	if c.fetchone() == None:
		c.execute(
			'''
			INSERT 
			INTO materials(ingredient, available_amount)
			VALUES (?,?)
			''',
			[urllib.parse.urlparse(ingredient).path, upd_quantity['quantity']]
		)

	else:
		c.execute(
			'''
			UPDATE materials
			SET available_amount = available_amount + ?
			WHERE ingredient = ?
			''',
			[upd_quantity['quantity'], urllib.parse.urlparse(ingredient).path]
		)
	c.execute(
		'''
		SELECT ingredient, available_amount, unit
		FROM materials
		JOIN ingredients
		USING (ingredient)
		WHERE ingredient = ?
		''',
		[urllib.parse.urlparse(ingredient).path]
	)
	
	found = [{'ingredient': urllib.parse.urlparse(ingredient).path, 'available_amount': available_amount, 'unit': unit} for ingredient, available_amount, unit in c]

	response.status = 201

	return {'data': found}

#NEDAN IFALL VI KÖR LOGG 
# @post('/ingredients/<ingredient>/deliveries') # osäker på om vi kan ha deliveries här eller om vi ska byta till materials på slutet?
# def update_stock(ingredient):
# 	upd_quantity = request.json
# 	c = db.cursor()
# 	c.execute(
# 		'''
# 		INSERT 
# 		INTO materials(ingredient, available_amount)
# 		VALUES (?,?)
# 		''',
# 		[urllib.parse.urlparse(ingredient).path, upd_quantity['quantity']]
# 	)
# 	c.execute(
# 		'''
# 		SELECT ingredient, available_amount, unit
# 		FROM materials
# 		JOIN ingredients
# 		USING (ingredient)
# 		WHERE ingredient = ?
# 		''',
# 		[urllib.parse.urlparse(ingredient).path]
# 	)
# 	found = [{'ingredient': urllib.parse.urlparse(ingredient).path, 'available_amount': available_amount, 'unit': unit} for ingredient, available_amount, unit in c]
# 	response.status = 201
# 	return {'data': found}



#curl -X GET http://localhost:1337/ingredients 
@get('/ingredients')
def get_all_ingredients():
	c = db.cursor()

	c.execute(
		'''
		SELECT ingredient, available_amount, unit
		FROM materials
		JOIN ingredients
		USING (ingredient)
		'''
	)
	
	found = [{'ingredient': ingredient, 'available_amount': available_amount, 'unit': unit} for ingredient, available_amount, unit in c]
	response.status = 200
	return {'data' : found}


@post('/pallets')
def post_pallet():
	pallet = request.json
	c = db.cursor()


	try: 
		c.execute(
			"""
			WITH recipe_cookie(ingredient) AS (
				SELECT ingredient 
				FROM recipe_lines
				WHERE cookie = ?
			)

            UPDATE materials
            SET available_amount = available_amount - 54*(SELECT amount FROM recipe_lines WHERE cookie = ? AND materials.ingredient = recipe_lines.ingredient)
			WHERE ingredient IN recipe_cookie 
            """,
            [pallet['cookie'], pallet['cookie']]
        )
		c.execute(
			"""
            INSERT
            INTO    pallets(cookie)
            VALUES  (?)
            """,
            [pallet['cookie']]
        )
		c.execute(
			"""
			SELECT pallet_id
			FROM pallets
			WHERE rowid = last_insert_rowid() 
			"""
		)
		response.status = 201
		loc = '/pallets/' + urllib.parse.quote(str(c.fetchone()))
		return {'location' : loc}
	except:
		response.status = 422
		return {'location': []}



@post('/cookies/<cookie_name>/block')
def block(cookie_name):
	if request.query.after:
		from_date = request.query.after
	else:
		from_date = '0000-01-01'
	if request.query.before:
		to_date = request.query.before
	else:
		to_date = '9999-12-31'

	c = db.cursor()
	query = """
			INSERT INTO blocked(cookie, blocked_from, blocked_to)
			VALUES  (?, ?, ?)
			"""
	c.execute(
		query,[cookie_name, from_date, to_date]
	)
	response.status = 205
	return ''


@post('/cookies/<cookie_name>/unblock')
def block(cookie_name):
	if request.query.after:
		from_date = request.query.after
	else:
		from_date = '0000-01-01'
	if request.query.before:
		to_date = request.query.before
	else:
		to_date = '9999-12-31'

	c = db.cursor()
	c.execute(
		"""
		DELETE FROM blocked
		WHERE cookie = ? AND blocked_from >= ? AND blocked_to <= ?
		""", [cookie_name, from_date, to_date]
	)	
	response.status = 205
	return ''




run(host='localhost', port=1337)
