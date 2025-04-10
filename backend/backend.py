from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/retrieve/<string:repolink>')
def retrieve(repolink):
    # Placeholder for the actual retrieval logic


    return send_file('output.json', mimetype='application/json', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)