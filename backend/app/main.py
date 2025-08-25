from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
import time

from .db import init_db, get_db
from .models import Provider, Build, Alert, Settings, Metrics
from .schemas import (
    MetricsSummary, BuildListResponse, Build as BuildSchema,
    GitHubWebhookPayload,
    AlertTestRequest, AlertTestResponse, SeedRequest, SeedResponse,
    HealthResponse
)
from .alerts import alert_service
from .secret_manager import get_secret_or_env

# In-memory rate limiter store
_rate_limits = defaultdict(list)  # ip -> [timestamps]
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 60

# Security configuration
WRITE_KEY = get_secret_or_env("secret_key", "WRITE_KEY", "default-key-change-in-production")
print(f"🔑 Webhook authentication key: {WRITE_KEY[:8]}...{WRITE_KEY[-8:] if len(WRITE_KEY) > 16 else WRITE_KEY}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting CI/CD Health Dashboard...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down CI/CD Health Dashboard...")

app = FastAPI(
    title="CI/CD Health Dashboard API",
    description="API for monitoring CI/CD pipeline health using GitHub Actions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
try:
    # Try to mount frontend directory if it exists
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
    if os.path.exists(frontend_path):
        app.mount("/static", StaticFiles(directory=frontend_path), name="static")
        print(f"✅ Frontend mounted at /static from {frontend_path}")
    else:
        print(f"⚠️  Frontend directory not found at {frontend_path}")
except Exception as e:
    print(f"⚠️  Could not mount frontend: {e}")

# Authentication middleware for webhooks
async def verify_webhook_auth(request: Request):
    """Verify webhook authentication"""
    auth_header = request.headers.get("Authorization")
    print(f"🔍 Auth header: {auth_header}")
    print(f"🔑 Expected key: {WRITE_KEY}")
    
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )
    
    token = auth_header.split(" ")[1]
    print(f"🔑 Received token: {token}")
    
    if token != WRITE_KEY:
        print(f"❌ Token mismatch! Expected: {WRITE_KEY}, Got: {token}")
        raise HTTPException(
            status_code=403,
            detail="Invalid authorization token"
        )
    
    print("✅ Authentication successful")
    return True

@app.get("/")
async def root():
    """Serve the dashboard HTML"""
    try:
        # Try to serve the frontend index.html
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "index.html")
        if os.path.exists(frontend_path):
            return FileResponse(frontend_path)
        else:
            # Fallback to API info if frontend not found
            return {
                "message": "CI/CD Health Dashboard API",
                "version": "1.0.0",
                "docs": "/docs",
                "health": "/health",
                "note": "Frontend not found, serving API only"
            }
    except Exception as e:
        # Fallback to API info on error
        return {
            "message": "CI/CD Health Dashboard API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "error": f"Frontend error: {str(e)}"
        }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "ok": True,
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "database": "connected"
    }

@app.get("/api/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary(session: AsyncSession = Depends(get_db)):
    """Get dashboard summary metrics for the last 7 days"""
    try:
        # Calculate time window: last 7 days from now
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        
        # Get builds in the time window
        builds_query = select(Build).where(
            and_(
                Build.started_at >= seven_days_ago,
                Build.status.in_(["success", "failed", "running", "queued"])
            )
        )
        result = await session.execute(builds_query)
        builds = result.scalars().all()
        
        if not builds:
            return MetricsSummary(
                window_days=7,
                success_rate=0.0,
                failure_rate=0.0,
                avg_build_time_seconds=0.0,
                last_build_status="unknown",
                last_updated=now
            )
        
        # Calculate metrics
        total_builds = len(builds)
        successful_builds = len([b for b in builds if b.status == "success"])
        failed_builds = len([b for b in builds if b.status == "failed"])
        
        success_rate = successful_builds / total_builds if total_builds > 0 else 0.0
        failure_rate = failed_builds / total_builds if total_builds > 0 else 0.0
        
        # Calculate average build time (only for completed builds)
        completed_builds = [b for b in builds if b.duration_seconds is not None]
        avg_build_time = sum(b.duration_seconds for b in completed_builds) / len(completed_builds) if completed_builds else 0.0
        
        # Get last build status
        last_build = max(builds, key=lambda b: b.started_at) if builds else None
        last_build_status = last_build.status if last_build else "unknown"
        
        return MetricsSummary(
            window_days=7,
            success_rate=success_rate,
            failure_rate=failure_rate,
            avg_build_time_seconds=avg_build_time,
            last_build_status=last_build_status,
            last_updated=now
        )
        
    except Exception as e:
        print(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@app.get("/api/builds", response_model=BuildListResponse)
async def get_builds(
    session: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get list of builds with pagination"""
    try:
        # Get total count
        count_query = select(func.count(Build.id))
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Get builds with pagination
        builds_query = select(Build).order_by(Build.started_at.desc()).limit(limit).offset(offset)
        result = await session.execute(builds_query)
        builds = result.scalars().all()
        
        # Convert to response format
        build_list = []
        for build in builds:
            build_data = {
                "id": build.id,
                "external_id": build.external_id,
                "status": build.status,
                "branch": build.branch,
                "commit_sha": build.commit_sha,
                "triggered_by": build.triggered_by,
                "url": build.url,
                "started_at": build.started_at,
                "finished_at": build.finished_at,
                "duration_seconds": build.duration_seconds,
                "provider_name": "GitHub Actions"
            }
            build_list.append(build_data)
        
        return BuildListResponse(
            builds=build_list,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        print(f"Error getting builds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get builds: {str(e)}")

@app.get("/api/builds/{build_id}", response_model=BuildSchema)
async def get_build(build_id: int, session: AsyncSession = Depends(get_db)):
    """Get specific build by ID"""
    try:
        build_query = select(Build).where(Build.id == build_id)
        result = await session.execute(build_query)
        build = result.scalar_one_or_none()
        
        if not build:
            raise HTTPException(status_code=404, detail="Build not found")
        
        return {
            "id": build.id,
            "external_id": build.external_id,
            "status": build.status,
            "branch": build.branch,
            "commit_sha": build.commit_sha,
            "triggered_by": build.triggered_by,
            "url": build.url,
            "started_at": build.started_at,
            "finished_at": build.finished_at,
            "duration_seconds": build.duration_seconds,
            "provider_name": "GitHub Actions"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting build {build_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get build: {str(e)}")

@app.post("/api/webhook/github-actions")
async def github_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """Handle GitHub Actions webhook"""
    # Verify authentication
    await verify_webhook_auth(request)
    
    try:
        payload = await request.json()
        print(f"Received GitHub webhook: {payload}")
        
        # Extract data from payload (handle different webhook formats)
        if 'workflow_run' in payload:
            # GitHub workflow_run webhook format
            workflow_run = payload['workflow_run']
            repository = payload.get('repository', {})
            sender = payload.get('sender', {})
            
            external_id = str(workflow_run.get('id', 'unknown'))
            status = workflow_run.get('conclusion', 'running')
            branch = workflow_run.get('head_branch', 'main')
            commit_sha = workflow_run.get('head_commit', {}).get('id', 'unknown')
            triggered_by = sender.get('login', 'unknown')
            url = workflow_run.get('html_url', '')
            started_at = workflow_run.get('run_started_at')
            finished_at = workflow_run.get('conclusion', 'running') == 'running' and None or workflow_run.get('updated_at')
            
        else:
            # Custom webhook format
            external_id = str(payload.get('run_id', 'unknown'))
            status = payload.get('conclusion', 'running')
            branch = payload.get('head_branch', 'main')
            commit_sha = payload.get('head_sha', 'unknown')
            triggered_by = payload.get('actor', {}).get('login', 'unknown')
            url = payload.get('html_url', '')
            started_at = payload.get('run_started_at')
            finished_at = payload.get('conclusion', 'running') == 'running' and None or payload.get('updated_at')
        
        # Parse dates if they're strings
        if isinstance(started_at, str):
            from datetime import datetime
            started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        if isinstance(finished_at, str):
            from datetime import datetime
            finished_at = datetime.fromisoformat(finished_at.replace('Z', '+00:00'))
        
        # Calculate duration
        duration_seconds = None
        if started_at and finished_at:
            duration_seconds = (finished_at - started_at).total_seconds()
        
        # Create or update build record
        build = Build(
            external_id=external_id,
            status=status,
            branch=branch,
            commit_sha=commit_sha,
            triggered_by=triggered_by,
            url=url,
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration_seconds,
            provider_id=1,  # GitHub Actions
            raw_payload=payload
        )
        
        session.add(build)
        await session.commit()
        
        print(f"✅ Build {external_id} processed successfully")
        
        # Send alert if build failed
        if status == "failure":
            print(f"🚨 Build failed! Sending alert for build {external_id}")
            try:
                alert_result = await alert_service.send_build_failure_alert(build, "GitHub Actions")
                print(f"📧 Alert result: {alert_result}")
            except Exception as e:
                print(f"❌ Failed to send alert: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"ℹ️  Build status: {status} - no alert needed")
        
        return {"message": "Webhook processed successfully", "build_id": build.id}
        
    except Exception as e:
        print(f"Error processing GitHub webhook: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")



@app.post("/api/alert/test", response_model=AlertTestResponse)
async def test_alert(request: AlertTestRequest):
    """Test alert functionality"""
    try:
        print(f"Testing alert: {request.message}")
        
        # Get recipient from environment variable or use default
        recipient = os.getenv("ALERT_TEST_RECIPIENT", "gopalakrishnan.kuppan@gmail.com")
        
        # Send test alert to configured recipient
        success = await alert_service.send_alert(
            message=request.message,
            severity=request.severity,
            alert_type=request.alert_type,
            recipients=recipient
        )
        
        return AlertTestResponse(
            success=success,
            message=f"Alert test completed successfully to {recipient}" if success else "Alert test failed"
        )
        
    except Exception as e:
        print(f"Error testing alert: {e}")
        return AlertTestResponse(
            success=False,
            message=f"Alert test failed: {str(e)}"
        )

@app.post("/api/seed", response_model=SeedResponse)
async def seed_database(session: AsyncSession = Depends(get_db)):
    """Seed database with sample data"""
    try:
        print("Seeding database with sample data...")
        
        # Create providers if they don't exist
        providers_query = select(Provider)
        existing_providers = await session.execute(providers_query)
        if not existing_providers.scalars().all():
            github_provider = Provider(
                name="GitHub Actions",
                kind="github_actions",
                config_json={"webhook_url": "https://api.github.com"},
                is_active=True
            )
            session.add(github_provider)
            await session.commit()
            print("✅ GitHub Actions provider created")
        
        # Create sample builds
        builds_query = select(Build)
        existing_builds = await session.execute(builds_query)
        if not existing_builds.scalars().all():
            now = datetime.now()
            sample_builds = [
                Build(
                    external_id="123456789",
                    status="success",
                    branch="main",
                    commit_sha="abc123def456",
                    triggered_by="github-actions",
                    url="https://github.com/nandhu-devops/cicd-pipeline-dashboard/actions/runs/123456789",
                    started_at=now - timedelta(hours=2),
                    finished_at=now - timedelta(hours=1, minutes=45),
                    duration_seconds=900,
                    provider_id=1
                ),
                Build(
                    external_id="987654321",
                    status="failed",
                    branch="feature/new-feature",
                    commit_sha="def456abc789",
                    triggered_by="github-actions",
                    url="https://github.com/nandhu-devops/cicd-pipeline-dashboard/actions/runs/987654321",
                    started_at=now - timedelta(hours=4),
                    finished_at=now - timedelta(hours=3, minutes=30),
                    duration_seconds=1800,
                    provider_id=1
                ),
                Build(
                    external_id="555666777",
                    status="running",
                    branch="main",
                    commit_sha="ghi789jkl012",
                    triggered_by="github-actions",
                    url="https://github.com/nandhu-devops/cicd-pipeline-dashboard/actions/runs/555666777",
                    started_at=now - timedelta(minutes=30),
                    finished_at=None,
                    duration_seconds=None,
                    provider_id=1
                )
            ]
            session.add_all(sample_builds)
            await session.commit()
            print("✅ Sample builds created")
        
        return SeedResponse(
            success=True,
            message="Database seeded successfully",
            builds_created=3,
            providers_created=1
        )
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to seed database: {str(e)}")

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    # Clean old timestamps
    _rate_limits[client_ip] = [ts for ts in _rate_limits[client_ip] if now - ts < RATE_LIMIT_WINDOW_SECONDS]
    
    # Check rate limit
    if len(_rate_limits[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Add current timestamp
    _rate_limits[client_ip].append(now)
    
    response = await call_next(request)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
