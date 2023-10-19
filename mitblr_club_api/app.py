from sanic import Sanic

appserver = Sanic("club-api", strict_slashes=False)
appserver.extend(oas_ui_swagger=False)
appserver.ext.openapi.describe(
    ".club API",
    version="1.0.0",
    description="This is a test.",
)
