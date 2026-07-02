FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# NEXT_PUBLIC_* vars are inlined into the client bundle at build time
ARG NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build the application
RUN npm run build

# Expose port
EXPOSE 3001

# Start the application
CMD ["npm", "start"]
