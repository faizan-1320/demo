from flask import Flask,g,jsonify
import mysql.connector
import os
from resturant.authentication import authentication_bp
from flask_mail import Mail
from datetime import timedelta
from flask_jwt_extended import JWTManager
from resturant.user import user_bp
# import socket
# socket.getaddrinfo('localhost', 8080)

app=Flask(__name__)

@app.before_request
def before_request():
    try:
        g.db=mysql.connector.connect(
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASSWORD'],
            host=os.environ['MYSQL_HOST'],
            database=os.environ['MYSQL_DB']
        )
    except:
        return jsonify({"Message":"Start Server"})

@app.after_request
def after_request(response):
    try:
        g.db.close()
        return response
    except:
        return jsonify({"Message":"Start Server"})


app.config['JWT_SECRET_KEY']=os.environ['JWT_SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES']=timedelta(days=1)
app.config['JWT_BLACKLIST_ENABLED']=True
app.config['JWT_BLACKLIST_TOKEN_CHECKS']=['access','refresh']

jwt = JWTManager(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'faizandiwan921@gmail.com'
app.config['MAIL_PASSWORD'] = 'dsxrvtuspfrhsjah'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

app.register_blueprint(authentication_bp)
app.register_blueprint(user_bp)