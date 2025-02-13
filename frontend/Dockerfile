# Stage 1: Build the frontend with Vite
FROM node:18 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . . 
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:latest AS production
# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf
# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Create a script to fix permissions and MIME types
RUN echo $'\n\
#!/bin/sh\n\
find /usr/share/nginx/html -type f -name "*.js" -exec chmod 644 {} \\;\n\
find /usr/share/nginx/html -type f -name "*.js" -exec sh -c '\''echo "Setting MIME type for {}"; chown nginx:nginx {}'\'' \\;\n\
nginx -g "daemon off;"\n\
' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

EXPOSE 80
CMD ["/docker-entrypoint.sh"]