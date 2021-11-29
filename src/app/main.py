"""
This rest api has 3 primary functions
    1. Provide good predicitons if a string of text is spam or not
    2. Improve the conditions to which it can make better predictions (storing data)
    3. Have it open and in production for other applications and user 
"""
import pathlib
from typing import Optional
from cassandra import cqlengine
from cassandra import query
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from cassandra.query import SimpleStatement
from cassandra.cqlengine.management import sync_table

from . import (config, ml, db, model)
from . import schema

app = FastAPI()
settings = config.get_settings() # this is the only way to grab env variables inside fast api. os.environ doesnt work


BASE_DIR = pathlib.Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent.parent / "models" / "spam-detection"
MODEL_PATH = MODEL_DIR / "spam-detection-model.h5"
TOKENIZER_PATH = MODEL_DIR / "spam-detection-tokenizer.json"
METADATA_PATH = MODEL_DIR / "spam-detection-metadata.json"

MODEL = None
DB_SESSION = None
SpamInference = model.SpamInference

# anything we want fast api to depend on e.g. a database or a model we will load it like this
# but where will we load our model to? we will a global variable
@app.on_event("startup")
def on_startup():
    global MODEL, DB_SESSION
    MODEL = ml.MLModel(
        model_path = MODEL_PATH,
        tokenizer_path = TOKENIZER_PATH,
        metadata_path = METADATA_PATH,
    )
    DB_SESSION = db.get_session()
    sync_table(SpamInference)

@app.get("/")
def read_index(q: Optional[str]=None):
    return {"info": "spam detection website"}

# we want the query to be something we pass in whichi would be a url parameter e.g. /?q=this is awesome
# the input has to be q we can't name it arbitrarily string etc.
# 
@app.post("/")
def create_inference(q:schema.Query):
    global MODEL
    #query = q or "hello world"
    predictions = MODEL.predict_text(q.text)
    top = predictions["top"]
    data = {"query": q.text, **top}
    obj = SpamInference.objects.create(**data)
    return obj

@app.get("/inferences/{uuid}")
def read_inference(uuid):
    obj = SpamInference.objects.get(uuid=uuid)
    return obj

# list out all our data. by default is the limit is 10000
@app.get("/inferences/")
def list_inferences():
    query_set = SpamInference.objects.all()
    return list(query_set)


def fetch_rows(statement:SimpleStatement, fetch_size:int=25, session=None):
    statement.fetch_size = fetch_size
    result_set = session.execute(statement)
    has_pages = result_set.has_more_pages
    yield "uuid, label, confidence, query, model_version\n"
    while has_pages:
        for row in result_set.current_rows:
            yield f"{row['uuid'], row['label'], row['confidence'], row['query'], row['model_version']}\n"
        has_pages = result_set.has_more_pages
        result_set = session.execute(statement, paging_state=result_set.paging_state)


# way to execute queries, we can change the limit etc. here
# streamning response allows us to call a generator and returhn the yeilded data from genenetor
# we want to turn the cql query to generator table in csvn
# pagination using cassandra database
@app.get("/dataset/")
def export_inferences():
    global DB_SESSION
    cql_query = "SELECT * FROM spam_inferences.spam_inference LIMIT 10000"
    statement = SimpleStatement(cql_query)
    #rows = DB_SESSION.execute(cql_query)
    return StreamingResponse(fetch_rows(statement, 25, DB_SESSION))


# ngrok will allow is to emulate a production enivronement

# we will not use the heroku or digital ocean because we dont control the entire environement
# we dont control the infrastructure

# Private github repos
# think of vm machines as temp sessions and not work stations
# we can add github user and id when we clone the repo but we want to do something more
# sustainable here. we will use github personal access tokens for this
# first we will add personl token to machine using export TOKEN = <TOKEN>
# then git clone https://${TOKEN}:x-oauth-basic@github.com/abdullahaleem/spam-detection-microservice.git

"""
Docker
When we are dealing with machine learning specially we need to super careful about versions of python and packages
highly recommended to islolate our applicaiton. Great choice for production. To install docker
sudo apt-get update -y
curl -fsSL https://get.docker.com -o get_docker.sh
sudo bash get_docker.sh
sudo apt-get autoremove -y # after installing things



"""
"""
nginx
when the system reboots the container will restart itself
docker run --restart always -p 80:80 -d nginx
"""

"""
ci/cd

in long run we will not hardcode our env variables in the remote machine
and we will use the ci/cd to configure the remote machine
we can use terraform to help automate all of this configuation and deployment process
once we have mostly configured it is something that would be done on regular basis


we dont have to astradb_connect.zip or models in our docker and we need to setup pipelines
to automate the process of getting those things. we will bring pipeline in docker as well

one method we can get astra-db connect to docker is using a pipeline but one problem is that 
its not encrypted. what we actually wanna do is encrpt this and upload it onto git and then
decrpyt in our production application
"""