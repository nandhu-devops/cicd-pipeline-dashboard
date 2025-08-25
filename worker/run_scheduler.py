#!/usr/bin/env python3
"""
Simple entry point for running the CI/CD Health Dashboard Worker Scheduler

Usage: python run_scheduler.py

This script runs the worker scheduler that polls CI/CD providers
and updates the dashboard via API calls.
"""

import asyncio
import sys
import os

# Add the worker directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scheduler import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWorker scheduler stopped by user")
    except Exception as e:
        print(f"Worker scheduler failed: {e}")
        sys.exit(1)
