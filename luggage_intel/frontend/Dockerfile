# SmartBuy AI -- frontend (React + Vite), built as a static site and served by nginx.
# Build context must be the frontend/ folder:
#   docker build --build-arg VITE_API_URL=https://your-backend-url -t smartbuy-frontend .
#
# IMPORTANT: Vite bakes VITE_API_URL into the JS bundle at BUILD time, not at
# container start time. If your backend URL changes, you must rebuild this
# image with the new --build-arg -- restarting the container is not enough.

FROM node:20-alpine AS build
WORKDIR /app

# Install deps first so this layer is cached unless package*.json changes
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# ---- serve stage ----
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
