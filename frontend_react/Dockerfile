# Build Stage (Compile React to raw HTML/JS/CSS)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production Stage (Serve via NGINX)
FROM nginx:alpine
# Copy compiled static assets into Nginx hosting bay
COPY --from=build /app/dist /usr/share/nginx/html

# Replace the default nginx config to handle SPA routing natively (no 404s on refresh)
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
