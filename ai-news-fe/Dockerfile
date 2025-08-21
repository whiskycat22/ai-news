# -----------------------
# Stage 1: Build
# -----------------------
FROM node:20-alpine AS builder

# Install build dependencies
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Update npm
RUN npm install -g npm@latest

# Copy package files first for caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install --legacy-peer-deps --verbose

# Copy source code
COPY . .

# Build-time ARG
ARG NEWS_AGENT_URL
ENV NEWS_AGENT_URL=$NEWS_AGENT_URL

# Build Next.js app
RUN npm run build

# -----------------------
# Stage 2: Production
# -----------------------
FROM node:20-alpine AS runner

WORKDIR /app

# Copy only production files
COPY --from=builder /app/package.json /app/package-lock.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Set environment variable for Cloud Run port
ENV PORT=8080
EXPOSE 8080

# Start app
CMD ["npm", "run", "start"]
