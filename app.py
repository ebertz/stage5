from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql
app = Flask(__name__)


@app.route('/')
def home():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()

	q = request.args.get('q', type = str)

	if q is not None:
		q = '%' + q + '%'
		cur.execute("SELECT COUNT(*) from comics where title like ?", (q,))
		count = cur.fetchone()[0]
		cur.execute("select * from comics where title like ? limit 1000", (q,))

	else:
		cur.execute("SELECT COUNT(*) from comics")
		count = cur.fetchone()[0]
		cur.execute("select * from comics limit 1000")

	rows = cur.fetchall()
	return render_template('home.html', rows = rows, count = count, q = q)


@app.route('/comic/<int:cid>')
def comic(cid):
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()

	cur.execute("select * from comics where CID = ?", (cid,))
	row = cur.fetchone()

	cur.execute("select l.*, u.name from listings as l, users as u WHERE l.UID = u.UID AND l.CID = ?", (cid,))
	listings = cur.fetchall()

	cur.execute("select r.*, u.name from reviews as r, users as u WHERE r.userID = u.UID AND  r.CID = ?", (cid,))
	reviews = cur.fetchall()

	return render_template('comic.html', row = row, listings = listings, reviews = reviews)

@app.route('/add')
def add_comic():
	return render_template('add_comic.html')

@app.route('/submit', methods=['POST'])
def submit_add_comic():
	try:
		name = request.form['name']
		author = request.form['author']
		issueNumber = request.form['issueNumber']
		description = request.form['description']
		image = request.form['image']

		with sql.connect("database.db") as con:
			cur = con.cursor()
			cur.execute("INSERT INTO comics VALUES (?,?,?,?,?,?)", (None,name,author, issueNumber, description,image) )
		con.commit()
		con.close()
		return redirect(url_for("home"))
	except:
		return redirect(url_for("add_comic"))

@app.route('/search')
def advanced_search():
	con = sql.connect("database.db")
	con.row_factory = sql.Row
	cur = con.cursor()


	listings = cur.execute('SELECT l.price, l.date, c.title, u.name from listings as l, comics as c, users as u WHERE l.UID = u.UID AND c.CID = l.CID').fetchall()


	con.close()
	return render_template('advanced_search.html', listings = listings)
	



if __name__ == '__main__':
	app.run(debug = True)
