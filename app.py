from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    Response,
)
import sqlite3
import csv
import json
from io import BytesIO, TextIOWrapper
import io
import os

app = Flask(__name__)


# Home page
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


# Book Search
@app.route("/search_books", methods=["GET", "POST"])
def search_books():
    result = None
    if request.method == "POST":
        # Get the search parameters
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        date = request.form.get("date")
        isbn = request.form.get("isbn")

        # Connect to the database
        con = sqlite3.connect("books.db")
        cur = con.cursor()

        # Search the database
        cur.execute(
            """SELECT * FROM Inventory
                       WHERE "Title" LIKE ? OR "Author" LIKE ? OR "Genre" LIKE ? OR "Publication Date" LIKE ? OR "ISBN" = ?""",
            (title, author, genre, date, isbn),
        )
        result = cur.fetchall()
        con.close()

    return render_template("search_books.html", result=result)


# Adding book
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        # Get the book data
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        date = request.form.get("date")
        isbn = request.form.get("isbn")

        # Connect to the database
        con = sqlite3.connect("books.db")
        cur = con.cursor()

        # Insert the book into the database
        cur.execute(
            """INSERT INTO Inventory ("Title", "Author", "Genre", "Publication Date", "ISBN")
                       VALUES (?, ?, ?, ?, ?)""",
            (title, author, genre, date, isbn),
        )
        con.commit()
        con.close()

        return redirect(url_for("list_books"))

    return render_template("add_book.html")


# Listing Books
@app.route("/list_books")
def list_books():
    # Connect to the database
    con = sqlite3.connect("books.db")
    cur = con.cursor()

    # Get all the books
    cur.execute("SELECT * FROM Inventory")
    result = cur.fetchall()
    con.close()

    return render_template("list_books.html", result=result)


# Exporting data
@app.route("/export_data", methods=["GET", "POST"])
def export_data():
    if request.method == "POST":
        format_type = request.form.get("format")

        # Connect to the database
        con = sqlite3.connect("books.db")
        cur = con.cursor()

        # Get all the books
        cur.execute("SELECT * FROM Inventory")
        rows = cur.fetchall()
        con.close()

        # Export the data as CSV
        if format_type == "csv":
            # Write the data to a CSV file
            output = io.StringIO()
            csv_writer = csv.writer(output)
            columns = [description[0] for description in cur.description]
            csv_writer.writerow(columns)
            csv_writer.writerows(rows)
            output.seek(0)

            # Return the file
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment;filename=books.csv"},
            )

        # Export the data as JSON
        elif format_type == "json":
            # Write the data to a JSON file
            books_list = []
            for row in rows:
                books_list.append(
                    {
                        "Title": row[1],
                        "Author": row[2],
                        "Genre": row[3],
                        "Publication Date": row[4],
                        "ISBN": row[5],
                    }
                )

            # Return the file
            json_output = json.dumps(books_list, indent=4).encode("utf-8")
            return send_file(
                BytesIO(json_output),
                as_attachment=True,
                mimetype="application/json",
                download_name="books.json",
            )

    return render_template("export_data.html")


if __name__ == "__main__":
    app.run(debug=True)
