from dash.api import application as app
from dash.api.dependencies import DashboardApiModule

application = app.create_application('my-config-file', DashboardApiModule())
