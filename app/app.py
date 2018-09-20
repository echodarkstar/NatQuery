from flask import Flask, render_template, request, jsonify

# initilize flask
app = Flask(__name__)


# routes



@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

# run the server
if __name__ == '__main__':
    app.run(debug=True)
