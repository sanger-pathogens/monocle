from dash.api import application as app
from dash.api.dependencies import ApiModule

application = app.create_application('config.json', ApiModule())
