# Activist OS API — Azure Container Apps image.
# Unlike insult-ai, this API is pure Python: stub agents run in-process and
# BandTransport speaks REST (thenvoi client) — no claude CLI, no conda.
# Build from the api/ dir:  docker build -t activist-os-api api/
FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
RUN chmod +x /app/entrypoint.sh

# Non-root user — house pattern from insult-ai.
RUN useradd --create-home --shell /bin/bash --uid 10001 runner \
 && chown -R runner:runner /app /home/runner
USER runner
ENV HOME=/home/runner

EXPOSE 8000
CMD ["/app/entrypoint.sh"]
