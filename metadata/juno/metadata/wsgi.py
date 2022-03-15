from metadata.api import application as app
from metadata.api.dependencies import MetadataApiModule

application = app.create_application("config.json", MetadataApiModule())
