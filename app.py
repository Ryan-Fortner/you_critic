from flask import Flask, render_template, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt 
from datetime import datetime, timedelta 
import re
 
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_dash.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "FriedRice"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
db=SQLAlchemy(app)
migrate=Migrate(app, db)

class User(db.Model):	
    __tablename__ = "users"    # optional		
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(45), unique=True)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


    def __repr__(self):
        return f"<User: {self.email}>"

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.Text)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref="reviews")
    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def num_likes(self):
        # likes_rec [User1, User2]
        return len(self.likes_rec)

    def __repr__(self):
        return f"<review: \"{self.content[:5]}...\">"


@app.route("/")
def main():
    return render_template("index.html")

@app.route("/login_register")
def login_register():
    return render_template("login_register.html")

@app.route("/movie_search")
def movie_search():
    return render_template("movie.html")

@app.route("/search_results")
def search_results():
    return render_template("/search_results.html")

@app.route("/users/create", methods=["POST"])
def register():
    errors = []

    if len(request.form['first_name']) < 3:
        errors.append("First name must be at least 3 characters")
        valid = False

    if len(request.form['last_name']) < 3:
        errors.append("Last name must be at least 3 characters")
        valid = False

    if not EMAIL_REGEX.match(request.form['email']):
        errors.append("Email must be valid")
        valid = False

    if len(request.form['password']) < 8:
        errors.append("Password must be at least 8 characters")
        valid = False

    #TODO: Validate email is unique
    user_check = User.query.filter_by(email=request.form["email"]).first()
    if user_check is not None:
        errors.append("Email is in use")
    
    if request.form['password'] != request.form['confirm']:
        errors.append("Passwords must match")
        valid = False

    if errors:
        for e in errors:
            flash(e)
    else:
        hashed = bcrypt.generate_password_hash(request.form["password"])
        new_user = None
        #TODO: Create New User
        new_user = User(
            first_name = request.form["first_name"],
            last_name = request.form["last_name"],
            email = request.form["email"],
            password = hashed
        )
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.id
        return redirect("/")

    return redirect("/")

@app.route("/users/login", methods=["POST"])
def login():
    errors = []

    user_attempt = User.query.filter_by(email=request.form["email"]).first()
    #TODO: Query for user wiith provided email
    
    if not user_attempt:
        flash("Email/Password Incorrect")
        return redirect("/")

    if not bcrypt.check_password_hash(user_attempt.password, request.form["password"]):
        flash("Email/Password Incorrect")
        return redirect("/")

    session["user_id"] = user_attempt.id
    return redirect("/reviews")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/reviews")
def reviews():
    if not "user_id" in session:
        return redirect("/")
    logged_in = User.query.get(session["user_id"])
    all_reviews = Review.query.all()
    return render_template("reviews.html", user=logged_in, reviews=all_reviews)

@app.route("/new")
def new():
    if not "user_id" in session:
        return redirect("/")
    
    logged_in = User.query.get(session["user_id"])
    return render_template("new.html", user=logged_in)


@app.route("/review/create", methods=["POST"])
def new_review():
    if not "user_id" in session:
        return redirect("/")
    errors = []

    if len(request.form['item']) < 3:
        errors.append("Item must be at least 3 characters")
        valid = False

    if len(request.form['content']) < 3:
        errors.append("Review must be at least 3 characters")
        valid = False
    if errors:
        for e in errors:
            flash(e)

    new_review = Review(content=request.form["content"], user_id=session["user_id"], item=request.form["item"])
    db.session.add(new_review)
    db.session.commit()
    logged_in = User.query.get(session["user_id"])
    return redirect("/reviews")

@app.route("/reviews/<review_id>/edit")
def edit(review_id):
    if not "user_id" in session:
        return redirect("/")
    logged_in = User.query.get(session["user_id"])
    review = Review.query.get(review_id)
    return render_template("edit.html", user=logged_in, review=review)

@app.route("/reviews/<review_id>/update", methods=["POST"])
def edit_review(review_id):
    if not "user_id" in session:
        return redirect("/")
    logged_in = User.query.get(session["user_id"])
    review = Review.query.get(review_id)
    review.item = request.form["item"]
    review.content = request.form["content"]
    db.session.commit()
    return redirect("/reviews")



@app.route("/reviews/<review_id>/remove")
def delete_review(review_id):
    if not "user_id" in session:
        return redirect("/")
    review= Review.query.get(review_id)
    db.session.delete(review)
    db.session.commit()
    return redirect("/reviews")

def remove_review(review_id):
    if not "user_id" in session:
        return redirect("/")
    review= Review.query.get(review_id)
    db.session.delete(review)
    db.session.commit()
    return redirect("/reviews")

if __name__ == "__main__":
    app.run(debug=True)