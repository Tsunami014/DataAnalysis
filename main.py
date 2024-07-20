import flask
from asyncro import wrapper, statuses

app = flask.Flask(__name__)

@wrapper
def long_task(update):
    import time, random
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit', 'bob']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        update(state='PROGRESS',
                current=i,
                total=total,
                status=message)
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

"""@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)"""

@app.route('/get_task/<URL>')
def get_task(URL):
    return flask.jsonify(statuses[URL])

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

@app.route('/')
def main():
    return flask.render_template("index.html")

app.run()
