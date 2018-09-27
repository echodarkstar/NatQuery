from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
# from models import *

from sqlalchemy import text

# initilize flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://darkstar:password@localhost/pagila"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.create_all()
db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def home():
    result = []
    #sql = text("select * from Film")
    #result = db.engine.execute(sql)
    return render_template('index.html', result=result)

# run the server
if __name__ == '__main__':
    app.run(debug=True)
