from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from flask_login import LoginManager,UserMixin,login_required, login_user, current_user
from wtforms import SubmitField,SelectField,IntegerField,StringField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager(app)

class Login(FlaskForm):
    password = PasswordField("enter password")
    submit = SubmitField("submit")

class Superuser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Integer, nullable=False)


class Cafes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    power = db.Column(db.Integer,db.CheckConstraint("0 <= power <= 5"),nullable=False)
    coffee_rating = db.Column(db.Integer,db.CheckConstraint("0 <= coffee_rating <= 5"), nullable=False)
    location = db.Column(db.String(100),nullable=False)
    wifi = db.Column(db.Integer,db.CheckConstraint("0 <= wifi <= 5"),nullable=False)

class Add(FlaskForm):
    name = StringField("cafe name", validators=[DataRequired()])
    map_url = StringField("map-url",validators=[DataRequired()])
    img_url = StringField("img-url",validators=[DataRequired()])
    power = SelectField("power rating", choices=[0,1,2,3,4,5])
    coffee_rating = SelectField("coffee rating", choices=[0,1,2,3,4,5],validators=[DataRequired()])
    wifi = SelectField("wifi", choices=[0,1,2,3,4,5],validators=[DataRequired()])
    location = StringField("location",validators=[DataRequired()])
    add = SubmitField()

# with app.app_context():
#     db.create_all()





class City_form(FlaskForm):
    city = SelectField("select city", choices=["london","lagos","helsinki","abuja","los angeles","seattle","california","manchester","NYC"],validators= [DataRequired(message="please select your city")])
    submit = SubmitField("show me")



@app.before_request
def before_request():
    db.session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        user = db.session.query(Superuser).get(user_id)
        return user

@app.route("/", methods=["GET","POST"])
def home():
    city_form = City_form()
    if city_form.validate_on_submit():
        city = city_form.city.data
        nested_selected_city = []
        with app.app_context():
            selected_city = db.session.query(Cafes).filter_by(location=city).all()
            
           
            for n in range(0,len(selected_city) + 1,4):
                nested_selected_city.append(selected_city[n-4:n])
        return render_template("index.html",city_cafes=selected_city,selected=True,city_form=city_form)
    return render_template("index.html", city_form=city_form, selected=False)


@app.route("/login", methods=["POST","GET"])
def login():
    login_form = Login()
    if login_form.validate_on_submit():
        with app.app_context():
            admin = db.session.query(Superuser).get(1)
        if check_password_hash(admin.password,login_form.password.data):
            login_user(admin)
            return redirect(url_for('add'))
    return render_template("login.html",login_form=login_form)
    


@app.route("/add", methods=["POST","GET"])
def add():
    add_form = Add()
    print(add_form.validate_on_submit())
    if add_form.validate_on_submit():
        if current_user.is_authorized:
            new_cafe= Cafes(name=add_form.name.data, 
                            map_url=add_form.map_url.data,
                            img_url=add_form.img_url.data,
                            power=add_form.power.data,
                            coffee_rating=add_form.coffee_rating.data,
                            wifi=add_form.coffee_rating.data,
                            location=add_form.location.data)
            with app.app_context():
                db.session.add(new_cafe)
                db.session.commit()
            return "added successfully"
        else:
            return "unauthorized"
    if current_user.is_authenticated:
        return render_template("add.html", form=add_form)
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
    