from flask import Flask
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)

import eventnotipy.config
import eventnotipy.views