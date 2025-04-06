from flask import Flask, render_template, request, session, redirect, url_for, abort, jsonify
import os
import json
from src import kmpostgres
from src import kmelasticsearch

app = Flask(__name__)

DEMO = True if os.environ.get("DEMO") else False
if DEMO:
    app.config['DEMO_MODE'] = True

app.secret_key = 'your_secret_key_here'  # TODO: get this from secrets manager

CONN_PARAMS = {
    'host': os.environ.get("POSTGRES_URL", 'localhost'),
    'user': os.environ.get("POSTGRES_USER", 'docker'),
    'password': os.environ.get("POSTGRES_PW", 'docker'),  # TODO: move this from OS to secrets manager
    'port': os.environ.get("POSTGRES_PORT", 5432)
}

ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', "http://localhost:9200")
print(f'Elasticsearch URL: {ELASTICSEARCH_URL}')


def require_auth_abort(func):
    """Decorator to enforce authentication depending on config."""
    def wrapper(*args, **kwargs):
        if app.config['DEMO_MODE']:
            # In demo mode, inject a default user
            session['user'] = 'demo_user'
        else:
            # TODO: setup flask-kerberos 
            if not request.environ.get('REMOTE_USER'):
                # If the Kerberos user isn’t set, abort
                abort(401)  # Unauthorized
        return func(*args, **kwargs)
    # Copy the function name and docstring
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


@app.route("/", methods=["GET"])
def index():
    # Get search query from URL parameters (if any).
    search_query = request.args.get("q", "")
    results = []

    user = ""
    kerberos_authenticated = False
    if app.config['DEMO_MODE']:
        user = session.get('user', 'demo_user')
        kerberos_authenticated = True
    if request.environ.get('REMOTE_USER'):
        user = request.environ.get('REMOTE_USER')
        kerberos_authenticated = True

    try:
        # For demonstration, we use a full table scan.
        # In production, consider using Query with proper keys/indexes.
        if search_query:
            results = kmelasticsearch.search_records(search_query, ELASTICSEARCH_URL)
        else:
            results = kmelasticsearch.get_latest(ELASTICSEARCH_URL)
        formatted_results = results
    except Exception as e:
        # Log error and optionally handle errors gracefully.
        print(f"Error querying Elasticsearch: {ELASTICSEARCH_URL}", e)

    return render_template(
        "index.html", 
        results=formatted_results, 
        search_query=search_query,
        user=user,
        kerberos_authenticated=kerberos_authenticated
    )


@app.route('/new-link', methods=['GET', 'POST'])
@require_auth_abort
def new_link():

    user = ""
    kerberos_authenticated = False
    if app.config['DEMO_MODE']:
        user = session.get('user', 'demo_user')
        kerberos_authenticated = True
    if request.environ.get('REMOTE_USER'):
        user = request.environ.get('REMOTE_USER')
        kerberos_authenticated = True

    if request.method == 'POST':
        if app.config['DEMO_MODE']:
            user = session.get('user', 'demo_user')
        elif request.environ.get('REMOTE_USER'):
            user = request.environ.get('REMOTE_USER')
        else:
            abort(400)

        link = request.form.to_dict()
        link['tags'] = json.loads(link['tags'])
        link['samaccountname'] = user
        kmpostgres.insert_record(CONN_PARAMS, **link)

        # After saving, redirect home
        return redirect(url_for('index'))
    return render_template('new_link.html',
                           user=user,
                           kerberos_authenticated=kerberos_authenticated)


@app.route('/manage-links', methods=['GET'])
@require_auth_abort
def manage_links():
    
    user = ""
    kerberos_authenticated = False
    if app.config['DEMO_MODE']:
        user = session.get('user', 'demo_user')
        kerberos_authenticated = True
    if request.environ.get('REMOTE_USER'):
        user = request.environ.get('REMOTE_USER')
        kerberos_authenticated = True

    if app.config['DEMO_MODE']:
        user = session.get('user', 'demo_user')
    if request.environ.get('REMOTE_USER'):
        user = request.environ.get('REMOTE_USER')

    records = kmelasticsearch.get_user_records(user, ELASTICSEARCH_URL)
    return render_template('manage_links.html',
                           records=records,
                           user=user,
                           kerberos_authenticated=kerberos_authenticated)


@app.route('/update_record', methods=['POST'])
@require_auth_abort
def update_records():
    if app.config['DEMO_MODE']:
        user = session.get('user', 'demo_user')
    elif request.environ.get('REMOTE_USER'):
        user = request.environ.get('REMOTE_USER')
    else:
        abort(403)

    record = request.json
    if not record:
        abort(400)
    try:
        record['id'] = int(record['id'])
    except Exception as e:
        print(f"Error {e}")
        abort(400)
    record['tags'] = json.loads(record['tags'])
    record['samaccountname'] = user
    success = kmpostgres.update_record(CONN_PARAMS, **record)
    if success:
        return jsonify({'success': success})
    else:
        abort(500)


@app.route('/delete_record', methods=['POST'])
@require_auth_abort
def delete_record():
    if app.config['DEMO_MODE']:
        user = session.get('user', 'demo_user')
    elif request.environ.get('REMOTE_USER'):
        user = request.environ.get('REMOTE_USER')
    else:
        abort(403)

    record = request.json
    if not record:
        abort(400)
    try:
        record['id'] = int(record['id'])
    except Exception as e:
        print(f"Error {e}")
        abort(400)
    print(record)
    record['samaccountname'] = user
    print(record)
    success = kmpostgres.delete_record(CONN_PARAMS, **record)
    essuccess = kmelasticsearch.delete_record(record, ELASTICSEARCH_URL)
    if success and essuccess:
        return jsonify({'success': success})
    else:
        abort(500)


if __name__ == "__main__":
    # Run the app on 0.0.0.0 so it’s accessible in the container.
    app.run(host="0.0.0.0", port=5000, debug=True)

