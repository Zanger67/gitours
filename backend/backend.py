from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/retrieve/<string:repolink>')
def retrieve(repolink):
    # Placeholder for the actual retrieval logic
    return f'Retrieving data from {repolink}'

if __name__ == '__main__':
    app.run(debug=True)