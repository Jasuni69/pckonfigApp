# Stage 1: Build the frontend with Vite
FROM node:18 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . . 
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:latest AS production
# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

EXPOSE 80
# Use the default nginx command
CMD ["nginx", "-g", "daemon off;"]