FROM python:3.11-slim 

WORKDIR /app

COPY . /app

COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv

RUN /bin/uv sync
RUN /bin/uv add streamlit
RUN /bin/uv add pandas plotly pymongo python-dotenv xlsxwriter

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Google Cloud Run sets PORT environment variable, default to 8080 if not set
ENV PORT=8080

RUN bash -c "source /app/.venv/bin/activate && export PATH=\"/app/.venv/bin:\$PATH\""

# Change the ENTRYPOINT to bash
ENTRYPOINT ["/bin/bash", "-c"]

# MongoDB credentials will be passed as environment variables at runtime
CMD ["source /app/.venv/bin/activate && exec streamlit run full-report.py --server.port=$PORT --server.address=0.0.0.0"]