-- Seed data for CI/CD Health Dashboard
-- This file contains sample data to populate the database for testing

-- Insert default settings
INSERT OR REPLACE INTO settings (id, alert_email, api_write_key, updated_at) 
VALUES (
    1, 
    'alerts@example.com',
    'dev-write-key-change-in-production',
    CURRENT_TIMESTAMP
);

-- Insert sample GitHub Actions providers
INSERT OR REPLACE INTO providers (id, name, kind, config_json, created_at) VALUES
(1, 'github-myorg/frontend-app', 'github_actions', '{"repository": "myorg/frontend-app", "description": "Frontend React application"}', CURRENT_TIMESTAMP),
(2, 'github-myorg/backend-api', 'github_actions', '{"repository": "myorg/backend-api", "description": "Backend FastAPI service"}', CURRENT_TIMESTAMP),
(3, 'github-myorg/mobile-app', 'github_actions', '{"repository": "myorg/mobile-app", "description": "Mobile React Native application"}', CURRENT_TIMESTAMP),
(4, 'github-myorg/infrastructure', 'github_actions', '{"repository": "myorg/infrastructure", "description": "Infrastructure as Code repository"}', CURRENT_TIMESTAMP);

-- Insert sample GitHub Actions builds
INSERT OR REPLACE INTO builds (id, provider_id, external_id, status, duration_seconds, branch, commit_sha, triggered_by, started_at, finished_at, url, raw_payload, created_at) VALUES
-- Frontend app builds
(1, 1, '123456789', 'success', 180, 'main', 'abc123def456789abcdef123456789abcdef1234', 'johndoe', '2024-01-15 10:30:00', '2024-01-15 10:33:00', 'https://github.com/myorg/frontend-app/actions/runs/123456789', '{"workflow_run": {"id": 123456789, "conclusion": "success"}}', '2024-01-15 10:30:00'),
(2, 1, '123456790', 'failed', 120, 'feature/new-component', 'def456ghi789abcdef123456789abcdef123456', 'janedoe', '2024-01-15 11:00:00', '2024-01-15 11:02:00', 'https://github.com/myorg/frontend-app/actions/runs/123456790', '{"workflow_run": {"id": 123456790, "conclusion": "failure"}}', '2024-01-15 11:00:00'),
(3, 1, '123456791', 'running', NULL, 'feature/dark-mode', 'ghi789jkl012abcdef123456789abcdef123456', 'bobsmith', '2024-01-15 12:00:00', NULL, 'https://github.com/myorg/frontend-app/actions/runs/123456791', '{"workflow_run": {"id": 123456791, "status": "in_progress"}}', '2024-01-15 12:00:00'),

-- Backend API builds
(4, 2, '987654321', 'success', 300, 'main', 'jkl012mno345abcdef123456789abcdef123456', 'alicejohnson', '2024-01-15 09:00:00', '2024-01-15 09:05:00', 'https://github.com/myorg/backend-api/actions/runs/987654321', '{"workflow_run": {"id": 987654321, "conclusion": "success"}}', '2024-01-15 09:00:00'),
(5, 2, '987654322', 'success', 280, 'feature/api-improvements', 'mno345pqr678abcdef123456789abcdef123456', 'charliebrown', '2024-01-15 14:00:00', '2024-01-15 14:04:40', 'https://github.com/myorg/backend-api/actions/runs/987654322', '{"workflow_run": {"id": 987654322, "conclusion": "success"}}', '2024-01-15 14:00:00'),
(6, 2, '987654323', 'queued', NULL, 'feature/database-optimization', 'pqr678stu901abcdef123456789abcdef123456', 'davidwilson', NULL, NULL, 'https://github.com/myorg/backend-api/actions/runs/987654323', '{"workflow_run": {"id": 987654323, "status": "queued"}}', '2024-01-15 16:00:00'),

-- Mobile app builds
(7, 3, '456789123', 'success', 420, 'main', 'stu901vwx234abcdef123456789abcdef123456', 'emilydavis', '2024-01-15 08:00:00', '2024-01-15 08:07:00', 'https://github.com/myorg/mobile-app/actions/runs/456789123', '{"workflow_run": {"id": 456789123, "conclusion": "success"}}', '2024-01-15 08:00:00'),
(8, 3, '456789124', 'failed', 600, 'feature/push-notifications', 'vwx234yza567abcdef123456789abcdef123456', 'frankmiller', '2024-01-15 15:00:00', '2024-01-15 15:10:00', 'https://github.com/myorg/mobile-app/actions/runs/456789124', '{"workflow_run": {"id": 456789124, "conclusion": "failure"}}', '2024-01-15 15:00:00'),

-- Infrastructure builds
(9, 4, '789123456', 'success', 900, 'main', 'yza567bcd890abcdef123456789abcdef123456', 'gracelee', '2024-01-15 07:00:00', '2024-01-15 07:15:00', 'https://github.com/myorg/infrastructure/actions/runs/789123456', '{"workflow_run": {"id": 789123456, "conclusion": "success"}}', '2024-01-15 07:00:00'),
(10, 4, '789123457', 'running', NULL, 'feature/new-region', 'bcd890efg123abcdef123456789abcdef123456', 'henrytaylor', '2024-01-15 13:00:00', NULL, 'https://github.com/myorg/infrastructure/actions/runs/789123457', '{"workflow_run": {"id": 789123457, "status": "in_progress"}}', '2024-01-15 13:00:00');

-- Insert sample alerts
INSERT OR REPLACE INTO alerts (id, build_id, channel, sent_at, success, message) VALUES
(1, 2, 'email', '2024-01-15 11:02:30', true, 'Build failure alert sent to alerts@example.com'),
(2, 8, 'email', '2024-01-15 15:10:30', true, 'Build failure alert sent to alerts@example.com'),
(3, 3, 'email', '2024-01-15 09:05:30', true, 'Backend API build succeeded on main branch. Build completed in 5 minutes.'),
(4, 1, 'email', '2024-01-15 10:33:30', true, 'Frontend app build succeeded on main branch. Build completed in 3 minutes.'),
(5, 7, 'email', '2024-01-15 08:07:30', true, 'Mobile app build succeeded on main branch. Build completed in 7 minutes.'),
(6, 9, 'email', '2024-01-15 07:15:30', true, 'Infrastructure build succeeded on main branch. Build completed in 15 minutes.');
