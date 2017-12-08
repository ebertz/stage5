import json
import hashlib
import requests
import sqlite3 as sql

timestamp = b'1'
url = 'http://gateway.marvel.com/v1/public/comics'
public_key = b'4933b5ad40b6ffa295fee233cb8bb9fb'
private_key = b'aa6e53144b51e664b670df5751d688a18054be74'

hash = hashlib.md5()
hash.update(timestamp + private_key + public_key)



con = sql.connect("database.db")
con.row_factory = sql.Row
cur = con.cursor()

cnt = cur.execute("SELECT COUNT(*) from comics")
count = cur.fetchone()[0]

print('Database currently contains ' + str(count) + ' comics.')
cmd = input("Delete existing database? [y/n]")
if cmd is "y":
	cur.execute('drop table comics')
	cur.execute('CREATE TABLE comics(CID INTEGER PRIMARY KEY, title TEXT, issueNumber INTEGER, author TEXT, description TEXT)')
	print('initialized empty database')
	count = 0;

offset = count
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






