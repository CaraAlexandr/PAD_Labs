FROM node:14-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Install NestJS CLI globally in the container
RUN npm install -g @nestjs/cli

# Copy the rest of the application files
COPY . .

# Build the NestJS application
RUN npm run build

# Command to start the application
CMD ["npm", "run", "start:prod"]
