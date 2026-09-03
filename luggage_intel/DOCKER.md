# Docker images

Two images, one per service. Both are built from the `luggage_intel/` folder layout described in the main README.

```
luggage_intel/
├── backend/Dockerfile
├── frontend/Dockerfile
├── frontend/nginx.conf
├── docker-compose.yml
└── .dockerignore
```

## Build the images

Run these from inside `luggage_intel/`.

**Backend** (build context is `luggage_intel/`, not `backend/`, because `requirements.txt` lives one level above the Dockerfile):

```bash
docker build -f backend/Dockerfile -t smartbuy-backend:latest .
```

**Frontend** (build context is `frontend/`). Vite bakes the backend URL into the JS bundle at *build* time, so pass it as a build arg — point it at wherever the backend image ends up running:

```bash
cd frontend
docker build --build-arg VITE_API_URL=https://your-backend-url.example.com -t smartbuy-frontend:latest .
cd ..
```

If you skip `--build-arg VITE_API_URL`, the bundle falls back to `http://localhost:5000`, which only works if both containers are running on your own machine.

## Run locally

```bash
docker run --env-file .env -p 5000:5000 smartbuy-backend:latest
docker run -p 8080:80 smartbuy-frontend:latest
```

Or bring both up together (this also handles the `VITE_API_URL` build arg for you):

```bash
docker compose up --build
```

Frontend: `http://localhost:8080` — Backend: `http://localhost:5000`

Either way, the backend still needs `SERPAPI_KEY` (and optionally `GROQ_API_KEY`) available at runtime — via `.env` (docker run --env-file / docker-compose's `env_file`) or via whatever env-var mechanism your host platform uses. Never bake these into the image itself.

## Push to a registry, so any platform can deploy the image directly

```bash
docker tag smartbuy-backend:latest <your-dockerhub-username>/smartbuy-backend:latest
docker push <your-dockerhub-username>/smartbuy-backend:latest

docker tag smartbuy-frontend:latest <your-dockerhub-username>/smartbuy-frontend:latest
docker push <your-dockerhub-username>/smartbuy-frontend:latest
```

(Docker Hub's free tier works fine for this; GitHub Container Registry — `ghcr.io` — is another common free option.)

## Deploying these images

Most platforms that run containers (Render, Railway, Fly.io, a VPS, etc.) support either: **point at your GitHub repo and a Dockerfile path** (no registry push needed — the platform builds the image itself from `backend/Dockerfile` / `frontend/Dockerfile`), or **point at an already-pushed image** from the registry step above. Either way, the required env vars are the same regardless of platform:

- Backend service: `SERPAPI_KEY` (required for real data), `GROQ_API_KEY` (optional, review sentiment tester)
- Frontend build: `VITE_API_URL` set to wherever the backend ends up publicly reachable

Whichever platform you land on next, these two images are the deployable unit — happy to walk through wiring up the specific platform whenever you're ready.
