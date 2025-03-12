FROM python:3.11-slim 

WORKDIR /app

# Copy only necessary files
COPY pyproject.toml uv.lock full-report.py ./

COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv

# Install dependencies using uv
RUN /bin/uv sync
RUN /bin/uv install streamlit pandas plotly pymongo python-dotenv

# Set non-sensitive environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Sensitive environment variables (MONGODB_URI, MONGODB_DATABASE) 
# will be set in Google Cloud Run's configuration

CMD streamlit run full-report.py --server.port=$PORT --server.address=0.0.0.0

