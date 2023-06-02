#!/bin/bash

echo "Generating Documentation..."

pdoc3 --html --force -c latex_math=True -o . ../PyHPC

echo "Finished"