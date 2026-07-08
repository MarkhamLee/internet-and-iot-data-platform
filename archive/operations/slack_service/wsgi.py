# standard wrapper that helps gunicorn find the app

import server as myapp

app = myapp.app
