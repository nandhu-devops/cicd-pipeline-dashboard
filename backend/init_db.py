#!/usr/bin/env python3
"""
Database initialization script for CI/CD Health Dashboard
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Add the app directory to the Python path
app_dir = current_dir / "app"
sys.path.insert(0, str(app_dir))

async def main():
    """Initialize the database with tables and basic data"""
    print("🚀 Initializing CI/CD Health Dashboard Database...")
    
    try:
        # Import after setting up paths
        from app.db import init_db, close_db, async_engine
        from app.models import Base, Provider, Alert, Settings
        
        print("📋 Creating database tables...")
        await init_db()
        
        # Wait for tables to be fully created
        await asyncio.sleep(2)
        
        # Verify tables exist before trying to insert data
        print("🔍 Verifying tables exist...")
        async with async_engine.begin() as conn:
            def get_table_names(connection):
                from sqlalchemy import inspect
                inspector = inspect(connection)
                return inspector.get_table_names()
            
            tables = await conn.run_sync(get_table_names)
            print(f"📋 Available tables: {tables}")
        
        if 'alerts' not in tables or 'settings' not in tables:
            print("⚠️  Tables not fully created, skipping data insertion")
            return
        
        # Create default alert configuration
        print("🔔 Setting up default alert configuration...")
        async with async_engine.begin() as conn:
            try:
                # Check if default alert exists
                from sqlalchemy import select
                result = await conn.execute(select(Alert).where(Alert.name == "default-email"))
                if not result.scalar_one_or_none():
                    # Create default email alert
                    await conn.execute(
                        "INSERT INTO alerts (name, type, config_json, is_active, created_at) VALUES (?, ?, ?, ?, ?)",
                        ("default-email", "email", '{"enabled": true, "recipients": ["admin@example.com"]}', True, "2024-01-01T00:00:00")
                    )
                    print("✅ Default email alert created")
                else:
                    print("ℹ️  Default alert already exists")
            except Exception as e:
                print(f"⚠️  Warning: Could not create default alert: {e}")
        
        # Create default settings
        print("⚙️  Setting up default settings...")
        async with async_engine.begin() as conn:
            try:
                # Check if default settings exist
                result = await conn.execute(select(Settings).where(Settings.key == "dashboard_title"))
                if not result.scalar_one_or_none():
                    # Create default settings
                    default_settings = [
                        ("dashboard_title", "CI/CD Health Dashboard", "Dashboard title"),
                        ("refresh_interval", "30", "Auto-refresh interval in seconds"),
                        ("alerts_enabled", "true", "Enable/disable alert system"),
                        ("max_builds_display", "50", "Maximum builds to display in table")
                    ]
                    
                    for key, value, description in default_settings:
                        await conn.execute(
                            "INSERT INTO settings (key, value, description, created_at) VALUES (?, ?, ?, ?)",
                            (key, value, description, "2024-01-01T00:00:00")
                        )
                    print("✅ Default settings created")
                else:
                    print("ℹ️  Default settings already exist")
            except Exception as e:
                print(f"⚠️  Warning: Could not create default settings: {e}")
        
        print("🎉 Database initialization completed successfully!")
        print("\n📊 Next steps:")
        print("1. Start the backend: python run_server.py")
        print("2. Seed with sample data: curl -X POST http://localhost:8000/api/seed")
        print("3. Open the frontend: frontend/index.html")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
