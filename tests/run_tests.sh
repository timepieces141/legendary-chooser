#!/bin/bash

# Wrapper script for running all the tests using pytest and coverage

cd `dirname $0`
# PYTHONPATH="../src" python -m coverage run --source dir_not_in_src -m pytest $@
PYTHONPATH="../src" python -m coverage run -m pytest $@
if [ "$?" != "0" ]; then
    exit 1
fi

python -m coverage report -m
python -m coverage html

# invoke pylint on tests modules and source packages
# pylint *py dir_not_in_src/*.py tests/*.py
pylint *py
