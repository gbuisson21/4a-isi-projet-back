# ---- Build ----
FROM python:3.15.2-slim-trixie AS builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Runtime ----
FROM python:3.15.2-slim-trixie
LABEL authors="sacha"
EXPOSE 8000

RUN useradd --create-home --shell /bin/bash api
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY --chown=api:api . .
USER api

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]