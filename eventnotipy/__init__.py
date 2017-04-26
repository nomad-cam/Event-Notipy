from flask import Flask

app = Flask(__name__)

import eventnotipy.config
import eventnotipy.views