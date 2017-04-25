from flask import request,current_app
from eventnotipy import app

@app.route('/')
def hello_world():
    return 'Access Denied!'

@app.route('/event/<change_type>')
def on_change(change_type):
    return 'Event Changed: %s' % change_type

