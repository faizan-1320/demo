from flask import Blueprint,request,g,jsonify,json
from flask_jwt_extended import jwt_required,get_jwt_identity

user_bp=Blueprint('user',__name__)

@user_bp.post('/address')
@jwt_required()
def add_address():
    try:
        user_id=get_jwt_identity()
        data=request.json
        address=data.get('address')
        address_type=data.get('address_type')
        latitude=data.get('latitude')
        longitude=data.get('longitude')
        if not address:
            return jsonify({"Message":"Please Enter Address"})
        if not address_type:
            return jsonify({"Message":"Please Enter Add-Address"})
        if not latitude:
            return jsonify({"Message":"Please Enter Latitude"})
        if not longitude:
            return jsonify({"Message":"Please Enter Longitude"})
        cursor=g.db.cursor()
        # print(type(address_type))
        # cursor.execute('SELECT address_type FROM tbl_address')
        if address_type in ['home','work','other']:
            cursor.execute('INSERT INTO tbl_address(user_id,address,address_type,latitude,longitude)VALUES(%s,%s,%s,%s,%s)',(user_id,address,address_type,latitude,longitude))
            g.db.commit()
            return jsonify({"Message":"Address add successfully"})
        else:
            return jsonify({"message":"Enter valid address type"})
    except:
        return jsonify({"Message":"All fields are requireds"})

@user_bp.post('/add-review/<resturant_id>')
@jwt_required()
def add_review(resturant_id):
    try:
        user_id=get_jwt_identity()
        data=request.json
        review=data.get('review')
        if not review:
            return jsonify({"Message":"Please enter review"})
        cursor=g.db.cursor()
        cursor.execute(f'SELECT review,user_id,restaurant_id FROM tbl_restaurants_rating WHERE user_id={user_id} AND restaurant_id={resturant_id}')
        user=cursor.fetchone()
        # print(user)
        if user is None:
            cursor.execute('INSERT INTO tbl_restaurants_rating(restaurant_id,user_id,review)VALUES(%s,%s,%s)',(resturant_id,user_id,review))
            g.db.commit()
            return jsonify({"Message":"Review add successfully"})
        if user_id==user[1] and user[0] is None:
            print("i mai update")
            cursor.execute('UPDATE tbl_restaurants_rating SET review=%s WHERE user_id=%s and restaurant_id=%s',(review,user_id,resturant_id))
            g.db.commit()
            return jsonify({"Message":"Review Updated successfully"})
        return jsonify({"erroe":"Already give review"})
    except:
        return jsonify({"Message":"Review is required"})

@user_bp.post('/add-rating/<resturant_id>')
@jwt_required()
def add_rating(resturant_id):
    try:
        # import pdb;pdb.set_trace()
        user_id=get_jwt_identity()
        data=request.json
        rating=data.get('rating')
        if not rating:
            return jsonify({"Message":"Please enter rating"})
        cursor=g.db.cursor()
        # cursor.execute(f'SELECT user_id FROM tbl_restaurants_rating WHERE user_id={user_id}')
        # user_one=cursor.fetchone()
        
        cursor.execute(f'SELECT rating,user_id,restaurant_id FROM tbl_restaurants_rating WHERE user_id={user_id} AND restaurant_id={resturant_id}')
        user=cursor.fetchone()
        print(user)
        if user is None:
            cursor.execute('INSERT INTO tbl_restaurants_rating(restaurant_id,user_id,rating)VALUES(%s,%s,%s)',(resturant_id,user_id,rating))
            g.db.commit()
            return jsonify({"Message":"Rating add successfully"})
        if user_id==user[1] and user[0] is None:
            cursor.execute(f'UPDATE tbl_restaurants_rating SET rating={rating} WHERE user_id={user_id} and restaurant_id={resturant_id}')
            g.db.commit()
            return jsonify({"Message":"Rating Updated add successfully"})
    
        return jsonify({"erroe":"Already give rating"})
    except:
        return jsonify({"Message":"Rating is required"})
@user_bp.get('/address-diaplay')
@jwt_required()
def display_address():
    user_id=get_jwt_identity()
    cursor=g.db.cursor(buffered=True)
    cursor.execute(f'SELECT address,address_type,latitude,longitude FROM tbl_address WHERE user_id={user_id}')
    user=cursor.fetchall()
    print(user)
    if user:
        # data_address=cursor.fetchone()
        address_data=[]
        for i in user:
            data_a={"Address":i[0],
                    "Address Type":i[1],
                    "Latitude":i[2],
                    "Longitude":i[3]}
            address_data.append(data_a)
        return jsonify(address_data)
    else:
        return jsonify({"Message":"Please add address"})

@user_bp.get('/home/<type_address>')
@jwt_required()
def home(type_address):
    user_id=get_jwt_identity()
    cursor=g.db.cursor(buffered=True)
    cursor.execute(f'SELECT id FROM tbl_user WHERE id={user_id}')
    user=cursor.fetchone()
    # print(user)
    if user:
        # print(type_address)
        # try:
            # cursor=g.db.cursor(dictionary=True)
            cursor.execute('SELECT address_type,address,latitude,longitude FROM tbl_address WHERE user_id=%s AND address_type=%s',(user_id,type_address))
            data_address=cursor.fetchone()
            # address_data=[]
            # for i in data_address:
            data_a={"Address":data_address[0],
                    "Address Type":data_address[1],
                    "Latitude":data_address[2],
                    "Longitude":data_address[3]}
            # address_data.append(data_a)
            if type_address in ['home','work','other']:
                cursor.execute('SELECT image FROM tbl_advertisement WHERE is_active = 1')
                advertisement=cursor.fetchall()
                advertisement_data=[]
                for i in advertisement:
                    data={"Image":i[0]}
                    advertisement_data.append(data)
                # print(data_address['latitude'])
                cursor.execute('''SELECT image,r_name,total_rating,payment,round((6371 * acos (cos (radians(%s))* cos(radians(latitude)) *cos( radians(%s) - radians(longitude) )+ sin (radians(%s) ) *sin(radians(latitude))))) AS distance  FROM tbl_restaurants WHERE is_active = 1 HAVING distance < 4''',(data_address[2],data_address[3],data_address[2]))
                resturant=cursor.fetchall()
                resturant_data=[]
                # print(resturant)
                for i in resturant:
                    data_r={"Image":i[0],
                            "Resturant Name":i[1],
                            "Rating":i[2],
                            "Payment":i[3],
                            "Distance":i[4]}
                    resturant_data.append(data_r)
                cursor.execute('SELECT name,image,price FROM tbl_product ORDER BY total_like DESC')
                product=cursor.fetchall()
                product_data=[]
                for i in product:
                    data_product={"Image":i[1],"Name":i[0],"Price":i[2]}
                    product_data.append(data_product)
                cursor.execute('SELECT image,r_name,total_rating FROM tbl_restaurants ORDER BY total_rating DESC')
                top_rated=cursor.fetchall()
                top_rated_data=[]
                for i in top_rated:
                    data_top_rated={"Image":i[0],"Restuarant_Name":i[1],"Rating":i[2]}
                    top_rated_data.append(data_top_rated)
                
                # return jsonify({"Address_type":data_address['address_type'],"Address":data_address['address']},response_data,{"Resturant Nearby":resturant},{"Top Picks":product},{"Top Rated Resturant":top_pick}),200
                return jsonify({"Address":data_a,"advertisement":advertisement_data,"Restaurants Neraby":resturant_data,"Top Picks":product_data,"Top Rated Restaurants":top_rated_data}),200
            else:
                return({"message":"Please enter address type is home or work or other"})
        # except:
        #     return({"message":"enter address type is not add in adress"})
    else:
        return({"message":"wrong credital"})

@user_bp.get('/resturant-detail/<resturant_id>')
@jwt_required()
def resturant_detail(resturant_id):
    cursor=g.db.cursor(dictionary=True)
    cursor.execute(f'SELECT r_name,image,total_rating,total_review,strt_time,end_time,(SELECT AVG(price) FROM tbl_product WHERE restaurant_id={resturant_id}) AS price FROM tbl_restaurants WHERE id={resturant_id}')
    one_resturant_detail=cursor.fetchone()
    # print(one_resturant_detail)
    # return jsonify(one_resturant_detail, default=str)
    # resturant_data=[]
    # for i in one_resturant_detail:
    #     data_restaurant={"Image":i[1],"Restuarant_Name":i[0],"Rating":i[2],"Review":i[3],"Start Time":i[4],"End Time":i[5],"Price":i[6]}
    #     resturant_data.append(data_restaurant)
    return json.dumps(one_resturant_detail, indent=4, sort_keys=True, default=str)

@user_bp.get('/about/<resturant_id>')
@jwt_required()
def display_about(resturant_id):
    cursor=g.db.cursor(dictionary=True)
    cursor.execute(f'SELECT about FROM tbl_restaurants WHERE id={resturant_id}')
    about_resturant=cursor.fetchone()
    return jsonify(about_resturant)
    
@user_bp.get('/menu/<resturant_id>')
@jwt_required()
def display_menu(resturant_id):
    cursor=g.db.cursor(dictionary=True)
    cursor.execute(f'SELECT name,image,price,total_like FROM tbl_product WHERE restaurant_id={resturant_id}')
    menu_resturant=cursor.fetchall()
    return jsonify(menu_resturant)

@user_bp.get('/reviwes/<resturant_id>')
@jwt_required()
def display_reviews(resturant_id):
    cursor=g.db.cursor(dictionary=True)
    cursor.execute(f'SELECT review,rating FROM tbl_restaurants_rating WHERE review IS NOT NULL AND restaurant_id={resturant_id}')
    review_resturant=cursor.fetchall()
    return jsonify(review_resturant)