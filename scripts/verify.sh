#!/bin/bash

# CI/CD Health Dashboard API Verification Script
# This script verifies that all backend API endpoints are working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_BASE="http://localhost:8000"
API_KEY="${API_WRITE_KEY:-dev-write-key-change-in-production}"
HEALTH_ENDPOINT="$API_BASE/health"
SEED_ENDPOINT="$API_BASE/api/seed"
METRICS_ENDPOINT="$API_BASE/api/metrics/summary"
BUILDS_ENDPOINT="$API_BASE/api/builds?limit=5"

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $message"
    else
        echo -e "${RED}❌ FAIL${NC}: $message"
        exit 1
    fi
}

# Function to check if jq is available
check_jq() {
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  Warning: jq is not installed. JSON responses will not be formatted.${NC}"
        echo "   Install jq with: brew install jq (macOS) or apt-get install jq (Ubuntu)"
        JQ_AVAILABLE=false
    else
        JQ_AVAILABLE=true
    fi
}

# Function to format JSON response
format_json() {
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$1" | jq .
    else
        echo "$1"
    fi
}

echo "🔍 CI/CD Health Dashboard API Verification"
echo "=========================================="
echo "API Base URL: $API_BASE"
echo "API Key: $API_KEY"
echo ""

# Check if jq is available
check_jq
echo ""

# Test 1: Health Check
echo "1️⃣  Testing Health Check Endpoint..."
echo "   GET $HEALTH_ENDPOINT"
if response=$(curl -s -f "$HEALTH_ENDPOINT" 2>/dev/null); then
    if echo "$response" | grep -q '"ok": true'; then
        print_status "PASS" "Health check endpoint is responding correctly"
        echo "   Response: $response"
    else
        print_status "FAIL" "Health check response format is incorrect"
        echo "   Response: $response"
        exit 1
    fi
else
    print_status "FAIL" "Health check endpoint is not accessible"
    echo "   Make sure the backend is running on port 8000"
    exit 1
fi
echo ""

# Test 2: Database Seeding
echo "2️⃣  Testing Database Seeding..."
echo "   POST $SEED_ENDPOINT"
if response=$(curl -s -f -H "X-API-KEY: $API_KEY" -X POST "$SEED_ENDPOINT" -d '{}' 2>/dev/null); then
    if echo "$response" | grep -q '"success": true'; then
        print_status "PASS" "Database seeding completed successfully"
        echo "   Response: $response"
    else
        print_status "FAIL" "Database seeding failed"
        echo "   Response: $response"
        exit 1
    fi
else
    print_status "FAIL" "Database seeding endpoint is not accessible"
    echo "   Make sure the backend is running and the API key is correct"
    exit 1
fi
echo ""

# Test 3: Metrics Summary
echo "3️⃣  Testing Metrics Summary Endpoint..."
echo "   GET $METRICS_ENDPOINT"
if response=$(curl -s -f "$METRICS_ENDPOINT" 2>/dev/null); then
    if echo "$response" | grep -q '"window_days"'; then
        print_status "PASS" "Metrics summary endpoint is responding correctly"
        echo "   Response:"
        format_json "$response"
    else
        print_status "FAIL" "Metrics summary response format is incorrect"
        echo "   Response: $response"
        exit 1
    fi
else
    print_status "FAIL" "Metrics summary endpoint is not accessible"
    echo "   Make sure the backend is running on port 8000"
    exit 1
fi
echo ""

# Test 4: Builds List
echo "4️⃣  Testing Builds List Endpoint..."
echo "   GET $BUILDS_ENDPOINT"
if response=$(curl -s -f "$BUILDS_ENDPOINT" 2>/dev/null); then
    if echo "$response" | grep -q '"builds"'; then
        print_status "PASS" "Builds list endpoint is responding correctly"
        echo "   Response:"
        format_json "$response"
    else
        print_status "FAIL" "Builds list response format is incorrect"
        echo "   Response: $response"
        exit 1
    fi
else
    print_status "FAIL" "Builds list endpoint is not accessible"
    echo "   Make sure the backend is running on port 8000"
    exit 1
fi
echo ""

# All tests passed
echo "🎉 All API verification tests PASSED!"
echo ""
echo "✅ Backend API is working correctly"
echo "✅ Database seeding is functional"
echo "✅ Metrics endpoint is responding"
echo "✅ Builds endpoint is accessible"
echo ""
echo "🚀 Your CI/CD Health Dashboard is ready to use!"
echo "   Frontend: http://localhost:5173 (dev) or http://localhost:8080 (prod)"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
