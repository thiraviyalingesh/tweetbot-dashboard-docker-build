FROM python:3.11-slim 

WORKDIR /app

COPY . /app

COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv

RUN /bin/uv sync
RUN /bin/uv add streamlit
RUN /bin/uv add pandas plotly pymongo python-dotenv

# Set environment variables
ENV PYTHONPATH=/app
ENV MONGODB_URI=mongodb://localhost:27017
ENV MONGODB_DATABASE=twitter_actions

# Expose port
EXPOSE 8501

RUN bash -c "source /app/.venv/bin/activate && export PATH=\"/app/.venv/bin:\$PATH\""

# Change the ENTRYPOINT to bash
ENTRYPOINT ["/bin/bash", "-c"]

# Corrected CMD instruction
CMD ["source /app/.venv/bin/activate && exec streamlit run full-report.py --server.port=8501 --server.address=0.0.0.0"]