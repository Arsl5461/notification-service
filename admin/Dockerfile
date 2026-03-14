# Admin: dev server only (no build). Source mounted from host.
FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

# Source is mounted via docker-compose volume
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
