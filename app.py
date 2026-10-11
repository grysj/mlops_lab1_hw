from fastapi import FastAPI

from api.models.sentiment import PredictRequest, PredictResponse
from inference import load_clf, load_sentence_transformer
from inference import predict as predict_sentiment

CLF = load_clf()
SENTENCE_TRANSFORMER = load_sentence_transformer()

app = FastAPI()


@app.post("/predict")
def predict(request: PredictRequest) -> PredictResponse:
    prediction = predict_sentiment(SENTENCE_TRANSFORMER, CLF, request.text)
    return PredictResponse(prediction=prediction)
