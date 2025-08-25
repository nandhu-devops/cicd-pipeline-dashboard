#!/usr/bin/env python3
"""
Test file that will intentionally fail to test email notifications
"""

def test_intentional_failure():
    """This test will fail to trigger email notifications"""
    assert 1 == 2, "This test is designed to fail to test email alerts"

def test_another_failure():
    """Another failing test"""
    assert "hello" == "world", "String comparison will fail"
