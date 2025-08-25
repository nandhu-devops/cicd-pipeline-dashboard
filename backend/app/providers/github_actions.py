import aiohttp
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..secret_manager import get_secret_or_env
import logging

logger = logging.getLogger(__name__)

class GitHubActionsProvider:
    """Provider for GitHub Actions CI/CD pipelines"""
    
    def __init__(self):
        self.token = get_secret_or_env("github_token", "GITHUB_TOKEN")
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        } if self.token else {}
    
    def parse_workflow_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parse GitHub Actions webhook payload into normalized Build format"""
        try:
            workflow_run = payload.get("workflow_run", {})
            repository = payload.get("repository", {})
            
            # Extract basic information
            external_id = str(workflow_run.get("id"))
            status = self._normalize_status(workflow_run.get("conclusion") or workflow_run.get("status"))
            
            # Calculate duration
            duration_seconds = None
            started_at = None
            finished_at = None
            
            if workflow_run.get("run_started_at") and workflow_run.get("updated_at"):
                started_at = datetime.fromisoformat(workflow_run["run_started_at"].replace("Z", "+00:00"))
                finished_at = datetime.fromisoformat(workflow_run["updated_at"].replace("Z", "+00:00"))
                duration_seconds = int((finished_at - started_at).total_seconds())
            
            # Extract commit information
            head_commit = workflow_run.get("head_commit", {})
            commit_sha = head_commit.get("id")
            commit_message = head_commit.get("message", "").split("\n")[0]  # First line only
            
            # Extract author information
            author = None
            if head_commit.get("author", {}).get("name"):
                author = head_commit["author"]["name"]
            elif workflow_run.get("triggering_actor", {}).get("login"):
                author = workflow_run["triggering_actor"]["login"]
            
            # Extract branch information
            branch = workflow_run.get("head_branch", "main")
            
            # Build URL
            url = workflow_run.get("html_url")
            
            # Raw payload for debugging
            raw_payload = payload
            
            return {
                "external_id": external_id,
                "status": status,
                "duration_seconds": duration_seconds,
                "branch": branch,
                "commit_sha": commit_sha,
                "commit_message": commit_message,
                "triggered_by": author,
                "started_at": started_at,
                "finished_at": finished_at,
                "url": url,
                "raw_payload": raw_payload,
                "metadata": {
                    "workflow_name": workflow_run.get("name"),
                    "event": workflow_run.get("event"),
                    "run_number": workflow_run.get("run_number"),
                    "repository": repository.get("full_name"),
                    "pull_request": workflow_run.get("pull_requests", []),
                    "conclusion": workflow_run.get("conclusion"),
                    "run_attempt": workflow_run.get("run_attempt")
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to parse GitHub Actions workflow run: {e}")
            raise
    
    def _normalize_status(self, status: str) -> str:
        """Normalize GitHub Actions status to standard statuses"""
        status_mapping = {
            "success": "success",
            "failure": "failed",
            "cancelled": "failed",
            "skipped": "success",
            "in_progress": "running",
            "queued": "queued",
            "waiting": "queued",
            "neutral": "success"
        }
        return status_mapping.get(status, "unknown")
    
    async def fetch_workflow_runs(
        self, 
        owner: str, 
        repo: str, 
        branch: str = "main",
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """Fetch workflow runs for a repository"""
        if not self.token:
            logger.warning("GitHub token not configured")
            return []
        
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs"
        params = {
            "branch": branch,
            "per_page": per_page,
            "status": "completed"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("workflow_runs", [])
                    else:
                        logger.error(f"Failed to fetch GitHub Actions runs: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching GitHub Actions runs: {e}")
            return []
    
    async def fetch_workflow_run_details(
        self, 
        owner: str, 
        repo: str, 
        run_id: int
    ) -> Optional[Dict[str, Any]]:
        """Fetch detailed information about a specific workflow run"""
        if not self.token:
            return None
        
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to fetch workflow run details: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching workflow run details: {e}")
            return None
    
    async def fetch_repository_workflows(
        self, 
        owner: str, 
        repo: str
    ) -> List[Dict[str, Any]]:
        """Fetch all workflows for a repository"""
        if not self.token:
            return []
        
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/workflows"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("workflows", [])
                    else:
                        logger.error(f"Failed to fetch workflows: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching workflows: {e}")
            return []
    
    async def fetch_repository_status(
        self, 
        owner: str, 
        repo: str
    ) -> Dict[str, Any]:
        """Fetch overall repository status and recent activity"""
        if not self.token:
            return {}
        
        try:
            # Fetch recent workflow runs
            runs = await self.fetch_workflow_runs(owner, repo, per_page=5)
            
            # Fetch repository info
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            async with aiohttp.ClientSession() as session:
                async with session.get(repo_url, headers=self.headers) as response:
                    if response.status == 200:
                        repo_data = await response.json()
                        
                        return {
                            "repository": repo_data,
                            "recent_runs": runs,
                            "last_updated": datetime.now().isoformat()
                        }
                    else:
                        logger.error(f"Failed to fetch repository info: {response.status}")
                        return {"recent_runs": runs}
        except Exception as e:
            logger.error(f"Error fetching repository status: {e}")
            return {}
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature for security"""
        if not self.webhook_secret:
            logger.warning("GitHub webhook secret not configured")
            return False
        
        try:
            import hmac
            import hashlib
            
            expected_signature = "sha256=" + hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
