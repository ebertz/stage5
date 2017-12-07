from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql
app = Flask(__name__)

@app.route('/')
def home():
	con = sql.connect("database.db")
	con.row_factory = sql.Row

	cur = con.cursor()
	cur.execute("select * from comics")
	rows = cur.fetchall()
	return render_template('home.html', rows = rows)

@app.route('/add')
def add_comic():
	return render_template('add_comic.html')

@app.route('/submit', methods=['POST'])
def submit_add_comic():
	try:
		name = request.form['name']
		author = request.form['author']

		with sql.connect("database.db") as con:
			cur = con.cursor()
			cur.execute("INSERT INTO comics VALUES (?,?,?)", (None,name,author) )
		con.commit()
		con.close()
		return redirect(url_for("home"))
	except:
		return redirect(url_for("add_comic"))

@app.route('/search')
def advanced_search():
	return render_template('advanced_search.html')
	
if __name__ == '__main__':
	app.run(debug = True)
