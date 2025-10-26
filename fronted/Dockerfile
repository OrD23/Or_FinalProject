# Stage 1: Build the React app using the specified Node version.
FROM node:23.9.0-alpine3.20 AS build

WORKDIR /app

# Copy package files and install dependencies.
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the code and build the app.
COPY . .
RUN npm run build

# Stage 2: Serve the built app with Nginx.
FROM nginx:stable-alpine

# Remove default Nginx static assets.
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from the previous stage.
COPY --from=build /app/build /usr/share/nginx/html

# Copy your custom nginx configuration file.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
