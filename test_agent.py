#!/usr/bin/env python3
"""
Backward-compatible Test Runner
Runs the modular testing suite located in the tests/ directory
"""

import sys
import pytest

if __name__ == "__main__":
    print("=" * 70)
    print("SHL Assessment Recommender - Production Modular Test Suite")
    print("=" * 70)
    
    # Execute pytest dynamically on our tests/ directory
    exit_code = pytest.main(["-v", "tests/"])
    sys.exit(exit_code)
