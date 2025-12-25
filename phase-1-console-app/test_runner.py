#!/usr/bin/env python3
"""
Simple test runner for the console todo application
"""
import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Discover and run tests
if __name__ == "__main__":
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with error code if tests failed
    if result.failures or result.errors:
        sys.exit(1)
    else:
        print("All tests passed!")