import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CICDPoller:
    """Polls CI/CD providers and updates the dashboard via API calls"""
    
    def __init__(self):
        # GitHub Actions configuration
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_base_url = "https://api.github.com"
        
        # Jenkins configuration
        self.jenkins_url = os.getenv("JENKINS_URL")
        self.jenkins_username = os.getenv("JENKINS_USERNAME")
        self.jenkins_api_token = os.getenv("JENKINS_API_TOKEN")
        
        # Dashboard API configuration
        self.dashboard_api_url = os.getenv("DASHBOARD_API_URL", "http://localhost:8000")
        self.dashboard_api_key = os.getenv("DASHBOARD_API_KEY", "dev-write-key-change-in-production")
        
        # HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "User-Agent": "CI/CD-Health-Dashboard-Worker/1.0.0"
            }
        )
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_api_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic"""
        try:
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return None
    
    async def poll_github_actions(self, owner: str, repo: str) -> bool:
        """Poll GitHub Actions for recent workflow runs"""
        if not self.github_token:
            logger.warning("GitHub token not configured, skipping GitHub Actions polling")
            return False
        
        try:
            # Get recent workflow runs
            url = f"{self.github_base_url}/repos/{owner}/{repo}/actions/runs"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get runs from last 24 hours
            since = datetime.now() - timedelta(hours=24)
            params = {
                "per_page": 50,
                "since": since.isoformat()
            }
            
            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            runs_data = response.json()
            
            workflow_runs = runs_data.get("workflow_runs", [])
            logger.info(f"Found {len(workflow_runs)} recent workflow runs for {owner}/{repo}")
            
            # Process each workflow run
            for run in workflow_runs:
                await self._process_github_workflow_run(owner, repo, run)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to poll GitHub Actions for {owner}/{repo}: {e}")
            return False
    
    async def _process_github_workflow_run(self, owner: str, repo: str, run: Dict[str, Any]):
        """Process a single GitHub workflow run and send to dashboard API"""
        try:
            # Create webhook payload format
            webhook_payload = {
                "workflow_run": run,
                "workflow": {
                    "id": run.get("workflow_id"),
                    "name": run.get("name", "Unknown Workflow"),
                    "path": f".github/workflows/{run.get('name', 'unknown')}.yml"
                },
                "repository": {
                    "id": run.get("repository", {}).get("id"),
                    "name": repo,
                    "full_name": f"{owner}/{repo}",
                    "private": False,
                    "owner": {
                        "login": owner,
                        "id": run.get("repository", {}).get("owner", {}).get("id"),
                        "type": "User"
                    }
                },
                "sender": {
                    "login": run.get("actor", {}).get("login", "unknown"),
                    "id": run.get("actor", {}).get("id"),
                    "type": "User"
                }
            }
            
            # Send to dashboard API
            await self._send_webhook_to_dashboard("/api/webhook/github-actions", webhook_payload)
            
        except Exception as e:
            logger.error(f"Failed to process GitHub workflow run {run.get('id')}: {e}")
    
    async def poll_jenkins(self, job_name: str) -> bool:
        """Poll Jenkins for recent builds"""
        if not all([self.jenkins_url, self.jenkins_username, self.jenkins_api_token]):
            logger.warning("Jenkins credentials not configured, skipping Jenkins polling")
            return False
        
        try:
            # Get job information
            job_url = f"{self.jenkins_url}/job/{job_name}/api/json"
            auth = (self.jenkins_username, self.jenkins_api_token)
            
            response = await self.http_client.get(job_url, auth=auth)
            response.raise_for_status()
            job_data = response.json()
            
            builds = job_data.get("builds", [])
            logger.info(f"Found {len(builds)} builds for Jenkins job {job_name}")
            
            # Get recent builds (last 10)
            recent_builds = builds[:10]
            
            # Process each build
            for build in recent_builds:
                await self._process_jenkins_build(job_name, build)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to poll Jenkins for job {job_name}: {e}")
            return False
    
    async def _process_jenkins_build(self, job_name: str, build: Dict[str, Any]):
        """Process a single Jenkins build and send to dashboard API"""
        try:
            # Get detailed build information
            build_number = build.get("number")
            build_url = f"{self.jenkins_url}/job/{job_name}/{build_number}/api/json"
            auth = (self.jenkins_username, self.jenkins_api_token)
            
            response = await self.http_client.get(build_url, auth=auth)
            response.raise_for_status()
            build_data = response.json()
            
            # Create webhook payload format
            webhook_payload = {
                "name": job_name,
                "url": f"{self.jenkins_url}/job/{job_name}",
                "build": build_data
            }
            
            # Send to dashboard API
            await self._send_webhook_to_dashboard("/api/webhook/jenkins", webhook_payload)
            
        except Exception as e:
            logger.error(f"Failed to process Jenkins build {build.get('number')}: {e}")
    
    async def _send_webhook_to_dashboard(self, endpoint: str, payload: Dict[str, Any]) -> bool:
        """Send webhook payload to dashboard API"""
        try:
            url = f"{self.dashboard_api_url}{endpoint}"
            headers = {
                "Content-Type": "application/json",
                "X-API-KEY": self.dashboard_api_key
            }
            
            response = await self.http_client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.debug(f"Successfully sent webhook to {endpoint}")
            return True
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending webhook to {endpoint}: {e.response.status_code}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Request error sending webhook to {endpoint}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending webhook to {endpoint}: {e}")
            return False
    
    async def poll_all_providers(self):
        """Poll all enabled providers"""
        logger.info("Starting provider polling cycle")
        
        # GitHub Actions repositories to poll
        github_repos = self._get_github_repos_from_env()
        for owner, repo in github_repos:
            try:
                await self.poll_github_actions(owner, repo)
            except Exception as e:
                logger.error(f"Failed to poll GitHub Actions for {owner}/{repo}: {e}")
                continue
        
        # Jenkins jobs to poll
        jenkins_jobs = self._get_jenkins_jobs_from_env()
        for job_name in jenkins_jobs:
            try:
                await self.poll_jenkins(job_name)
            except Exception as e:
                logger.error(f"Failed to poll Jenkins for job {job_name}: {e}")
                continue
        
        logger.info("Completed provider polling cycle")
    
    def _get_github_repos_from_env(self) -> List[tuple]:
        """Get GitHub repositories to poll from environment variables"""
        repos = []
        
        # Check for GITHUB_REPOS environment variable
        github_repos_env = os.getenv("GITHUB_REPOS")
        if github_repos_env:
            for repo_spec in github_repos_env.split(","):
                repo_spec = repo_spec.strip()
                if "/" in repo_spec:
                    owner, repo = repo_spec.split("/", 1)
                    repos.append((owner.strip(), repo.strip()))
        
        # Fallback to default if none specified
        if not repos:
            default_owner = os.getenv("GITHUB_OWNER", "myorg")
            default_repo = os.getenv("GITHUB_REPO", "myapp")
            repos.append((default_owner, default_repo))
        
        return repos
    
    def _get_jenkins_jobs_from_env(self) -> List[str]:
        """Get Jenkins jobs to poll from environment variables"""
        jobs = []
        
        # Check for JENKINS_JOBS environment variable
        jenkins_jobs_env = os.getenv("JENKINS_JOBS")
        if jenkins_jobs_env:
            jobs = [job.strip() for job in jenkins_jobs_env.split(",") if job.strip()]
        
        # Fallback to default if none specified
        if not jobs:
            default_job = os.getenv("JENKINS_DEFAULT_JOB", "myapp-pipeline")
            jobs.append(default_job)
        
        return jobs

async def main():
    """Main entry point"""
    poller = CICDPoller()
    
    try:
        await poller.poll_all_providers()
    except KeyboardInterrupt:
        await poller.close()

if __name__ == "__main__":
    asyncio.run(main())
