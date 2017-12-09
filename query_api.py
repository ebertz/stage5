import json
import hashlib
import requests
import sqlite3 as sql
import random



con = sql.connect("database.db")
con.row_factory = sql.Row
cur = con.cursor()

def select_function():
	op = int(input("Add entries to which table?\n1. Comics\n2. Users\n3. Reviews\n4. Listings\n5. Purchases"))
	if op is 1:
		add_comics()
	elif op is 2:
		add_users()
	elif op is 3:
		add_reviews()
	elif op is 4:
		add_listings()
	elif op is 5:
		add_purchases()
	else:
		print("select a value [1-5]")
		exit(0)

def rand_date():
	date = ""
	date += str(random.randint(1, 12)) + '/'
	date += str(random.randint(1, 28)) + '/'
	date += str(random.randint(2005, 2017))
	return date

def add_users():
	cmd = input("Delete existing USERS database? [y/n]")
	if cmd is "y":
		cur.execute(
			'CREATE TABLE IF NOT EXISTS users(UID INTEGER PRIMARY KEY, name TEXT, email TEXT, age INTEGER)')
		cur.execute('DELETE from users')
		con.commit()

	letters = 'abcdefghijklmnopqrstuvwxyz'
	num=int(input("add how many?"))
	for i in range(num):
		name = ""
		for k in range(random.randint(4,12)):
			name += random.choice(letters)
		email = name + random.choice(['@gmail.com', '@wisc.edu', '@hotmail.com', '@email.net', '@yahoo.com'])
		age = random.randint(15,55)

		cur.execute('INSERT INTO users VALUES(?,?,?,?)', (None, name, email, age))
	con.commit()

def add_reviews():
	cmd = input("Delete existing REVIEWS database? [y/n]")
	if cmd is "y":
		cur.execute(
			'CREATE TABLE IF NOT EXISTS reviews(RID INTEGER PRIMARY KEY, userID INTEGER, CID INTEGER, date TEXT, rating INTEGER, body TEXT, FOREIGN KEY(CID) REFERENCES comics(CID),FOREIGN KEY(userID) REFERENCES users(UID))')
		cur.execute('DELETE from reviews')
		con.commit()

	body_list = ['This comic was terrible!', 'This issue was pretty dissapointing.', 'It was a decent read, but I was hoping for more', 'A great and exciting story!', 'One of my favorite comics of all time!']

	cur.execute('SELECT * FROM comics ORDER BY RANDOM()')
	comics = cur.fetchall()

	num = int(input('add how many reviews?'))
	cur.execute('SELECT COUNT(*) FROM users')
	num_users = cur.fetchone()[0]
	cur.execute('SELECT COUNT(*) FROM comics')
	num_comics = cur.fetchone()[0]

	for i in range(num):

		date = rand_date()
		rating = random.randint(1,5)
		body = body_list[rating - 1]
		cid = comics[random.randint(1,num_comics - 1)]['CID']
		uid = random.randint(1,num_users - 1)
		#uid = users[i]['UID']
		cur.execute('INSERT INTO reviews VALUES(?,?,?,?,?,?)', (None, uid, cid, date, rating, body))

	con.commit()
	con.close()



def add_listings():
	cmd = input("Delete existing LISTINGS database? [y/n]")
	if cmd is "y":
		cur.execute(
			'CREATE TABLE IF NOT EXISTS listings(LID INTEGER PRIMARY KEY, UID INTEGER, CID INTEGER, price REAL, date TEXT, FOREIGN KEY(CID) REFERENCES comics(CID), FOREIGN KEY(UID) REFERENCES users(UID))')
		cur.execute('DELETE from listings')
		con.commit()

	cur.execute('SELECT COUNT(*) FROM users')
	num_users = cur.fetchone()[0]
	cur.execute('SELECT COUNT(*) FROM comics')
	num_comics = cur.fetchone()[0]

	num = int(input('add how many?'))
	for i in range(num):
		uid = random.randint(1,num_users - 1)
		cid = random.randint(1, num_comics - 1)
		price = random.randint(0,12)
		price += (float(random.randint(0,99))/100)
		date = rand_date()

		cur.execute('INSERT INTO listings VALUES(?,?,?,?,?)', (None, uid, cid, price, date))
	con.commit()
	con.close()





def add_purchases():
	cmd = input("Delete existing PURCHASES database? [y/n]")
	if cmd is "y":
		cur.execute(
			'CREATE TABLE IF NOT EXISTS purchases(PID INTEGER PRIMARY KEY, seller INTEGER, buyer INTEGER,  CID INTEGER, date TEXT, FOREIGN KEY(CID) REFERENCES comics(CID), FOREIGN KEY(seller) REFERENCES users(UID),FOREIGN KEY(buyer) REFERENCES users(UID))')
		cur.execute('DELETE from purchases')
		con.commit()

	cur.execute('SELECT COUNT(*) FROM users')
	num_users = cur.fetchone()[0]
	cur.execute('SELECT COUNT(*) FROM comics')
	num_comics = cur.fetchone()[0]
	num = int(input('add how many?'))
	for i in range(num):
		seller = random.randint(1, num_users - 1)
		buyer = random.randint(1, num_users - 1)
		cid = random.randint(1, num_comics - 1)
		date = rand_date()
		cur.execute('INSERT INTO purchases VALUES(?,?,?,?,?)', (None, seller, buyer, cid, date))
	con.commit()
	con.close()


def add_comics():


	cmd = input("Delete existing COMICS database? [y/n]")
	if cmd is "y":
		cur.execute(
			'CREATE TABLE IF NOT EXISTS comics(CID INTEGER PRIMARY KEY, title TEXT, issueNumber INTEGER, author TEXT, description TEXT, image TEXT)')
		cur.execute('DELETE from comics')
		con.commit()

	cnt = cur.execute("SELECT COUNT(*) from comics")
	count = cur.fetchone()[0]
	offset = count
	print('Database currently contains ' + str(count) + ' comics.')


	#hash API keys
	timestamp = b'1'
	url = 'http://gateway.marvel.com/v1/public/comics'
	public_key = b'4933b5ad40b6ffa295fee233cb8bb9fb'
	private_key = b'aa6e53144b51e664b670df5751d688a18054be74'

	hash = hashlib.md5()
	hash.update(timestamp + private_key + public_key)


	cmd = input('Add how many comics?')
	cmd = int(cmd)
	if cmd > 100000:
		print('Too many!')
		exit(0)

	print('Adding ' + str(cmd) + 'comics to the database.')
	max_entries = offset + cmd
	total_added = 0
	while total_added < cmd:
		limit = min(100, cmd - total_added)

		params = {'apikey':public_key,
			 'ts':timestamp,
			 'hash':hash.hexdigest(),
			 'format':'comic',
			 'formatType':'comic',
			 'limit':str(limit),
			 'offset':str(offset)
			}


		response = requests.get(url, params)
		input_dict = json.loads(response.content.decode())
		try:
			data = input_dict['data']['results']
		except:
			offset += 100
			continue


		comics_added = 0
		for comic in data:

			image = ""
			name = ""
			#print(str(list(comic['creators'].items())))
			try:
				name = list(comic['creators'].items())[2][1][1]['name']
				image = comic['thumbnail']['path'] + '.' + comic['thumbnail']['extension']
			except:
				pass
			#skip incomplete entries
			if name is "":
				continue
			if comic['description'] is None:
				continue

			#print(type(thing))
			#for schema comic (CID, title, issue, author, description, image
			cur.execute('INSERT into comics VALUES(?,?,?,?,?,?)',
						(None, comic['title'], comic['issueNumber'], name, comic['description'], image))
			comics_added += 1
		con.commit()
		offset += 100
		total_added += comics_added
		print('added '+ str(comics_added) + ' entries to comics database. TOTAL ENTRIES = ' + str(count + total_added))

	con.close()


if __name__ == '__main__':
	select_function()



