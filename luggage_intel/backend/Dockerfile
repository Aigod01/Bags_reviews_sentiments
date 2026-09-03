# SmartBuy AI -- backend (FastAPI)
# Build context must be the luggage_intel/ folder (not backend/), since
# requirements.txt lives one level above this Dockerfile:
#   docker build -f backend/Dockerfile -t smartbuy-backend .
FROM python:3.12-slim

WORKDIR /app

# Install Python deps first so this layer is cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY backend/ ./backend/

# Render/Railway/etc inject $PORT at runtime; default to 5000 for local docker run
ENV PORT=5000
EXPOSE 5000

# Runs uvicorn against backend/main.py, same as local dev (`--app-dir backend`)
CMD ["sh", "-c", "uvicorn main:app --app-dir backend --host 0.0.0.0 --port ${PORT}"]
