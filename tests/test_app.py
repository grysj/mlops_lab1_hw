import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.models.sentiment import PredictRequest, PredictResponse
from app import app
from inference import CLASSES, load_clf, load_sentence_transformer, predict


SAMPLE_TEXTS = [
    "I love this product, it works perfectly!",
    "This is the worst experience I have ever had.",
    "The package arrived on Tuesday.",
]


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def clf():
    return load_clf()


@pytest.fixture(scope="module")
def sentence_transformer():
    return load_sentence_transformer()


# Input validation


@pytest.mark.parametrize("text", ["hello", "  padded  ", "a"])
def test_request_accepts_non_empty_string(text):
    assert PredictRequest(text=text).text == text.strip()


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_request_rejects_empty_string(text):
    with pytest.raises(ValidationError):
        PredictRequest(text=text)


@pytest.mark.parametrize("text", [None, 123, ["a"], {"a": 1}])
def test_request_rejects_non_string(text):
    with pytest.raises(ValidationError):
        PredictRequest(text=text)


def test_request_requires_text_field():
    with pytest.raises(ValidationError):
        PredictRequest()


# Model loading and inference


def test_classifier_loads(clf):
    assert hasattr(clf, "predict")


def test_sentence_transformer_loads(sentence_transformer):
    assert hasattr(sentence_transformer, "encode")


@pytest.mark.parametrize("text", SAMPLE_TEXTS)
def test_inference_returns_known_class(sentence_transformer, clf, text):
    assert predict(sentence_transformer, clf, text) in CLASSES.values()


# Response validation


def test_response_model_accepts_string():
    assert PredictResponse(prediction="positive").prediction == "positive"


def test_response_model_rejects_missing_prediction():
    with pytest.raises(ValidationError):
        PredictResponse()


# Endpoint


@pytest.mark.parametrize("text", SAMPLE_TEXTS)
def test_predict_endpoint_returns_valid_json(client, text):
    response = client.post("/predict", json={"text": text})

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    body = response.json()
    assert set(body) == {"prediction"}
    assert body["prediction"] in CLASSES.values()
    PredictResponse.model_validate(body)


@pytest.mark.parametrize(
    "payload",
    [{"text": ""}, {"text": "   "}, {"text": 5}, {"text": None}, {}, {"txt": "hello"}],
)
def test_predict_endpoint_invalid_input_returns_error_json(client, payload):
    response = client.post("/predict", json=payload)

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"
    detail = response.json()["detail"]
    assert isinstance(detail, list) and detail
    for error in detail:
        assert error["msg"]
        assert error["loc"][0] == "body"


def test_predict_endpoint_rejects_get(client):
    assert client.get("/predict").status_code == 405
