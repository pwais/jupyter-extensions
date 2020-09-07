from notebook.base.handlers import IPythonHandler, FilesRedirectHandler, path_regex
from notebook.utils import url_path_join
from tornado import web, gen
from tornado.ioloop import PeriodicCallback
from traitlets.config import Config
from nbconvert import HTMLExporter
import nbformat
import logging
import os
import requests

@gen.coroutine
def refresh_token():
    log.info('refreshed')
    r=requests.get(f"{os.environ['JUPYTERHUB_API_URL']}/user/{os.environ['NB_USER']}",
            headers={"Authorization": f"token {os.environ['JUPYTERHUB_API_TOKEN']}"})
    with open(os.environ['OAUTH2_FILE'],'w') as f:
        f.write(f"oauth2:{r.json()['auth_state']['access_token']}:{os.environ['OAUTH_INSPECTION_ENDPOINT']}")

def load_jupyter_server_extension(nb_server_app):
    """
    Called when the Jupyter server extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """

    global log
    log = logging.getLogger('tornado.oauthrenew')
    log.name = "OauthRenew"
    log.setLevel(logging.INFO)
    log.propagate = True

    log.info("Loading Server Extension")
    if os.environ['OAUTH2_FILE'] and os.environ['OAUTH2_TOKEN'] and os.environ['JUPYTERHUB_API_URL']:
        #refresh every 15 minutes
        PeriodicCallback(refresh_token,15*60*1000).start()
 
