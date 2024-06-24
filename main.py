import flask

app = flask.Flask(__name__)

@app.route('/')
def main():
    return flask.render_template("index.html").replace(r'%uniqueTextToBeReplaced%%', 'THIS TEXT GOT REPLACED >:)')

@app.route('/test_get')
def test_get():
    return "THIS TEXT ALSO GOT REPLACED >:) >:)"

app.run()
