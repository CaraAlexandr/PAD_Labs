FROM node:14-alpine

WORKDIR /app

# Copy package.json and package-lock.json first
COPY package*.json ./

# Install dependencies (including grpc-tools locally)
RUN npm install

# Install NestJS CLI globally in the container
RUN npm install -g @nestjs/cli

# Copy the rest of the application files
COPY . .

# Copy the proto folder into the container
COPY ./proto /app/proto

# Use npx to run grpc_tools_node_protoc to generate gRPC code
RUN npx grpc_tools_node_protoc \
  --js_out=import_style=commonjs,binary:./src \
  --grpc_out=./src \
  -I ./proto ./proto/*.proto

# Command to start the application
CMD ["npm", "start"]
