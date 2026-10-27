from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)

# create database
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books-collection.db'

# create the extension
db = SQLAlchemy(model_class=Base)
# initialize the app with the extension
db.init_app(app)

class Books(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

with app.app_context():
    db.create_all()


@app.route('/')
def home():

    with app.app_context():
        book_count = db.session.execute(db.select(Books).group_by(Books.id)).scalar()
        print(book_count)
    if book_count == None:
        return render_template('index.html', library=None)
        # read all records
    with app.app_context():
        all_records = db.session.execute(db.select(Books).order_by(Books.title))
        all_books = all_records.scalars()
        # first_book = next(all_books, None)
        # print(first_book)
        # for book in all_books:
        #     print(book.id, book.title, book.author, book.rating)
        return render_template('index.html',library=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        book_title = request.form.get('book_title')
        author = request.form.get('author')
        rating = request.form.get('rating')
        with app.app_context():
            new_book = Books(title=book_title, author=author, rating=rating)
            db.session.add(new_book)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html')

@app.route("/edit_rating", methods=['GET', 'POST'])
def edit_rating():
    if request.method == 'POST':
        new_book_rating = request.form.get('rating')
        id = request.form.get('id')
        with app.app_context():
            book_to_update = db.session.execute(db.select(Books).where(Books.id == id)).scalar()
            book_to_update.rating = new_book_rating
            db.session.commit()
        return redirect(url_for('home'))
    else:
        id = request.args.get('id')
        with app.app_context():
            book = db.session.execute(db.select(Books).where(Books.id == id)).scalar()
        return render_template('edit_rating.html', book=book)

@app.route("/delete")
def delete():
    id = request.args.get('id')
    with app.app_context():
        book_to_delete = db.session.execute(db.select(Books).where(Books.id == id)).scalar()
        db.session.delete(book_to_delete)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

