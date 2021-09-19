# render_template handles the html files in the template directory so not directly in script
# url_for takes care of static files like css
# flash will help with displaying text in html
# redirect: to switch route
# request: to access query parameters
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

# dummy data
posts = [
    {
        "author": "Corey Schafer",
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": "April 20, 2018",
    },
    {
        "author": "Jane Doe",
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": "April 21, 2018",
    },
]

# route: navigating trough different site on the website
# the slash(/) is the root of the website
# stacking decorators possible
@app.route("/")
@app.route("/home")
def home():
    # instead of typing here all html
    # can use any argument e.g. posts and this parameter will be a variable
    # in the html file
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


# 2nd argument methods: allows which request this route can handle
@app.route("/register", methods=["GET", "POST"])
def register():
    # if user is logged in there is no need to go to register, so redirect to home
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    # check if submit was entered
    if form.validate_on_submit():
        # decode at the end to get a hashed-string
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )

        # add user to the database & commit it
        db.session.add(user)
        db.session.commit()

        # flash: easy way to display a message
        # 2nd argument is for Bootstrap classes what kind of message it should be
        flash("Your account has been created! You are now able to log in", "success")
        # redirect to different route. url_for takes as a argument the name of the function
        # for this route. Not the name of the route!
        return redirect(url_for("login"))
    # 3rd argument pass form
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if user entered in url account but was not logged and then logs in
            # this will make to get the query parameter which to go next, here account and
            # not redirect to home
            # Note: args is a dictionary but access with brackets is not good due to if
            # key does not exist it will throw an error. But with get it will return None
            next_page = request.args.get("next")
            # next_page includes the route for the next page, so can pass it like this
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account")
# with this decorator only if logged in this route can be accessed
@login_required
def account():
    return render_template("account.html", title="Account")
