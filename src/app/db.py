"""
Goal of this is to make a way to connect to any given session and cluster inside astradb
"""
import pathlib
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection

from . import config


BASE_DIR = pathlib.Path(__file__).resolve().parent

SOURCE_DIR = BASE_DIR / "ignored"
if not SOURCE_DIR.exists():
    SOURCE_DIR = BASE_DIR / "decrypted_db"

CLUSTER_BUNDLE = str(SOURCE_DIR / "astradb_connect.zip") # we want it to be a string for our cluster

settings = config.get_settings()

ASTRA_DB_CLIENT_ID = settings.db_client_id
ASTRA_DB_CLIENT_SECRET = settings.db_client_secret 

def get_cluster():
    cloud_config= {
        'secure_connect_bundle': CLUSTER_BUNDLE
        }
    auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    return cluster

def get_session():
    """
    We get the session in a diffrent manner cause of how our application is gonna
    be working in fastapi
    The two connection things are extra from documentation cause of fastapi
    """
    cluster = get_cluster()
    session = cluster.connect()
    connection.register_connection(str(session), session=session) # because we are gonna be using this session throughout our fastapi session
    connection.set_default_connection(str(session)) 
    return session