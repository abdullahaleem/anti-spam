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
    return {"info": "spam detection api. make a post request with a text"}

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

every once in a while while you are updating a project simple do
the reason is once you start building things on produciton env it will starting eating up room
so pruning it is a good idea
docker system prune -a --volumes

docker run -it image-name /bin/bash is like ssh into the container

Once we the gunicorn inside docker we don't actually have access to the app
as its still running locally
we will use the following command to make the app available
over here we are making setting the env variable port to 8001 as we can from entrypoint.sh although the default is 8000.
Next we map the outside port 80 (default) to that port inside the container which gunicorn in running on
Next we will also detach it.
docker run --restart always -e PORT=8001 -p 80:8001 -d spam-detection

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

we want to automate as much such as possible so we dont have to do it manually
we want to know how to do it manaually first before automating using ci cd piplines
"""
"""
Consideration we should have while updating our code and project
We would clone the virtual machine, make changes to the clone and then rotate things.
On digital ocean to clone we can make an image of the vm (snapshot) and do it that way
We would also add a private ip address to these vm so we can implement a load balancer.
The idea is with the new clone we would power it on. Then we can make changes to a clone and
replicate it again to other one. But that wont be efficent. 
What would be more efficent and better in long term would be to have a load balancer.
The load balancer would do a couple of things.
 1. it would distribute the load accross the machine so not one of them is handling everything
 2. it will allow us to rotate the vm machines easily.

We can automate most of this stuff using IaC.
We can use github actions to run workflows and use tool like terraform to provision the infrastructure
as in turning on our instances, adding load baalncers, write scipts to pull all the code, run docker install, build etc.
All of the stuff can be handled using a combination of github actions and terraform.
Doing things manually is how you end up causing alot of errors and breaking alot of stuff causing downtime.

Another part about actions which is very cool and will better secture the environment is that you can put
env variable in github actions so you are not manually doing it e.g. hardcoding.

We need to have an automated deployment pipeline.
"""