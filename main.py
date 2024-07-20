import flask
from asyncro import wrapper, statuses
from getWeather import cached_status, remove_cache

app = flask.Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return flask.url_for('static', filename='favicon.ico')

@wrapper
def long_task(update):
    import time, random
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking', 'Preparing', 'Cleaning']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast', 'red', 'quick', 'silly']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit', 'fire brigade', 'space station']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        update(current=i,
               total=total,
               status=message)
        time.sleep(random.randint(2, 20)/10)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

@app.route('/status/<task_id>')
def status(task_id):
    if task_id not in statuses:
        return flask.jsonify({'State': 'NONEXISTANT'})
    return flask.jsonify(statuses[task_id])

@app.route('/longtask', methods=['POST'])
def longfunc():
    long_task('longtask')
    return flask.jsonify({}), 202

@app.route('/read-form', methods=['POST'])
def read_form(): # Thanks to https://www.geeksforgeeks.org/how-to-use-web-forms-in-a-flask-application/
    # Get the form data as Python ImmutableDict datatype
    data = flask.request.form
  
    ## Return the extracted information
    return data

@app.route('/get_files', methods=['POST'])
def get_files(): # Thanks to https://www.geeksforgeeks.org/how-to-use-web-forms-in-a-flask-application/
    # Get the form data as Python ImmutableDict datatype
    data = {'Cache': 'off', 'Force': 'off'} # Because when it's off, for some reason it does not show in the dict
    data.update(dict(flask.request.form))
  
    ## Return the extracted information
    return data

@app.route('/cache_status')
def cache_status():
    return cached_status(flask.request.args.get('cache') == 'true', flask.request.args.get('force') == 'true')

@app.route('/delete_cache')
def delete_cache():
    remove_cache()
    return flask.jsonify({})

@app.route('/')
def main():
    return flask.render_template("index.html")

app.run()
