# gateway/Dockerfile
FROM node:18-alpine

WORKDIR /usr/src/app

COPY package*.json ./

# Upgrade NPM to the latest version
RUN npm install -g npm@10.8.3

RUN npm install

COPY . .

# Build the project, which copies .proto files to dist/grpc/
RUN npm run build

# Verify that .proto files are present
RUN ls -la dist/grpc/

EXPOSE 3000

CMD ["node", "dist/main.js"]
