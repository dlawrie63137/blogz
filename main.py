from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:1234@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(400))
    
    def __init__(self, title, body):
        self.title = title
        self.body = body
        

@app.route("/", methods=['POST', 'GET'])
def index():
    return redirect('/blog')


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    t_error=''
    b_error=''

    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-body']

        if blog_title == "" :
            t_error = 'Please fill out Title.'
        if blog_body == "":
            b_error = 'Please fill in body of post.'
            
        if len(t_error) > 2 or len(b_error) > 2:
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, t_error=t_error, b_error=b_error)
        else:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            id=str(new_blog.id)
            return redirect('/blog?id=' + id)

    return render_template('newpost.html')
    
@app.route("/blog", methods=['GET'])
def show_post():
    if request.args.get('id'):
        id=request.args.get('id')
        entry=Blog.query.filter_by(id=id).first()
        return render_template('post.html', entry=entry)
        

    entries = Blog.query.all()
    return render_template('blog.html', title='Build A Blog', entries=entries)

if __name__ == '__main__':
    app.run()