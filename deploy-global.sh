#!/bin/bash

# Global Scaling Deployment Script
# This script orchestrates the deployment of the AI Heart Platform's global scaling infrastructure

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INFRASTRUCTURE_DIR="$PROJECT_ROOT/infrastructure"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Global Scaling Deployment Script

Usage: $0 [OPTIONS] COMMAND

Commands:
    init           Initialize global scaling infrastructure
    deploy         Deploy to specific region
    test           Run global scaling tests
    health         Check health of all regions
    failover       Test failover mechanisms
    cleanup        Clean up resources

Options:
    -r, --region REGION     Target AWS region (default: us-east-1)
    -e, --env ENV          Environment (dev/staging/production)
    -c, --config FILE      Custom configuration file
    -v, --verbose          Verbose output
    -h, --help             Show this help message

Examples:
    $0 init --region us-east-1
    $0 deploy --region eu-west-1 --env production
    $0 test --region all
    $0 health
    $0 failover --region us-east-1

Supported Regions:
    us-east-1      US East (Virginia) - Primary
    us-west-2      US West (Oregon)
    eu-west-1      Europe (Ireland)
    eu-central-1   Europe (Frankfurt)
    ap-southeast-1 Asia Pacific (Singapore)
    ap-northeast-1 Asia Pacific (Tokyo)
    me-south-1     Middle East (Bahrain)

EOF
}

# Parse command line arguments
REGION="us-east-1"
ENVIRONMENT="production"
CONFIG_FILE=""
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            log_error "Unknown option $1"
            show_help
            exit 1
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Validate region
VALID_REGIONS=("us-east-1" "us-west-2" "eu-west-1" "eu-central-1" "ap-southeast-1" "ap-northeast-1" "me-south-1")
if [[ ! " ${VALID_REGIONS[@]} " =~ " ${REGION} " ]] && [[ "$REGION" != "all" ]]; then
    log_error "Invalid region: $REGION"
    log_info "Valid regions: ${VALID_REGIONS[*]}"
    exit 1
fi

# Load configuration
load_config() {
    local region=$1
    local env_file="$INFRASTRUCTURE_DIR/environments/.env.$region"
    
    if [[ -f "$env_file" ]]; then
        log_info "Loading configuration for region: $region"
        set -a # automatically export all variables
        source "$env_file"
        set +a
        log_success "Configuration loaded from $env_file"
    else
        log_warning "Configuration file not found: $env_file"
        log_info "Using default configuration"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    local tools=("docker" "docker-compose" "curl" "jq")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    # Check optional tools
    local optional_tools=("terraform" "aws" "kubectl")
    for tool in "${optional_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_warning "$tool is not installed (optional but recommended)"
        fi
    done
    
    # Check Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        exit 1
    fi
    
    log_success "Prerequisites check completed"
}

# Initialize infrastructure
init_infrastructure() {
    log_info "Initializing global scaling infrastructure..."
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/data"
    mkdir -p "$PROJECT_ROOT/ssl"
    
    # Copy configuration files
    if [[ -n "$CONFIG_FILE" ]] && [[ -f "$CONFIG_FILE" ]]; then
        log_info "Using custom configuration: $CONFIG_FILE"
        cp "$CONFIG_FILE" "$PROJECT_ROOT/.env"
    else
        load_config "$REGION"
    fi
    
    # Initialize Terraform if available
    if command -v terraform &> /dev/null && [[ -d "$INFRASTRUCTURE_DIR/terraform" ]]; then
        log_info "Initializing Terraform..."
        cd "$INFRASTRUCTURE_DIR/terraform"
        terraform init
        cd "$PROJECT_ROOT"
        log_success "Terraform initialized"
    fi
    
    log_success "Infrastructure initialization completed"
}

# Deploy to region
deploy_region() {
    local target_region=$1
    log_info "Deploying to region: $target_region"
    
    # Load region-specific configuration
    load_config "$target_region"
    
    # Deploy with Docker Compose
    log_info "Starting Docker Compose deployment..."
    
    # Set environment variables for Docker Compose
    export AWS_REGION="$target_region"
    export ENVIRONMENT="$ENVIRONMENT"
    
    # Start services
    docker-compose -f docker-compose.global.yml up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    local max_wait=300
    local wait_time=0
    
    while [[ $wait_time -lt $max_wait ]]; do
        if check_service_health "http://localhost:5000/api/health"; then
            log_success "Services are healthy"
            break
        fi
        sleep 10
        wait_time=$((wait_time + 10))
        log_info "Waiting... ($wait_time/$max_wait seconds)"
    done
    
    if [[ $wait_time -ge $max_wait ]]; then
        log_error "Services did not become healthy within $max_wait seconds"
        return 1
    fi
    
    log_success "Deployment to $target_region completed successfully"
}

# Check service health
check_service_health() {
    local url=$1
    local response
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null)
    
    if [[ "$response" == "200" ]]; then
        return 0
    else
        return 1
    fi
}

# Run tests
run_tests() {
    log_info "Running global scaling tests..."
    
    # Check if Python and pytest are available
    if command -v python &> /dev/null; then
        if python -c "import pytest" 2>/dev/null; then
            python -m pytest tests/test_global_scaling.py -v
        else
            log_warning "pytest not available, running basic curl tests"
            run_basic_tests
        fi
    else
        log_warning "Python not available, running basic curl tests"
        run_basic_tests
    fi
}

# Basic health tests using curl
run_basic_tests() {
    log_info "Running basic health tests..."
    
    local endpoints=(
        "http://localhost:5000/api/health"
        "http://localhost:5000/api/health/readiness"
        "http://localhost:5000/api/health/liveness"
    )
    
    for endpoint in "${endpoints[@]}"; do
        log_info "Testing endpoint: $endpoint"
        if check_service_health "$endpoint"; then
            log_success "✓ $endpoint is healthy"
        else
            log_error "✗ $endpoint is not responding"
        fi
    done
}

# Check health of all regions
check_all_health() {
    log_info "Checking health of all regions..."
    
    # This would check health across all deployed regions
    # For now, we'll check the local deployment
    local services=("backend" "frontend" "db" "redis")
    
    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.global.yml ps "$service" | grep -q "Up"; then
            log_success "✓ $service is running"
        else
            log_error "✗ $service is not running"
        fi
    done
    
    # Check application health
    run_basic_tests
}

# Test failover mechanisms
test_failover() {
    local region=$1
    log_info "Testing failover mechanisms for region: $region"
    
    # This would simulate failure scenarios and test failover
    log_warning "Failover testing is not implemented in this demo"
    log_info "In production, this would:"
    log_info "  - Simulate service failures"
    log_info "  - Test database failover"
    log_info "  - Verify traffic routing"
    log_info "  - Check recovery procedures"
}

# Cleanup resources
cleanup_resources() {
    log_info "Cleaning up resources..."
    
    # Stop Docker Compose services
    docker-compose -f docker-compose.global.yml down -v
    
    # Remove unused Docker resources
    docker system prune -f
    
    log_success "Cleanup completed"
}

# Main execution
main() {
    log_info "Global Scaling Deployment Script"
    log_info "Command: ${COMMAND:-none}"
    log_info "Region: $REGION"
    log_info "Environment: $ENVIRONMENT"
    echo
    
    case "${COMMAND:-}" in
        init)
            check_prerequisites
            init_infrastructure
            ;;
        deploy)
            check_prerequisites
            if [[ "$REGION" == "all" ]]; then
                for region in "${VALID_REGIONS[@]}"; do
                    deploy_region "$region"
                done
            else
                deploy_region "$REGION"
            fi
            ;;
        test)
            run_tests
            ;;
        health)
            check_all_health
            ;;
        failover)
            test_failover "$REGION"
            ;;
        cleanup)
            cleanup_resources
            ;;
        "")
            log_error "No command specified"
            show_help
            exit 1
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"