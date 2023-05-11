from flask import Flask, render_template, request,jsonify,redirect,session
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import mysql.connector
import os
import pymongo



app = Flask(__name__)
CORS(app)

app.secret_key=os.urandom(24)

mydb = mysql.connector.connect(host="localhost",user="root",password="93283Kish@n",database="user_db")
my_cursor = mydb.cursor()



@app.route("/")
def login():
    if 'user_id' in session:
        return redirect('/home')
    else:
        return render_template('login.html')
    
@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/home")
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

@app.route("/analysis")
def analysis():
    if 'user_id' in session:
        return render_template('index.html')
    else:
        return redirect('/')
    
@app.route("/images")
def images():
    if 'user_id' in session:
        return render_template('images.html')
    else:
        return redirect('/')

@app.route("/login_validation",methods=['POST'])
def login_validation():
    global email
    email = request.form.get('email')
    password = request.form.get('password')

    my_cursor.execute("""select * from `user` where `email` like '{}' and `password` like '{}'""".format(email,password))
    user = my_cursor.fetchall()
    if len(user)>0:
        session['user_id']=user[0][0]
        return redirect('/home')
    else:
        return redirect('/signup') 
    
@app.route("/add_user",methods=['POST'])
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    
    my_cursor.execute("""select * from `user` where `email` like '{}' and `password` like '{}'""".format(email,password))
    user = my_cursor.fetchall()
    if len(user)>0:
        return redirect('/')
    else:
        my_cursor.execute("""insert into `user` (`user_id`,`username`,`email`,`password`) values (NULL,'{}','{}','{}')""".format(name,email,password))
        mydb.commit()
        return redirect('/')

#@app.route("/", methods = ['GET'])
#def homepage():
#    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
                #fw.write(mydict)
            logging.info("log my final result {}".format(reviews))
            
            my_cursor.execute("""insert into `review_history` (`email_id`,`Product_name`,`reviewer_name`) values ('{}','{}','{}')""".format(email,searchString,name))
            mydb.commit()
         
            #client = pymongo.MongoClient("mongodb+srv://kishan42:kishan42@review.hzf2bua.mongodb.net/test")
            #db = client['Review_scrap']
            #review_col = db['review_scrap_data']
            #data = [{"mail_id": email,
            #         "Product_name" : searchString,
            #         'Reviewer_name' : name}]
            
            #review_col.insert_many(data) 
            #review_col.insert_many(reviews) 
            
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return redirect('index.html')
    

@app.route("/imagereview" , methods = ['POST' , 'GET'])
def imagereview():
    if request.method == 'POST':
        try:
            save_dir = "images/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            query = request.form['content'].replace(" ","")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")
            soup = bs(response.content)
            images_tags = soup.find_all("img")
            del images_tags[0]
            img_data_mongo = []
            for i in images_tags:
                image_url = i['src']
                image_data = requests.get(image_url).content
                mydict = {"index":image_url,"image":image_data}
                img_data_mongo.append(mydict)
                with open(os.path.join(save_dir,f"{query}_{images_tags.index(i)}.jpg"),"wb") as f:
                    f.write(image_data)
            
            return render_template('images.html')
        
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')
    else:
        return redirect('images.html')
    

if __name__=="__main__":
    app.run(debug=True)
