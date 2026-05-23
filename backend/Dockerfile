ARG DOCKER_REGISTRY=docker.arvancloud.ir
ARG DOCKER_OFFICIAL_NAMESPACE=library
FROM ${DOCKER_REGISTRY}/${DOCKER_OFFICIAL_NAMESPACE}/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
ARG PIP_INDEX_URL=https://pypi.devneeds.ir/simple/
RUN pip install --no-cache-dir --index-url "${PIP_INDEX_URL}" -r /app/requirements.txt

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
