import json
import hashlib
import requests
import sqlite3 as sql



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

def add_users():
	cmd = input("Delete existing USERS database? [y/n]")
	if cmd is "y":
		cur.execute('drop table users')
		cur.execute(
			'CREATE TABLE users(#ADD SCHEME HERE)')

def add_reviews():
	cmd = input("Delete existing REVIEWS database? [y/n]")
	if cmd is "y":
		cur.execute('drop table reviews')
		cur.execute(
			'CREATE TABLE reviews(#ADD SCHEME HERE)')

def add_listings():
	cmd = input("Delete existing LISTINGS database? [y/n]")
	if cmd is "y":
		cur.execute('drop table listings')
		cur.execute(
			'CREATE TABLE listings(#ADD SCHEME HERE)')

def add_purchases():
	cmd = input("Delete existing PURCHASES database? [y/n]")
	if cmd is "y":
		cur.execute('drop table purchases')
		cur.execute(
			'CREATE TABLE purchases(#ADD SCHEME HERE)')


def add_comics():
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
			name = ""
			#print(str(list(comic['creators'].items())))
			try:
				name = list(comic['creators'].items())[2][1][1]['name']
			except:
				pass
			#skip incomplete entries
			if name is "":
				continue
			if comic['description'] is None:
				continue

			#print(type(thing))
			#for schema comic (CID, title, issue, author, description, image
			cur.execute('INSERT into comics VALUES(?,?,?,?,?)',
						(None, comic['title'], comic['issueNumber'], name, comic['description']))
			comics_added += 1
		con.commit()
		offset += 100
		total_added += comics_added
		print('added '+ str(comics_added) + ' entries to comics database. TOTAL ENTRIES = ' + str(count + total_added))

	con.close()


if __name__ == '__main__':
	select_function()



