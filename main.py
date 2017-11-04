from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey

app=Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz2:mypassword@localhost:3306/blogz2'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y350kGcys&zp38'

class Blogz2(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    blog = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
     
    def __init__(self, title,blog,owner):
        self.title = title 
        self.blog = blog
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blogz2',backref ='owner')

    def __init__(self, uname,password):
        self.uname = uname
        self.password = password


@app.before_request
def require_login():
#   allowed pages
    allowed_routes = ['login','index','post_blogs','signup','register']
    if request.endpoint not in allowed_routes and 'uname' not in session:
        return redirect('login')

@app.route('/login', methods=['POST','GET'])
def login():    
    if request.method == 'POST':
        uname = request.form['uname']
        password = request.form['password']
#       login details
        user = User.query.filter_by(uname=uname).first()
        if user and user.password == password:
            session['uname'] = uname
            flash("Logged in")
            return redirect('/new_post')
        else:
            flash('user password is not correct')
            return '<h1>User does not exist </h1>'
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST','GET'])
def register():
    
    if request.method =='POST':
        uname = request.form['uname']
        password = request.form['password']
        verify = request.form['verify']
#   sign up page        
        error_name =""
        error_password = ""
        error_pass_same = ""
        password1=""
            
        existing_user = User.query.filter_by(uname=uname).first()
    
        if existing_user :
           return "Duplicate user"

        if not existing_user :
            if password == "":
                error_password = "'{0}'please specify the password".format(password)
                password=""
            else:
                if len(password) > 20:
                    password = ""
                    error_password = "password lenght is more than 20 Characters"
                    password1=password
                else:
                    if len(password) < 3:
                        error_password = "password is less than 3 characters"
                        password1=password
                        password=""
                    else:
                        password = password
            if verify == "":
                error_pass_same = "'{0}'password re-enter is empty".format(verify)
                verify=""
                password=""
            else:
                if verify != password:
                    if password1 == verify : 
                        verify =""
                        password=""
                    else:
                        error_pass_same = "Password did not match "
                        verify =""
                        password=""
                else:
                    if verify == password : 
                        if password1 != "" :
                            password = ""
                            verify = ""
                if password == "":
                    verify = ""
                else:
                    verify = verify
            if uname == "":
                error_name = "'{0}'please specify the username".format(uname)
                uname=""
            else:
                if len(uname) > 20:
                    error_name = "username can be a max of 20 characters"
                    uname=""
                
                else:
                    if len(uname) < 3 :
                        error_name = "username should be at least 3 letters long"
                        uname=""
                    
                    else:
                        uname = uname
            
            if not error_name and not error_password and not error_pass_same  :
                new_user = User(uname,password)
                db.session.add(new_user)
                db.session.commit()
                session['uname'] = uname
                return redirect('/')
            else:    
                return render_template('signup.html',
                    uname=uname,
                    password=password,
                    verify=verify,
                    error_name=error_name,
                    error_password=error_password,
                    error_pass_same=error_pass_same)


@app.route('/logout')
def logout():
    del session['uname']
    return redirect('/')


@app.route('/', methods=['POST', 'GET'])
def index():
    user = request.args.get('uname')
    if request.method == 'GET' :    
        users = User.query.all()
#   user list in root
        return render_template('index.html',users=users)

@app.route('/newpost')
def new_post_index():
    return render_template('new_post.html')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error =""
    blog_error = ""
    if request.method == 'POST' :
       input = request.form['title']
       entry = request.form['blog']
#   new Post by user
       if input =="" :
          title_error = "Field cannot be empty"
       if entry == "":
          blog_error = "Field cannot be empty"
          title=""
    if not title_error and not blog_error :
       if input != "" :
            owner = User.query.filter_by(uname=session['uname']).first()
            input_data = Blogz2(input , entry, owner)
            db.session.add(input_data)
            db.session.commit()
            input_id = Blogz2.query.filter_by(title=input).first().id
            owner_id = Blog.query.filter_by(id=input_id).first().owner_id
            user_name = User.query.filter_by(id=owner_id).first().uname
            return redirect('/blog?id='+str(input_id))
    else: 
        return render_template('/new_post.html',title_error=title_error,blog_error=blog_error)     
     


@app.route('/blog')
def post_blogs():
    add_columns = []
    blogs1 = Blogz2.query.join(User).add_columns(Blogz2.id,Blogz2.title,Blogz2.blog,User.uname).filter(Blogz2.owner_id==User.id).all()    
    blogs = Blogz2.query.all()

    blog_user = request.args.get('user')
    if blog_user :
        blog_user_id = User.query.filter_by(uname=blog_user).first().id
#   User Blogs    
        blogs2 = Blogz2.query.join(User).add_columns(Blogz2.id,Blogz2.title,Blogz2.blog,User.uname).filter(Blogz2.owner_id==blog_user_id).all()
        return render_template('singleuser.html',blogs2=blogs2,blog_user = blog_user)

    if request.args.get('id') == None :
        blogs = Blogz2.query.all()
#   Print all blogs
        return render_template('blog.html',blogs1=blogs1)
    elif request.args.get('id') != "" :
#   print one blog
        input_id = request.args.get('id')
        input= Blog.query.filter_by(id=input_id).first().title
        entry= Blog.query.filter_by(id=input_id).first().blog
        blog_user_id = Blog.query.filter_by(id=input_id).first().owner_id
        user_name = User.query.filter_by(id=blog_user_id).first().uname
        return render_template('blog.html',input_id = input_id,input=input,entry=entry,user_name=user_name)

if __name__=='__main__':
    app.run()
