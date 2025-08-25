#!/usr/bin/env python3
"""
Simple import tests to verify dependencies are available
"""

def test_import_aiohttp():
    """Test that aiohttp can be imported"""
    try:
        import aiohttp
        assert aiohttp is not None
        print("✅ aiohttp imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import aiohttp: {e}")

def test_import_fastapi():
    """Test that fastapi can be imported"""
    try:
        import fastapi
        assert fastapi is not None
        print("✅ fastapi imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import fastapi: {e}")

def test_import_uvicorn():
    """Test that uvicorn can be imported"""
    try:
        import uvicorn
        assert uvicorn is not None
        print("✅ uvicorn imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import uvicorn: {e}")

def test_import_sqlalchemy():
    """Test that sqlalchemy can be imported"""
    try:
        import sqlalchemy
        assert sqlalchemy is not None
        print("✅ sqlalchemy imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import sqlalchemy: {e}")

def test_import_aiosmtplib():
    """Test that aiosmtplib can be imported"""
    try:
        import aiosmtplib
        assert aiosmtplib is not None
        print("✅ aiosmtplib imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import aiosmtplib: {e}")

def test_import_aiosqlite():
    """Test that aiosqlite can be imported"""
    try:
        import aiosqlite
        assert aiosqlite is not None
        print("✅ aiosqlite imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import aiosqlite: {e}")

if __name__ == "__main__":
    print("Running import tests...")
    test_import_aiohttp()
    test_import_fastapi()
    test_import_uvicorn()
    test_import_sqlalchemy()
    test_import_aiosmtplib()
    test_import_aiosqlite()
    print("✅ All import tests passed!")
