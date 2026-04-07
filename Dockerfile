FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

COPY pyproject.toml uv.lock .python-version /app/

RUN uv sync

COPY . /app/

CMD [ "uv", "run", "src/main.py" ]