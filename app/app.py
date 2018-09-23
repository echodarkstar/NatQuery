from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
# from models import Actor, Film

from config import *

from sqlalchemy import text

# initilize flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app)
db.create_all()
db.session.commit()

# routes

@app.route('/', methods=['GET', 'POST'])
def home():
    #actors = db.session.query(Actor).all()
    sql = text("select * from Film where film_id = 20")
    result = db.engine.execute(sql)
    return render_template('index.html', result=result)

# run the server
if __name__ == '__main__':
    app.run(debug=True)
