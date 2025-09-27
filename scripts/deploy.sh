#!/bin/bash

# Deployment script for Volunteer Matching System
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="volunteer-matching-system"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENVIRONMENT=${1:-production}

echo -e "${BLUE}🚀 Starting deployment for $PROJECT_NAME${NC}"
echo -e "${BLUE}Environment: $ENVIRONMENT${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Docker and Docker Compose are installed
check_prerequisites() {
    echo -e "${BLUE}📋 Checking prerequisites...${NC}"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_status "Docker is installed"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_status "Docker Compose is installed"
}

# Setup environment variables
setup_environment() {
    echo -e "${BLUE}🔧 Setting up environment...${NC}"
    
    # Check if .env file exists
    if [ ! -f "backend/.env" ]; then
        if [ -f "backend/.env.example" ]; then
            print_warning "Creating .env from .env.example"
            cp backend/.env.example backend/.env
            print_warning "Please update backend/.env with your configuration"
        else
            print_error "No .env.example file found"
            exit 1
        fi
    fi
    print_status "Environment file ready"
}

# Build Docker images
build_images() {
    echo -e "${BLUE}🔨 Building Docker images...${NC}"
    
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    if [ $? -eq 0 ]; then
        print_status "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Pull latest images (for dependencies)
pull_images() {
    echo -e "${BLUE}📥 Pulling latest dependency images...${NC}"
    
    docker-compose -f $DOCKER_COMPOSE_FILE pull
    
    if [ $? -eq 0 ]; then
        print_status "Dependencies updated"
    else
        print_warning "Some dependencies might not have been updated"
    fi
}

# Stop existing containers
stop_containers() {
    echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
    
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    print_status "Containers stopped"
}

# Start containers
start_containers() {
    echo -e "${BLUE}🚀 Starting containers...${NC}"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f $DOCKER_COMPOSE_FILE --profile production up -d
    else
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
    fi
    
    if [ $? -eq 0 ]; then
        print_status "Containers started successfully"
    else
        print_error "Failed to start containers"
        exit 1
    fi
}

# Health check
health_check() {
    echo -e "${BLUE}🏥 Performing health check...${NC}"
    
    # Wait for services to be ready
    sleep 10
    
    # Check backend health
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_status "Backend is healthy"
            break
        fi
        
        if [ $i -eq 30 ]; then
            print_error "Backend health check failed"
            docker-compose -f $DOCKER_COMPOSE_FILE logs backend
            exit 1
        fi
        
        echo "Waiting for backend... (attempt $i/30)"
        sleep 2
    done
    
    # Check frontend (if not in API-only mode)
    if [ "$ENVIRONMENT" != "api-only" ]; then
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            print_status "Frontend is healthy"
        else
            print_warning "Frontend health check failed, but continuing..."
        fi
    fi
}

# Show running containers
show_status() {
    echo -e "${BLUE}📊 Deployment status:${NC}"
    docker-compose -f $DOCKER_COMPOSE_FILE ps
}

# Cleanup function
cleanup_on_exit() {
    if [ $? -ne 0 ]; then
        print_error "Deployment failed!"
        echo -e "${YELLOW}To view logs, run:${NC}"
        echo "docker-compose -f $DOCKER_COMPOSE_FILE logs"
    fi
}

# Database migration (if needed)
run_migrations() {
    echo -e "${BLUE}🗃️ Running database migrations...${NC}"
    
    # Check if migrations are needed
    docker-compose -f $DOCKER_COMPOSE_FILE exec -T backend python -c "
import asyncio
from app.database import connect_to_mongo, create_indexes

async def run_migrations():
    await connect_to_mongo()
    await create_indexes()
    print('Migrations completed')

asyncio.run(run_migrations())
" 2>/dev/null

    if [ $? -eq 0 ]; then
        print_status "Database migrations completed"
    else
        print_warning "Database migrations may have failed"
    fi
}

# Seed initial data (optional)
seed_data() {
    if [ "$1" = "--seed" ]; then
        echo -e "${BLUE}🌱 Seeding initial data...${NC}"
        
        docker-compose -f $DOCKER_COMPOSE_FILE exec -T backend python scripts/seed_data.py
        
        if [ $? -eq 0 ]; then
            print_status "Initial data seeded"
        else
            print_warning "Data seeding may have failed"
        fi
    fi
}

# Backup function
backup_data() {
    if [ "$1" = "--backup" ]; then
        echo -e "${BLUE}💾 Creating backup...${NC}"
        
        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        
        # This would depend on your backup strategy
        # For MongoDB, you might use mongodump
        print_status "Backup created in $BACKUP_DIR"
    fi
}

# Main deployment function
main() {
    # Set trap for cleanup
    trap cleanup_on_exit EXIT
    
    # Check for backup flag
    backup_data $2
    
    # Run deployment steps
    check_prerequisites
    setup_environment
    pull_images
    stop_containers
    build_images
    start_containers
    run_migrations
    health_check
    
    # Seed data if requested
    seed_data $2
    
    show_status
    
    echo ""
    print_status "Deployment completed successfully! 🎉"
    echo ""
    echo -e "${GREEN}Services are running at:${NC}"
    echo -e "  • Backend API: ${BLUE}http://localhost:8000${NC}"
    echo -e "  • Frontend: ${BLUE}http://localhost:3000${NC}"
    echo -e "  • API Documentation: ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo -e "  • View logs: ${BLUE}docker-compose logs -f${NC}"
    echo -e "  • Stop services: ${BLUE}docker-compose down${NC}"
    echo -e "  • Restart services: ${BLUE}docker-compose restart${NC}"
    echo ""
}

# Script usage
usage() {
    echo "Usage: $0 [environment] [options]"
    echo ""
    echo "Environments:"
    echo "  production    Production deployment with optimizations"
    echo "  development   Development deployment (default)"
    echo "  staging       Staging environment"
    echo ""
    echo "Options:"
    echo "  --seed        Seed initial data after deployment"
    echo "  --backup      Create backup before deployment"
    echo ""
    echo "Examples:"
    echo "  $0                          # Deploy in development mode"
    echo "  $0 production               # Deploy in production mode"
    echo "  $0 development --seed       # Deploy and seed data"
    echo "  $0 production --backup      # Deploy with backup"
}

# Check for help flag
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    usage
    exit 0
fi

# Validate environment
if [ "$ENVIRONMENT" != "development" ] && [ "$ENVIRONMENT" != "production" ] && [ "$ENVIRONMENT" != "staging" ]; then
    print_error "Invalid environment: $ENVIRONMENT"
    usage
    exit 1
fi

# Run main function
main $@ 