import json

from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from ._compat import urljoin
from .model import Customer

__all__ = [
    "FileTokenStorage",
    "VismaSession",
    "Store",
]

class FileTokenStorage(object):
    # TODO: The current approach is possibly not thread safe unless there is a
    #       separate token storage, with its own file, per thread.
    def __init__(self, path):
        self.path = path

    def load(self):
        try:
            with open(self.path, "r") as f:
                return json.loads(f.read())
        except IOError as e:
            if e.errno == 2:
                return None
            raise e

    def save(self, token):
        with open(self.path, "w") as f:
            f.write(json.dumps(token))

    def __bool__(self):
        return self.load() is not None

    __nonzero__ = __bool__


class VismaSession(OAuth2Session):
    """
    A OAuth2 session for Visma eAccounting API.

    This class is an extension of
    :class:`requests_oauthlib.oauth2_session.OAuth2Session` with some
    compatibility fixes for Visma. The ``client`` parameter has been replaced
    by a ``client_secret`` parameter since the API only supports
    :class:`oauthlib.oauth2.WebApplicationClient`.

    :param client_id: Client ID as provided by Visma
    :param client_secret: Client secret as provided by Visma
    :param scope: List of scopes you wish to request access to
    :param redirect_uri: Redirect URI you registered as callback
    :param token: Token dictionary, must include access_token and token_type.
    :param state: State string used to prevent CSRF. This will be given
                  when creating the authorization url and must be supplied
                  when parsing the authorization response. Can be either a
                  string or a no argument callable. This parameter is optional.
    :param auto_refresh_url: Refresh token endpoint URL, must be HTTPS. Supply
                             this if you wish the client to automatically refresh
                             your access tokens.
    :param auto_refresh_kwargs: Extra arguments to pass to the refresh token
                                endpoint.
    :param token_updater: Method with one argument, token, to be used to update
                          your token databse on automatic token refresh. If not
                          set a TokenUpdated warning will be raised when a token
                          has been refreshed. This warning will carry the token
                          in its token argument.
    :param base_url: Base URL to use for all HTTP(S) requests unless an absolute
                     URI is provided.
    """

    def __init__(
            self, client_id=None, client_secret=None, auto_refresh_url=None,
            auto_refresh_kwargs=None, scope=None, redirect_uri=None, token=None,
            state=None, token_updater=None, base_url=None):
        self.base_url = base_url
        self.client_secret = client_secret
        self.auth = HTTPBasicAuth(client_id, client_secret)

        super(VismaSession, self).__init__(
            client_id, None, auto_refresh_url, auto_refresh_kwargs, scope,
            redirect_uri, token, state, token_updater)

    def request(
            self, method, url, data=None, headers=None, withhold_token=False,
            client_id=None, client_secret=None, **kwargs):

        if self.base_url is not None:
            url = urljoin(self.base_url, url)

        if client_id is None:
            client_id = self.client_id

        if client_secret is None:
            client_secret = self.client_secret

        return super(VismaSession, self).request(
            method, url, data, headers, withhold_token, client_id,
            client_secret, **kwargs)


class Store(object):
    """
    Connection manager for Visma API connection.

    This class provides methods of querying and persisting objects
    over the API.

    :param client: Client used to handle communication over the API.
                   This is in most cases an instance of :class:`VismaSession`,
                   but the only requirement is that it manages authentication
                   and provide a method ``request`` which the same arguments
                   as Requests' ``request`` method.
    """

    def __init__(self, client):
        self.client = client

    def find(self, type, **params):
        """
        Return a list of objects of the given ``type`` which matches
        the filters provided as keyyword arguments.

        :param type: Class to list
        :param  **params: Keyword arguments to pass on to
                          ``type._visma_list(**params)``.
        :return: List of type ``type`` instances
        :rtype: [type]
        """
        response = self.client.request(**type._visma_list(**params))

        if response.status_code != 200:
            raise IOError(
                "Failed to list {name}': '{content}'".format(
                    name=type.__name__,
                    content=request.content))

        return [type.from_json(data) for data in response.json()]

    def get(self, type, id):
        """
        Return the object of ``type`` with `ìd``.

        :param type: Class of get
        :param id: Visma's unique object ID, UUID style string
        :return: Instance of type ``type`` if ID exists, else ``None``
        :rtype: ``type`` or None
        """

        response = self.client.request(**type._visma_get(id))

        if response.status_code != 200:
            raise IOError(
                "Failed to get {name} with ID '{id}': '{content}'".format(
                    name=type.__name__,
                    id=id,
                    content=request.content))

        return type.from_json(response.json())

    def add(self, obj):
        """
        Store the given object in in Visma.

        :param obj: Object to store
        """

        response = self.client.request(**obj._visma_add())

        if response.status_code != 200:
            raise IOError(
                "Failed to add {name} with ID '{id}': '{content}'".format(
                    name=obj.__class__.__name__,
                    id=id,
                    content=request.content))

        obj.from_json(response.json())
