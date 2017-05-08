from eventnotipy import app
from gevent.pywsgi import WSGIServer
import time

app.debug = True # disable for production

# if __name__ == '__main__':
# app.run(host='0.0.0.0',port=8540)
# use WSGIServer to try and reduce timeout errors seen occasionally
date = time.strftime('%Y-%m-%d %H:%M:%S')
print('Server Started: %s' % date)
print('Running on port 8540...')
WSGIServer(('0.0.0.0',8540),app).serve_forever()
