#!/bin/bash

# Wrapper script for running all the tests using pytest and coverage

cd `dirname $0`
PYTHONPATH="../src" python -m coverage run --source legendary -m pytest $@
if [ "$?" != "0" ]; then
    exit 1
fi

# generate coverage
python -m coverage report -m | tee coverage.log
python -m coverage html

# invoke pylint on tests modules and source packages
echo
echo "Pylint Analysis"
shopt -s globstar
pylint *py ../src/**/*.py | tee pylint.log
