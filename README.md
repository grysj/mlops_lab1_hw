# mlops_lab1_hw
<<<<<<< HEAD

## Run with Docker Compose

Build and start the inference API with:

```bash
docker compose up --build
```

The API is available at <http://localhost:8000>. For example:

```bash
curl -X POST http://localhost:8000/predict \
  -H 'content-type: application/json' \
  -d '{"text":"I love this product"}'
```

The Docker image includes the application dependencies and the local models
under `models/`.
=======
>>>>>>> a62eeff (lab01_hw_done)
