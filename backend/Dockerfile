# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S magi -u 1001

# Copy built application
COPY --from=builder --chown=magi:nodejs /app/dist ./dist
COPY --from=builder --chown=magi:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=magi:nodejs /app/package*.json ./

# Create necessary directories
RUN mkdir -p logs data && chown magi:nodejs logs data

# Switch to non-root user
USER magi

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:5000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

EXPOSE 5000

CMD ["node", "dist/index.js"]
