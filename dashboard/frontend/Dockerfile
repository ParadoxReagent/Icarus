FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY public/ ./public/
COPY src/ ./src/

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
