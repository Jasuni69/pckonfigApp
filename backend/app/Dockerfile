FROM python:3.12

WORKDIR /app

# Copy requirements first for better caching
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy alembic files
COPY alembic.ini .
COPY alembic/ ./alembic/

# Copy ChromaDB directory
COPY ChromaDB/ ./ChromaDB/

# Copy the application code
COPY app/ .

# Add the parent directory to PYTHONPATH
ENV PYTHONPATH=/app

EXPOSE 8000

# Start FastAPI server
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
