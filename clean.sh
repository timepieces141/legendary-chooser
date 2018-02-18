#!/bin/bash

# clean up from unit tests, builds, etc.

# from building
find . -type d -name __pycache__ -exec rm -rf {} \; 2>/dev/null
find . -type d -name build -exec rm -rf {} \; 2>/dev/null
find . -type d -name dist -exec rm -rf {} \; 2>/dev/null
find . -type d -name *egg-info -exec rm -rf {} \; 2>/dev/null
find . -type f -name version.py -exec rm -f {} \; 2>/dev/null

# from testing
find . -type d -name .pytest_cache -exec rm -rf {} \; 2>/dev/null
find . -type d -name .cache -exec rm -rf {} \; 2>/dev/null
find . -type d -name htmlcov -exec rm -rf {} \; 2>/dev/null
find . -type f -name .coverage -exec rm -f {} \; 2>/dev/null

# logs
find . -type f -name *.log -exec rm -f {} \; 2>/dev/null
