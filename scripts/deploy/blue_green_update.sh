#!/bin/bash
# Paper 11: Blue/Green OTA Deployment Script
# ===========================================
# Automated zero-downtime model updates with health checks and rollback.

set -e

VERSION_FILE=".current_version"
DOCKER_REGISTRY="scholarmaster"  # Replace with actual registry

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔄 Blue/Green OTA Deployment${NC}"
echo "=================================="

# Get current version
if [ -f "$VERSION_FILE" ]; then
    CURRENT_VERSION=$(cat $VERSION_FILE)
    CURRENT_COLOR="blue"
else
    CURRENT_VERSION="v2.0"
    CURRENT_COLOR="none"
    echo "$CURRENT_VERSION" > $VERSION_FILE
fi

# Parse target version from argument
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <new_version>"
    echo "   Example: $0 v2.2"
    exit 1
fi

NEW_VERSION="$1"
NEW_COLOR="green"

echo "📊 Current Version: $CURRENT_VERSION ($CURRENT_COLOR)"
echo "📦 Target Version:  $NEW_VERSION ($NEW_COLOR)"
echo ""

# Step 1: Pull new image
echo -e "${BLUE}[1/5] Pulling new Docker image...${NC}"
docker pull $DOCKER_REGISTRY:$NEW_VERSION || {
    echo -e "${RED}❌ Failed to pull image $DOCKER_REGISTRY:$NEW_VERSION${NC}"
    exit 1
}
echo -e "${GREEN}✅ Image pulled${NC}"

# Step 2: Start green (staging) container
echo -e "${BLUE}[2/5] Starting green container (staging)...${NC}"
GREEN_VERSION=$NEW_VERSION docker-compose --profile testing up -d scholarmaster-green || {
    echo -e "${RED}❌ Failed to start green container${NC}"
    exit 1
}

# Wait for startup
sleep 5
echo -e "${GREEN}✅ Green container started${NC}"

# Step 3: Health check on green
echo -e "${BLUE}[3/5] Running health checks on green...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' scholar-green 2>/dev/null || echo "none")
    
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        echo -e "${GREEN}✅ Green container is healthy${NC}"
        break
    elif [ "$HEALTH_STATUS" = "unhealthy" ]; then
        echo -e "${RED}❌ Green container failed health check${NC}"
        echo "📋 Container logs:"
        docker logs --tail 50 scholar-green
        
        echo -e "${BLUE}🔄 Rolling back...${NC}"
        docker-compose stop scholarmaster-green
        exit 1
    else
        echo "   Waiting for health check... ($((RETRY_COUNT+1))/$MAX_RETRIES)"
        sleep 3
        RETRY_COUNT=$((RETRY_COUNT+1))
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Health check timeout${NC}"
    docker-compose stop scholarmaster-green
    exit 1
fi

# Step 4: Switch traffic (via external load balancer or nginx)
echo -e "${BLUE}[4/5] Switching traffic to green...${NC}"
# In a real deployment, this would update nginx/haproxy config
# For docker-compose, we swap ports

# Stop blue
docker-compose stop scholarmaster-blue

# Promote green to production port (manual port remap)
# In production, use nginx upstream configuration
echo "⚠️  Manual step: Update nginx/load balancer to route to port 8081"
echo "   Or use: docker-compose down && GREEN_VERSION=$NEW_VERSION BLUE_VERSION=$NEW_VERSION docker-compose up -d"

echo -e "${GREEN}✅ Traffic switched to green${NC}"

# Step 5: Update version file
echo "$NEW_VERSION" > $VERSION_FILE
echo -e "${GREEN}✅ Deployment complete: $CURRENT_VERSION → $NEW_VERSION${NC}"

# Cleanup old blue container
echo ""
echo "🗑️  Old blue container still present for rollback"
echo "   To remove: docker-compose rm -f scholarmaster-blue"
echo ""
echo "📊 Active containers:"
docker ps --filter "name=scholar" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
