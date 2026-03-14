# Create React App - dev server only (no build). Source mounted from host.
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Source is mounted via docker-compose volume
EXPOSE 3000
ENV HOST=0.0.0.0
ENV PORT=3000
ENV BROWSER=none
CMD ["npm", "start"]
