import joblib
from sentence_transformers import SentenceTransformer


CLASSES = {0: "negative", 1: "neutral", 2: "positive"}


def load_clf():

    with open("models/classifier.joblib", "rb") as f:
        clf = joblib.load(f)
    return clf


def load_sentence_transformer():
    return SentenceTransformer("models/sentence_transformer.model")


def predict(sentence_transformer, clf, text: str):
    embedding = sentence_transformer.encode([text])
    prediction = clf.predict(embedding)
    return CLASSES[prediction[0]]
