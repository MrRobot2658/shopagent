FROM nginx:alpine

# Routing config (also mounted by docker-compose for live edits).
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static site is mounted at /usr/share/nginx/html by docker-compose.
EXPOSE 80
