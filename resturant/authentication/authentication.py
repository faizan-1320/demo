from flask import Blueprint, request, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_jwt_extended import create_access_token
# from flask_mail import Mail
import math
import random
import threading
import time
import hashlib

# mail = Mail(app)

authentication_bp = Blueprint('auth', __name__)
email = ''
mobilenumber=''
pwd_hash=''
fullname=''
# committhread = None


@authentication_bp.post('/register')
def register():
    # try:
        digits = "0123456789"
        OTP = ""
        for i in range(4):
            OTP += digits[math.floor(random.random() * 10)]
        global a
        a = OTP
        global email, mobilenumber, user_type, pwd_hash, fullname
        data = request.json
        fullname = data.get('fullname')
        email = data.get('email')
        print(email)
        mobilenumber = data.get('number')
        password = data.get('password')
        if not fullname:
            return ({"Message": "Please Enter Fullname"})
        if not email:
            return ({"Message": "Please Enter Email"})
        if not mobilenumber:
            return ({"Message": "Please Enter Mobilenumber"})
        if not password:
            return ({"Message": "Please Enter Password"})
        cursor = g.db.cursor()
        cursor.execute("SELECT email FROM tbl_user WHERE email=%s", (email,))
        user_check = cursor.fetchone()
        print("this is email---------------------->", user_check)
        if user_check:
            return jsonify({'message': 'Account already exits'})
        cursor = g.db.cursor()
        cursor.execute('INSERT INTO tbl_otp(otp,email)VALUES(%s,%s)', (a, email))
        g.db.commit()
        pwd_hash = generate_password_hash(password, method='sha256', salt_length=8)

        from resturant import mail
        mail.send_message('Your OTP is ',
                        sender=email,
                        recipients=['faizandiwan921@gmail.com'],
                        body=a)
        return jsonify({"Message": "OTP send on mail"}), 200
        # else:
        #     return jsonify({'message': 'Account already exits'})
    # except:
    #     return jsonify({'message':'All Fields are required'}),400


@authentication_bp.post('/otp')
def verify():
    try:
        v_otp = request.json.get('otp')
        email_otp= request.json.get('email')
        cursor = g.db.cursor()
        print(email)
        print(v_otp)
        if not v_otp:
            return jsonify({"Message":"Please Enter Valid OTP"}),400
        if not email_otp:
            return jsonify({"Message":"Please Enter Valid Email"}),400
        cursor.execute(
            'SELECT email,otp FROM tbl_otp WHERE email=%s AND otp=%s', (email_otp, v_otp))
        otp_check = cursor.fetchone()
        # user=cursor.fetchone()
        print(otp_check[1])
        if v_otp == otp_check[1]:
            cursor.execute('INSERT INTO tbl_user(full_name,email,mobile_number,user_password)VALUES(%s, %s ,%s ,%s)',
                           (fullname, email, mobilenumber, pwd_hash))
            g.db.commit()
            return jsonify({'message': 'User registered successfully'}), 200
        else:
            return jsonify({"Message": "Enter Valid OTP"}), 400
    except:
        return jsonify({"Message": "Please Enter OTP"}), 400


@authentication_bp.post('/login')
def login():
    try:
        # import pdb
        # pdb.set_trace()
        # print("i am login")
        data = request.json
        email = data.get('email')
        phone_number = data.get('phone_number')
        if email=="" and phone_number=="":
            return ({"Message": "Please Enter Email or phonenumber"})
        else:
            print(email)
            password_user = data.get('password_user')
            if password_user == "":
                return ({"Message": "Please Enter Password"})
            else:
                print(password_user)
                # uesr_type='user'
                cursor = g.db.cursor()
                cursor.execute(
                    'SELECT * FROM tbl_user WHERE (email = %s OR mobile_number=%s)AND is_active=1 AND is_delete=0', (email, phone_number))
                user = cursor.fetchone()
                # import pdb;pdb.set_trace()
                if user:
                    is_pass_correct = check_password_hash(user[6], password_user)
                    if is_pass_correct:
                        access = create_access_token(identity=user[0])
                        return jsonify({'user': {'access': access, 'name': user[3]}}), 200
                    else:
                        return jsonify({'Message': 'Please enter correct password!'}), 400
                else:
                    return jsonify({'Message': 'Wrong Credentials!'}), 400
    except:
        return jsonify({"Message":"All Fields are required"}),400

@authentication_bp.post('/mail-forgot-password')
def mail_forgot_password():
    try:
        data = request.json
        email_s = data.get('email')
        if not email:
            return jsonify({"message": "Please Enter Email"})
        else:
            cursor = g.db.cursor(dictionary=True)
            cursor.execute('SELECT * FROM tbl_user WHERE email=%s', (email_s,))
            user = cursor.fetchone()
            encdoe_email = generate_password_hash(
                email_s, method='sha256', salt_length=8)
            if user:
                from resturant import mail
                mail.send_message('Change password Link',
                                  sender=email_s,
                                  recipients=["faizandiwan921@gmail.com"],
                                  body=f'http://127.0.0.1:8080/forgot-password/{email_s}')
                mail.send
                return jsonify({"Message": "Mail send"}), 200
            return jsonify({"Message": "Enter Valid Mail"}), 400
    except:
        return jsonify({"Message": "Email is required"})


@authentication_bp.patch('/forgot-password/<email_s>')
def forgot_password(email_s):
    try:
        new_password = request.json.get('new_pass')
        cursor = g.db.cursor()
        # import pdb;pdb.set_trace()
        cursor.execute('SELECT * FROM tbl_user WHERE email=%s', (email_s,))
        passw = cursor.fetchone()
        # print(passw[2])
        # is_mail_corrcet=check_password_hash(email_s,passw[2])
        # if is_mail_corrcet:
        # is_pass_correct=check_password_hash(new_password,passw[6])
        if new_password == "":
            return ({"Message": "Please Enter Password"})
        else:
            hash_pwd = generate_password_hash(
                new_password, method='sha256', salt_length=8)
            cursor.execute(
                'UPDATE tbl_user SET user_password=%s WHERE id=%s', (hash_pwd, passw[0]))
            g.db.commit()
            return jsonify({"Message": "Successfully Update passsword"})
            # else:
            #     return jsonify({"message":"Enter Valid Email"})
    except:
        return ({"Message": "Password is required"})
