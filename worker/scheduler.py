#!/usr/bin/env python3
"""
CI/CD Health Dashboard Worker Scheduler

Entry point: python scheduler.py

This script runs the worker scheduler that polls CI/CD providers
and updates the dashboard via API calls.

Environment variables:
- ENABLE_GH: Enable GitHub Actions polling (default: true)
- ENABLE_JENKINS: Enable Jenkins polling (default: false)
- WORKER_POLL_INTERVAL: Polling interval in seconds (default: 60)
- WORKER_JITTER_SECONDS: Jitter to avoid thundering herd (default: 10)
- GITHUB_TOKEN: GitHub personal access token
- GITHUB_REPOS: Comma-separated list of owner/repo pairs
- JENKINS_URL: Jenkins server URL
- JENKINS_USERNAME: Jenkins username
- JENKINS_API_TOKEN: Jenkins API token
- JENKINS_JOBS: Comma-separated list of job names
- DASHBOARD_API_URL: Dashboard API base URL (default: http://localhost:8000)
- DASHBOARD_API_KEY: Dashboard API write key
"""

import os
import asyncio
import logging
import random
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from dotenv import load_dotenv

from .poller import CICDPoller

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkerScheduler:
    """Schedules and manages CI/CD provider polling jobs"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.poller = CICDPoller()
        self.running = False
        
        # Configuration from environment
        self.poll_interval = int(os.getenv("WORKER_POLL_INTERVAL", "60"))  # seconds
        self.enable_github = os.getenv("ENABLE_GH", "true").lower() == "true"
        self.enable_jenkins = os.getenv("ENABLE_JENKINS", "false").lower() == "true"
        self.jitter_seconds = int(os.getenv("WORKER_JITTER_SECONDS", "10"))  # jitter to avoid thundering herd
        
        # Add event listeners
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    
    async def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("Starting CI/CD Worker Scheduler")
        logger.info(f"Poll interval: {self.poll_interval} seconds")
        logger.info(f"GitHub Actions enabled: {self.enable_github}")
        logger.info(f"Jenkins enabled: {self.enable_jenkins}")
        logger.info(f"Jitter: {self.jitter_seconds} seconds")
        
        try:
            # Start the scheduler
            self.scheduler.start()
            self.running = True
            
            # Add the main polling job
            await self._add_polling_job()
            
            logger.info("Scheduler started successfully")
            
            # Keep the scheduler running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        logger.info("Stopping CI/CD Worker Scheduler")
        self.running = False
        
        try:
            # Shutdown the scheduler
            self.scheduler.shutdown(wait=True)
            
            # Close the poller
            await self.poller.close()
            
            logger.info("Scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def _add_polling_job(self):
        """Add the main polling job to the scheduler"""
        try:
            # Add jitter to avoid thundering herd
            jitter = random.randint(0, self.jitter_seconds)
            
            # Schedule the job
            self.scheduler.add_job(
                func=self._execute_polling_cycle,
                trigger=IntervalTrigger(
                    seconds=self.poll_interval,
                    jitter=jitter
                ),
                id="cicd_polling_job",
                name="CI/CD Provider Polling",
                max_instances=1,  # Prevent overlapping executions
                coalesce=True,    # Combine missed executions
                misfire_grace_time=300  # 5 minutes grace time
            )
            
            logger.info(f"Added polling job with {self.poll_interval}s interval and {jitter}s jitter")
            
        except Exception as e:
            logger.error(f"Failed to add polling job: {e}")
            raise
    
    async def _execute_polling_cycle(self):
        """Execute a single polling cycle"""
        try:
            logger.info("Executing polling cycle")
            
            # Check if providers are enabled
            if not self.enable_github and not self.enable_jenkins:
                logger.warning("No providers enabled, skipping polling cycle")
                return
            
            # Execute the polling
            await self.poller.poll_all_providers()
            
            logger.info("Polling cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in polling cycle: {e}")
            # Don't re-raise - let the scheduler handle it
    
    def _job_listener(self, event):
        """Handle job execution events"""
        if event.code == EVENT_JOB_EXECUTED:
            logger.debug(f"Job {event.job_id} executed successfully")
        elif event.code == EVENT_JOB_ERROR:
            logger.error(f"Job {event.job_id} failed: {event.exception}")
            logger.error(f"Traceback: {event.traceback}")
    
    async def run_once(self):
        """Run a single polling cycle (useful for testing)"""
        logger.info("Running single polling cycle")
        await self.poller.poll_all_providers()
        logger.info("Single polling cycle completed")

async def main():
    """Main entry point for the worker scheduler"""
    scheduler = WorkerScheduler()
    
    try:
        await scheduler.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        await scheduler.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker scheduler stopped by user")
    except Exception as e:
        logger.error(f"Worker scheduler failed: {e}")
        exit(1)
