from eventnotipy import app
import json

json_data = open('eventnotipy/config.json')
data = json.load(json_data)
json_data.close()

username = data['dbuser']
password = data['password']
host = data['dbhost']
db_name = data['database']

email_host = data['email_host']
email_localhost = data['email_localhost']
sms_host = data['sms_host']
sms_localhost = data['sms_localhost']

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s' % (username,password,host,db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False



app.secret_key = data['session_key']