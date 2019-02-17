from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'po54b03mh84n'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(400))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True)
    pw_hash = db.Column(db.String(150))
    blogs = db.relationship('Blog', backref='user')
    
    def __init__(self, username, password):
        self.username = username
        self.pw_hash=make_pw_hash(password)   

@app.before_request
def require_login():
    allowed_routes = ['login', 'show_post', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.args.get('id'):
        id=request.args.get('id')
        user=User.query.filter_by(id=id).first()
        posts=Blog.query.filter_by(user_id=user.id).all()
        return render_template('singleUser.html', posts=posts, user=user)
    
    users = User.query.all()
    return render_template('index.html', users=users)

def string_exists(username, password, verify):
    if username=="" or password=="" or verify=="":
        return False
    return True

def validate_username(username):
    if len(username) < 3:
        return False
    return True

def validate_password_length(password):
    if len(password) < 3:
        return False
    return True

def confirm_password(password, verify):
    if len(password) != len(verify):
        return False
    for idx in range(len(password)):
        if password[idx] != verify[idx]:
            return False
    return True

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        verify=request.form['verify']
        
        #check for empty fields
        if not string_exists(username, password, verify):
            flash('One or more field is empty. Please try again.', 'error')
            return redirect('/signup')
        
        #validate username
        if not validate_username(username):
            flash('Username must be at least 3 characters long.', 'error')
            return redirect('/signup')

        #validate password
        if not validate_password_length(password):
            flash('Password must be at least 3 characters long.', 'error')
            return redirect('/signup')

        if not confirm_password(password, verify):
            flash('Passwords do not match.', 'error')
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()

        #if user not in db & password good, enter user into db
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
           #error message, username already exists in db
           flash('That name is already in use.', 'error')
           return redirect('/signup')
    return render_template("signup.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
        #retrieve user info from login page
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        #user not in db, return to login page
        if not user:
            flash('User does not exist.', 'error') 
            return redirect('login')
        
        #everything is good, begin session 
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash(username + ":" + " Logged In", 'info')
            return redirect('/newpost')
        else: # incorrect password, return to login page
            flash("Password is incorrect.", 'error')
            return redirect('/login')
               
    return render_template("login.html")

def check_blog_input(str):
    if str != "":
        return True
    return False

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    t_error=''
    b_error=''

    user = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']
        
        if not check_blog_input(blog_title):
            t_error = 'Please fill out Title.'
        if not check_blog_input(blog_body):
            b_error = 'Please fill in body of post.'
            
        if len(t_error) > 2 or len(b_error) > 2:
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body,
                                     user=user, t_error=t_error, b_error=b_error)
        else:
            new_blog = Blog(blog_title, blog_body, user)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/newpost')
    return render_template('newpost.html')
    
@app.route("/blog", methods=['GET'])
def show_post():
    if request.args.get('id'):
        print('are we still here?')
        id=request.args.get('id')
        entry=Blog.query.filter_by(id=id).first()
        user_id=entry.user_id
        poster=User.query.filter_by(id=user_id).first()
        return render_template('post.html', entry=entry, poster=poster)
    
    if request.args.get('user'):
        print('did we get here?')
        username=request.args.get('user')
        poster=User.query.filter_by(username=username).first()
        user_id=poster.id
        entry=Blog.query.filter_by(id=user_id).first()
        return render_template('post.html', entry=entry, poster=poster)
    
    #entries = Blog.query.all()
    print('Are we stuck here?')
    user=Blog.query.join(User).add_columns(Blog.user_id, Blog.title, Blog.body, User.id, User.username).filter_by(id=Blog.user_id).all()
    #poster=User.query.all()
    return render_template('blog.html', title='Blogz', user=user)#entries=entries,)

# End session & redirect to blog page  when user logs off
@app.route('/logout')
def logout():
    print (session['username'])
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()