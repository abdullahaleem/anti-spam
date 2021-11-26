import pathlib
from typing import Optional
from fastapi import FastAPI

from . import ml

app = FastAPI()

BASE_DIR = pathlib.Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent.parent / "models" / "spam-detection"
MODEL_PATH = MODEL_DIR / "spam-detection-model.h5"
TOKENIZER_PATH = MODEL_DIR / "spam-detection-tokenizer.json"
METADATA_PATH = MODEL_DIR / "spam-detection-metadata.json"

MODEL = None

# anything we want fast api to depend on e.g. a database or a model we will load it like this
# but where will we load our model to? we will a global variable
@app.on_event("startup")
def on_startup():
    global MODEL
    MODEL = ml.MLModel(
        model_path = MODEL_PATH,
        tokenizer_path = TOKENIZER_PATH,
        metadata_path = METADATA_PATH,
    )
    
# we want the query to be something we pass in whichi would be a url parameter e.g. /?q=this is awesome
# the input has to be q we can't name it arbitrarily string etc.
@app.get("/")
def read_index(q: Optional[str]=None):
    global MODEL
    query = q or "hello world"
    predictions = MODEL.predict_text(query)
    return {"query": query, "results": predictions}