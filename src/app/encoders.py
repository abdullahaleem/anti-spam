import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """
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
    
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def encode_to_json(data, as_py=True):
    encoded = json.dumps(data, cls=NumpyEncoder)
    if as_py:
        return json.loads(encoded)
    return encoded