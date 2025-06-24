# Stage 1: Build
FROM node:18-alpine AS build-stage

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

ARG VUE_APP_BACKEND_HOSTNAME
ENV VUE_APP_BACKEND_HOSTNAME=$VUE_APP_BACKEND_HOSTNAME

COPY . .
RUN npm run build

# Production stage with nginx
FROM nginx:1.28.0-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Custom nginx config for SPA
COPY ./nginx.conf  /etc/nginx/conf.d/default.conf


EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]