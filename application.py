# Importing Dependencies
import os
import requests

from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.utils import secure_filename
from uuid import uuid1
import boto3, botocore
from botocore.client import Config
import pytz
from datetime import datetime


UPLOAD_FOLDER = 'media/repos/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Setting up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "Attack0nT1tanSeas0n4!"

# Setting up AWS
S3_KEY = os.getenv("S3_KEY")
S3_SECRET = os.getenv("S3_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

s3 = boto3.client(
   "s3",
   aws_access_key_id= S3_KEY,
   aws_secret_access_key= S3_SECRET,
   config = Config(signature_version="s3v4")
)

#main page
# asks user to login if not already
@app.route('/')
def welcome_page():
    if "user" in session:
        return redirect(url_for("login"))
    return render_template("welcome.html")

# login function and also registers users
@app.route("/homepage", methods=["POST", "GET"])
def login():
    fimg = db.execute("SELECT * FROM Images ORDER BY RANDOM() LIMIT 1").fetchone()
    fimg_tags = fimg.tags.split(',')
    lis = []
    lis.append(fimg)
    lis.append(fimg_tags)
    if "user" not in session:
        if request.method=="POST":
            if request.form['action']=='Lgn':
                username = request.form.get("uname")
                password = request.form.get("pswd")
                
                u = db.execute("SELECT * FROM Users WHERE username = :username" , {"username": username}).fetchone()
                
                if (username or password) is None:
                    flash('Login or Password is empty')
                    return redirect(request.url)

                if u is None or (u.password)!=password:
                    flash('Invalid Credentials')
                    return redirect(request.url)

                session["user"] = username

            if request.form['action']=='CreateAcc':
                username = request.form.get("uname")
                usernameNew = request.form.get("unameNew")
                passwordNew = request.form.get("pswdNew")
                passwordNewRe = request.form.get("pswdNewRe")

                if (usernameNew.isspace() or passwordNew.isspace() or passwordNewRe.isspace()):
                    flash('One of the fields is empty')
                    return redirect(request.url)
                
                if len(usernameNew)>16:
                    flash('Username should be shorter than 17 characters')
                    return redirect(request.url)

                usernameFind = db.execute("SELECT * FROM Users WHERE username = :usernameNew" , {"usernameNew": usernameNew}).fetchone()
                if usernameFind is not None:
                    flash('Username Already Exists')
                    return render_template("error.html", message="Username Already Exists")

                if passwordNew!=passwordNewRe:
                    flash("Passwords don't match")
                    return render_template("error.html", message="Passwords don't match")

                if ' ' in passwordNew or ' ' in usernameNew:
                    flash("Space in one of the Parameters")
                    return redirect(request.url)

                timeStamp = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                db.execute("INSERT INTO Users (username, password) VALUES  (:usernameNew, :passwordNew)",
                    {"usernameNew": usernameNew, "passwordNew": passwordNew})
                db.commit()
                session["user"] = usernameNew
            return render_template("homepage.html", fimg=lis)
        else:
            return redirect("/")
    else:
        return render_template("homepage.html", fimg=lis)
        

# log out
@app.route("/logout", methods=["POST","GET"])
def logout():
    session.pop("user", None)
    return redirect("/")

# user profile page displays some information about an account
@app.route("/user_profile/<user_name>", methods=["GET"])
def user_profile(user_name):
    if "user" not in session:
        return redirect("/")
    
    user =  db.execute("SELECT * FROM Users WHERE username = :username" , {"username": user_name}).fetchone()
    u1 = db.execute("SELECT * FROM Users WHERE username = :username" , {"username": session["user"]}).fetchone()
    u2 = db.execute("SELECT * FROM Users WHERE username = :username" , {"username": user_name}).fetchone()
    if user is None:
        return render_template("error.html",message="User Not Found")
    rel_exists = db.execute("SELECT * FROM Relations WHERE follower_id = :follower_id AND following_id = :following_id", {"follower_id": u1[0], "following_id": u2[0]}).fetchone()
    if rel_exists:
        ru = "Unfollow"
    else:
        ru = "Follow"
    fimg = db.execute("SELECT * FROM Images WHERE username= :username ORDER BY RANDOM() LIMIT 1",  {"username": user_name}).fetchone()
    fimg_tags = ""
    if fimg:
        fimg_tags = fimg.tags.split(',')
    lis = []
    lis.append(fimg)
    lis.append(fimg_tags)
    return render_template("user_profile.html",user=user,ru_txt=ru, fimg=lis)

def get_user_id(user_name):
    user =  db.execute("SELECT * FROM Users WHERE username = :username" , {"username": user_name}).fetchone()
    user_id = user.userid
    return user_id

# follows or unfollows depending on the previou selection
@app.route("/relationship_update/<user_name>", methods=["GET"])
def relationship_update(user_name):
    u1 = get_user_id(session['user'])
    u2 = get_user_id(user_name)
    rel_exists = db.execute("SELECT * FROM Relations WHERE follower_id = :follower_id AND following_id = :following_id", {"follower_id": u1, "following_id": u2}).fetchone()
    if rel_exists:
        rel_update = db.execute("DELETE FROM Relations WHERE (follower_id = :follower_id AND following_id = :following_id)", {"follower_id": u1, "following_id": u2})
        db.commit()
    else:
        if u1 and u2:
            quer = "INSERT INTO Relations (follower_id, following_id) VALUES("+str(u1) +","+ str(u2) +")"
            rel_update = db.execute(quer)
            db.commit()
    return redirect("/user_profile/"+user_name)


# user feed page, returns a curated list of images a user might find useful
# sorts based on who the user is following
@app.route("/feed", methods=["POST","GET"])
def user_feed():
    if "user" not in session:
        return redirect("/")
    
    fimg_lis = db.execute("SELECT * FROM Images WHERE userid = ANY (SELECT following_id FROM Relations WHERE follower_id = :user_id) ORDER BY date DESC", {"user_id" : get_user_id(session['user'])}).fetchall()
    fimg_tags_lis =[]
    lis = []

    c = 0
    for i in fimg_lis:
        spli = i.tags.split(',')
        fimg_tags_lis.append(spli)
        x = []
        x.append(fimg_lis[c])
        x.append(spli)
        c+=1
        lis.append(x)

    return render_template("feed.html", feed = lis)

 # similar to user feed but more generic - not sorted
@app.route("/discover", methods=["POST","GET"])
def discover():
    if "user" not in session:
        return redirect("/")

    fimg_lis = db.execute("SELECT * FROM Images ORDER BY date DESC").fetchall()
    fimg_tags_lis =[]
    lis = []

    c = 0
    for i in fimg_lis:
        spli = i.tags.split(',')
        fimg_tags_lis.append(spli)
        x = []
        x.append(fimg_lis[c])
        x.append(spli)
        c+=1
        lis.append(x)

    return render_template("discover.html", feed = lis)

def followers(user_id):
    relations_list = db.execute("SELECT * FROM Relations WHERE following_id = :userID", {"userID": user_id})
    results = []
    for i in relations_list:
        u =  db.execute("SELECT * FROM Users WHERE userid = :userid" , {"userid": i[0]}).fetchone()
        results.append(u[1])
    return results

def following(user_id):
    relations_list = db.execute("SELECT * FROM Relations WHERE follower_id = :userID", {"userID": user_id})
    results = []
    for i in relations_list:
        u =  db.execute("SELECT * FROM Users WHERE userid = :userid" , {"userid": i[1]}).fetchone()
        results.append(u[1])
    print(results)
    return results

#returns list of accounts following the user
@app.route("/user_followers/<user_name>", methods=["GET"])
def user_followers(user_name):
    if "user" not in session:
        return redirect("/")
    
    user_id = get_user_id(user_name)
    if user_id is None:
        return render_template("error.html",message="User Not Found")
    results = followers(user_id)
    return render_template("relations.html",user=user_name,pagetype="Followers", results=results)

# returns list of accounts followed by the user
@app.route("/user_following/<user_name>", methods=["GET"])
def user_following(user_name):
    if "user" not in session:
        return redirect("/")

    user_id = get_user_id(user_name)
    if user_id is None:
        return render_template("error.html",message="User Not Found")
    results = following(user_id)
    return render_template("relations.html",user=user_name,pagetype="Following", results=results)

def allowed_file_type(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def make_unique(string):
    ident = uuid1().__str__()[:16]
    return f"{ident}-{string}"

# redirect to a page which allows uploading files to the server
# creates a unique name for file and uploads to disk and also stores refernce in the SQL Database
@app.route("/add_file", methods=["POST","GET"])
def add_file():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        if request.form['action'] == 'upload':
            file = request.files.getlist("file")
            caption = request.form.get("caption")
            tags = request.form.get("tags")

            for f in file:
                if f.filename == '':
                    flash("NO FILE UPLOADED!")
                    return redirect(request.url)

                if f and allowed_file_type(f.filename):
                    f.filename = make_unique(f.filename)
                    f.filename = secure_filename(f.filename)
                    upload_file_to_s3(f, S3_BUCKET, caption, tags)
            flash('Image Uploaded Successfully')
            return redirect(request.url)

    return render_template("add.html",user=session['user'])

def upload_file_to_s3(file, bucket_name, caption, tags, acl="public-read"):
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e
    url =  "{}{}".format(S3_LOCATION, file.filename)
    add_file_to_DB(url, caption, tags)

def process_tags(tags):
    tags = "," + tags + ","
    tags = tags.upper()
    print(tags)
    tags = tags.split()

    for i in range(1, len(tags)):
        if tags[i] == ',':
            if tags[i-1]==" ":
                tags.remove(i)
            if tags[i+1]==" ":
                tags.remove(i)

    tags = ''.join(tags)
    return tags

# stores refence of url to sql database
def add_file_to_DB(url, caption, tags):
    timeStamp = (datetime.now(pytz.timezone('America/Toronto')).strftime('%Y-%m-%d %H:%M:%S'))
    user =  db.execute("SELECT * FROM Users WHERE username = :username" , {"username": session["user"]}).fetchone()
    db.execute("INSERT INTO Images (userid, caption, date, imgurl, tags, username) VALUES (:userid, :caption, :date, :imgurl, :tags, :username)",
                    {"userid": user[0], "caption": caption, "date": timeStamp  ,"imgurl": url, "tags": process_tags(tags), "username": user[1]})
    db.commit()


# search function, lets users search based on keywords or tags
@app.route("/search", methods=["POST","GET"])
def search():
    if "user" not in session:
            return redirect("/")

    query = ""
    query_sql = ""

    if request.method=="POST":
        query = request.form.get("query")
        query_sql = "%" + query + "%"
    else:
        query = request.args.get("query")
        query_sql = "%" + query + "%"
    query_sql = query_sql.upper()
    
    img_lis =  db.execute("SELECT * FROM Images WHERE upper(username) Like :username OR tags LIKE upper(:query)", {"username": query_sql, "query": query_sql}).fetchall()

    if request.form.get("exact_search"):
        query_sql = "%," + query + ",%"
        query_sql = query_sql.upper()
        img_lis =  db.execute("SELECT * FROM Images WHERE username LIKE :username OR upper(tags) LIKE (:query)", {"username": session["user"], "query": query_sql}).fetchall()
    
    img_tags_lis =[]
    search_results = []

    c = 0
    for i in img_lis:
        spli = i.tags.split(',')
        img_tags_lis.append(spli)
        x = []
        x.append(img_lis[c])
        x.append(spli)
        c+=1
        search_results.append(x)
     
    return render_template("search.html", query=query, search_results=search_results)

if __name__ == "__main__":
    app.run