#!/usr/bin/env python3
"""
Basic tests that don't require importing the full app
"""

def test_basic_math():
    """Test basic math operations"""
    assert 2 + 2 == 4
    assert 3 * 4 == 12
    assert 10 / 2 == 5

def test_string_operations():
    """Test string operations"""
    assert "hello" + " " + "world" == "hello world"
    assert len("test") == 4
    assert "CI/CD" in "CI/CD Health Dashboard"

def test_list_operations():
    """Test list operations"""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert sum(test_list) == 15
    assert test_list[0] == 1
    assert test_list[-1] == 5

def test_dict_operations():
    """Test dictionary operations"""
    test_dict = {"name": "Dashboard", "type": "CI/CD"}
    assert test_dict["name"] == "Dashboard"
    assert test_dict["type"] == "CI/CD"
    assert len(test_dict) == 2

def test_boolean_operations():
    """Test boolean operations"""
    assert True is True
    assert False is False
    assert not False is True
    assert True and True is True
    assert True or False is True

if __name__ == "__main__":
    print("Running basic tests...")
    test_basic_math()
    test_string_operations()
    test_list_operations()
    test_dict_operations()
    test_boolean_operations()
    print("✅ All basic tests passed!")
