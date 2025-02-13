# Stage 1: Build the frontend with Vite
FROM node:18 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . . 
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:latest AS production
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]