import json
import numpy as np
from typing import Optional, List
from pathlib import Path
from dataclasses import dataclass

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences

from . import encoders

# is its recommended to create many get functions like this to have
# one function deal with only a single thing (single concern priciple)

# we can also make our own exception here
class NotImplemented(Exception):
    pass

@dataclass
class MLModel:
    model_path: Path
    tokenizer_path: Optional[Path] = None
    metadata_path: Optional[Path] = None

    model = None
    tokenizer = None
    metadata = None

    def __post_init__(self):
        if self.model_path.exists():
            self.model = load_model(self.model_path)
        if self.tokenizer_path and self.tokenizer_path.exists():
            if self.tokenizer_path.name.endswith("json"):
                tokenizer_text = self.tokenizer_path.read_text()
                self.tokenizer = tokenizer_from_json(tokenizer_text)
        if self.metadata_path and self.metadata_path.exists():
            if self.metadata_path.name.endswith("json"):
                self.metadata = json.loads(self.metadata_path.read_text())

    def get_model(self):
        if not self.model:
            raise Exception("Model not implemented")
        return self.model
    
    def get_tokenizer(self):
        if not self.tokenizer:
            raise Exception("Tokenizer not implemented")
        return self.tokenizer
    
    def get_metadata(self):
        if not self.metadata:
            raise Exception("Metadata not implemented")
        return self.metadata

    def get_sequences_from_texts(self, texts: List[str]):
        tokenizer = self.get_tokenizer()
        sequences = tokenizer.texts_to_sequences(texts)
        return sequences
    
    def get_input_from_sequences(self, sequences):
        maxlen = self.get_metadata().get("max_sequence_length")
        return pad_sequences(sequences, maxlen=maxlen)

    def get_label_legend_inverted(self):
        # will raise exception here if legend doesn't exist
        return self.get_metadata().get("label_legend_inverted")

    def get_label_pred(self, idx, pred):
        legend = self.get_label_legend_inverted()
        return {"label": legend[str(idx)], "confidence": pred}

    def get_top_pred_labeled(self, preds):
        top_idx= np.argmax(preds)
        return self.get_label_pred(top_idx, preds[top_idx])

    def predict_text(self, query: str, include_top=True, encode_to_json=True):
        model = self.get_model()
        sequences = self.get_sequences_from_texts([query])
        inputs = self.get_input_from_sequences(sequences)
        preds = model.predict(inputs)[0]
        labeled_preds = [self.get_label_pred(idx, pred) for idx, pred in enumerate(list(preds))]
        results = {
            "predictions": labeled_preds
        }
        if include_top:
            results["top"] = self.get_top_pred_labeled(preds)
        if encode_to_json:
            results = encoders.encode_to_json(results, as_py=True)
        return results
