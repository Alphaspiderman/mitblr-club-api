"""API endpoints for external (MS-Entra) authentication provider."""
from sanic import Request, redirect
from sanic.views import HTTPMethodView
from sanic_ext import validate
import uuid

from mitblr_club_api.models.request.ms_auth import MsAuth


class ExternalAuth(HTTPMethodView):
    template = (
        "https://login.microsoftonline.com/%(tenant)s/oauth2/v2.0/authorize?client_id=%(client_id)s"
        "&response_type=id_token "
        "&response_mode=form_post"
        "&redirect_uri=%(redirect_uri)s"
        "&nonce=%(nonce)s"
        "&scope=%(scope)s"
        "&state=%(state)s"
    )

    @validate(query=MsAuth)
    async def get(self, request: Request, query: MsAuth):
        """Return a URL to authenticate against Azure AD with a state."""
        token_id = uuid.uuid1()
        nonce = uuid.uuid1()

        # Save the token ID and nonce
        request.app.ctx.tokens[token_id] = nonce

        # Generate the URL to redirect the user to.
        url = self.template % {
            "tenant": request.app.config["AZURE_AD_TENANT_ID"],
            "client_id": request.app.config["AZURE_AD_CLIENT_ID"],
            "redirect_uri": request.app.config["AZURE_AD_REDIRECT_URI"],
            "scope": "openid profile email offline_access",
            "state": token_id,
            "nonce": nonce,
        }

        # Return a redirect
        return redirect(url)
