FROM node:18-alpine

WORKDIR /app

# Install dependencies first (for better caching)
COPY package*.json ./
RUN npm install

# Copy frontend code
COPY . .

# Start development server
CMD ["npm", "run", "dev"]
