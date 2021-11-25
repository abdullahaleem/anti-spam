import json
import pathlib
import numpy as np
from typing import Optional
from fastapi import FastAPI
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = FastAPI()

BASE_DIR = pathlib.Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent.parent / "models" / "spam-detection"
MODEL_PATH = MODEL_DIR / "spam-detection-model.h5"
TOKENIZER_PATH = MODEL_DIR / "spam-detection-tokenizer.json"
METADATA_PATH = MODEL_DIR / "spam-detection-metadata.json"

ML_MODEL = None
TOKENIZER = None
METADATA = None

# anything we want fast api to depend on e.g. a database or a model we will load it like this
# but where will we load our model to? we will a global variable
@app.on_event("startup")
def on_startup():
    global ML_MODEL, TOKENIZER, METADATA
    if MODEL_PATH.exists():
        ML_MODEL = load_model(MODEL_PATH)
    if TOKENIZER_PATH.exists():
        tokenizer_json = TOKENIZER_PATH.read_text()
        TOKENIZER = tokenizer_from_json(tokenizer_json)   
    if METADATA_PATH.exists():
        METADATA = json.loads(METADATA_PATH.read_text())


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    

def predict(query: str):
    legend_inverted = METADATA["label_legend_inverted"]
    sequences = TOKENIZER.texts_to_sequences([query])
    model_input = pad_sequences(sequences, maxlen=METADATA["max_sequence_length"])
    preds_array = ML_MODEL.predict(model_input)
    preds = preds_array[0]
    top_idx= np.argmax(preds)
    # without coverting to float we would get an error because pred is giving us
    # back numpy numbers and fast api is trying to dump it into json and numpy numbers
    # is not json serialiable
    # we can also implement a numpy encoder and we can use it for all sorts of things
    # and dont have to explicity specificy the types. We encode using custoemr encoder and
    # then convert it back to python dictionary
    
    # top_pred = {"label": legend_inverted[str(top_idx)], "confidence": float(preds[top_idx])}
    # labeled_preds = [{"label": legend_inverted[str(i)], "confidence": float(pred)} for i, pred in enumerate(list(preds))]
    # return {"top": top_pred, "predictions": labeled_preds}

    # with custom encoder class for numpy
    top_pred = {"label": legend_inverted[str(top_idx)], "confidence": preds[top_idx]}
    labeled_preds = [{"label": legend_inverted[str(i)], "confidence": pred} for i, pred in enumerate(list(preds))]
    return json.loads(json.dumps({"top": top_pred, "predictions": labeled_preds}, cls=NumpyEncoder))

# we want the query to be something we pass in whichi would be a url parameter e.g. /?q=this is awesome
# the input has to be q we can't name it arbitrarily string etc.
@app.get("/")
def read_index(q: Optional[str]=None):
    global ML_MODEL, TOKENIZER, METADATA
    query = q or "hello world"
    predictions = predict(query)
    return {"query": query, "results": predictions}