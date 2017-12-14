from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql

app = Flask(__name__)


@app.route('/')
def home():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    # q = request.args.get('q', type = str)
    cur.execute("SELECT COUNT(*) from comics")
    count = cur.fetchone()[0]
    cur.execute("select * from comics limit 1000")
    comics = cur.fetchall()

    cur.execute("SELECT COUNT(*) from reviews")
    r_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) from listings")
    l_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) from purchases")
    p_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) from users")
    u_count = cur.fetchone()[0]

    # cur.execute("select * from purchases")
    cur.execute(
        "select u.name, c.title, c.author, p.* FROM users as u, comics as c, purchases as p WHERE p.buyer = u.UID AND c.CID = p.CID limit 1000")
    purchases = cur.fetchall()
    cur.execute("select * from users limit 1000")
    users = cur.fetchall()
    cur.execute(
        "select r.*, u.name, c.title, c.author from reviews as r, users as u, comics as c WHERE r.userID = u.UID AND  r.CID = c.CID limit 1000")
    reviews = cur.fetchall()
    cur.execute(
        "select l.*, u.name, c.title, c.author from listings as l, comics as c, users as u WHERE l.UID = u.UID AND c.CID = l.CID limit 1000")
    listings = cur.fetchall()

    return render_template('home.html', rows=comics, count=count, r_count=r_count, l_count=l_count, p_count=p_count,
                           u_count=u_count,
                           purchases=purchases, users=users, reviews=reviews, listings=listings)


@app.route('/results', methods=['GET', 'POST'])
def results():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    _type = request.form['type']
    # build search query from strings
    _select = "SELECT "
    _from = " FROM "
    _where = " WHERE "
    _args = ()
    print(_type.encode())
    # build query based on appropriate table
    if _type == "c":
        min_rating = request.form['min']
        max_rating = request.form['max']
        title = request.form['title']
        author = request.form['author']
        cid = request.form['id']

        _select += "c.*"
        _from += "comics as c"

        if min_rating != "":
            _where += "(SELECT avg(r.rating) FROM reviews as r WHERE r.CID = c.CID) >= ?"
            _args = _args + tuple([int(min_rating)])

        if max_rating != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += "(SELECT avg(r.rating) FROM reviews as r WHERE r.CID = c.CID) <= ?"
            _args = _args + tuple([int(max_rating)])

        if title != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += " title LIKE ?"
            arg_str = "%" + title + "%"
            _args += tuple([arg_str])
        if author != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += " author LIKE ?"
            arg_str = "%" + author + "%"
            _args += tuple([arg_str])
        if cid != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += " CID = ?"
            _args += tuple([int(cid)])



    elif _type == 'l':
        _select += "l.*, c.title, c.author"
        _from += "listings as l, comics as c"
        min_price = request.form['min']
        max_price = request.form['max']
        title = request.form['title']
        author = request.form['author']
        id = request.form['id']

        if min_price != "":
            _where += "price > ?"
            _args = _args + tuple([float(min_price)])

        if max_price != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += "price < ?"
            _args = _args + tuple([float(max_price)])

        if title != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += " title LIKE ?"
            arg_str = "%" + title + "%"
            _args += tuple([arg_str])
        if author != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += " author LIKE ?"
            arg_str = "%" + author + "%"
            _args += tuple([arg_str])
        if id != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += " LID = ?"
            _args += tuple([int(id)])
        if _where != " WHERE ":
            _where += " AND "
        _where += " c.CID = l.cid "

    elif _type == 'r':
        _select += "r.*, c.author, c.title "
        _from += "reviews as r, comics as c "

        min_rating = request.form['min']
        max_rating = request.form['max']
        title = request.form['title']
        author = request.form['author']
        rid = request.form['id']

        if min_rating != "":
            _where += "r.rating >= ?"
            _args = _args + tuple([int(min_rating)])

        if max_rating != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += "r.rating <= ?"
            _args = _args + tuple([int(max_rating)])

        if title != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += " c.title LIKE ?"
            arg_str = "%" + title + "%"
            _args += tuple([arg_str])
        if author != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += " c.author LIKE ?"
            arg_str = "%" + author + "%"
            _args += tuple([arg_str])
        if rid != "":
            if _where != " WHERE ":
                _where += " AND "
            _where += " RID = ?"
            _args += tuple([int(rid)])
        if _where != " WHERE ":
            _where += " AND "
        _where += " c.CID = r.CID "

    # drop where clause if no filters given
    if _where is "WHERE ":
        _where = ""
    _where += " limit 1000"
    query = _select + _from + _where
    print(query)
    cur.execute(query, (_args))
    results = cur.fetchall()
    print(_args)
    return render_template('results.html', type=_type, results=results)


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

    return render_template('comic.html', row=row, listings=listings, reviews=reviews)


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
            cur.execute("INSERT INTO comics VALUES (?,?,?,?,?,?)",
                        (None, name, author, issueNumber, description, image))
        con.commit()
        con.close()
        return redirect(url_for("home"))
    except:
        return redirect(url_for("add_comic"))


@app.route('/submit_bulk', methods=['GET', 'POST'])
def submit_bulk_file():
    if request.method == 'POST':
        try:
            f = request.files['bulkFile']
            if f is None:
                return redirect(url_for("add_comic"))

        except:
            return redirect(url_for("add_comic"))
        # check if the post request has the file part
        # print(f.filename)

        if allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as f:
                        for line in f:
                            value_array = line.split(',')
                            name = value_array[0]
                            author = value_array[1]
                            issueNumber = value_array[2]
                            description = value_array[3]
                            image = value_array[4]

                            check = cur.execute("INSERT INTO comics VALUES (?,?,?,?,?,?)",
                                                (None, name, author, issueNumber, description, image))
                        # print(check)

                    f.close()
                con.commit()
                con.close()
                return redirect(url_for("home"))
            except:
                return redirect(url_for("add_comic"))
    return redirect(url_for("add_comic"))


@app.route('/search')
def advanced_search():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    listings = cur.execute(
        'SELECT l.price, l.date, c.title, u.name from listings as l, comics as c, users as u WHERE l.UID = u.UID AND c.CID = l.CID').fetchall()

    con.close()
    return render_template('advanced_search.html', listings=listings)


if __name__ == '__main__':
    app.run(debug=True)
