FROM node:14-alpine

WORKDIR /app

COPY package.json tsconfig*.json ./
COPY src ./src

# Install dependencies
RUN npm install

# Install NestJS CLI globally
RUN npm install -g @nestjs/cli

# Build the application
RUN npm run build

EXPOSE 3000

CMD ["node", "dist/main.js"]
