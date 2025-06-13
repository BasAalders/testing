#!/bin/bash
echo "Running Quiz App Tests..."
python -m unittest discover -s tests -p "test_*.py"
echo "Tests finished."
