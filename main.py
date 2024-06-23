from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from timed_token import generate_confirmation_token, confirm_token
from itsdangerous import SignatureExpired
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.urandom(12)       # Randomly generates secret key
# Changes directory of where data.db is stored and used from
# app.root_path is absolute path to current python app directory
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/instance/email.db"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587   # 465 for SMTP, 587 for TLS
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = "SENDER_EMAIL_ADDRESS"          # Sender email address
app.config["MAIL_PASSWORD"] = os.getenv("PASSWORD")         # Sender email password
app.config["MAIL_USE_TLS"] = True

db = SQLAlchemy(app)

mail = Mail(app)

class Form(db.Model):
    """Creates columns and their datatypes inside email.db"""
    __tablename__ = "emails"
    id_num = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))

    def __init__(self, email):
        self.email = email


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route('/verify', methods=["POST"])  
def verify():  
    """Sends email with verify link"""
    global rec_email 
    rec_email = request.form["email"]

    user_token = generate_confirmation_token(rec_email)     # Creates token associated with email
    
    link = url_for('validate', token=user_token, _external=True)

    # Sends email with verification link
    message_body = "Thank you for subscribing to our mailing list!"\
                    " Click this link to verify your email: {}".format(link)
    message = Message("Please Confirm your email!",
                    sender=app.config["MAIL_USERNAME"], 
                    recipients=[rec_email],
                    body=message_body)
    
    mail.send(message)

    return render_template('verify.html')  


@app.route('/validate/<token>')
def validate(token):
    """Checks if token from user link is still valid"""
    try:
        session_token = confirm_token(token)    # Token check, if confirm_token returns False, go to except block
        
        email = rec_email                       # Gets email from global variable rec_email

        form = Form( 
            email=email, 
        )

        db.session.add(form)
        db.session.commit()

    # Error is raised when token is expired
    except SignatureExpired:
        return render_template("error.html")
    
    return render_template("success.html") 
    
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # app.run(debug=True, port=5001)        # Runs on local 127.0.0.1 network
        app.run(host="0.0.0.0")         # Opens webpage to entire network (Uses host IPv4 address)