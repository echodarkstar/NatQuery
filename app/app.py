from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import json

# import converter as cnv
# initilize flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://darkstar:password@localhost/pagila"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.create_all()
db.session.commit()


# from converter.main import *
@app.route('/', methods=['GET', 'POST'])
def home():
    result = []
    #sql = text("select * from Film")
    #result = db.engine.execute(sql)
    return render_template('index.html', result=result)

@app.route('/query')
def get_query():
    query = request.args.get('nat_query',"not interpreted",type = str)
    query_info = parse_dependency(query, db, class_mapping)
    return jsonify(json.dumps(db_element_selector(query_info, db, class_mapping)))

# run the server
if __name__ == '__main__':
    from converter.main import *
    from models import *
    class_mapping = {
        "actor" : Actor,
        "film" : Film,
        "category" : Category,
        "country" : Country,
        "language" : Language,
        "city" : City,
        "address" : Addres,
        "film_actor" : FilmActor,
        "film_category" : FilmCategory,
        "store" : Store,
        "customer" : Customer,
        "inventory" : Inventory,
        "staff" : Staff,
        "rental" : Rental
    }
    app.run(debug=True)
