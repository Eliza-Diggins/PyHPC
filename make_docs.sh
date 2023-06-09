#!/bin/bash

echo "PyHPC: Generating the documentation..."

# Locating the correct directory
#---------------------------------#
echo "PyHPC:     Locating the correct directory..."
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CURRENT_DIR=`pwd`

echo "PyHPC:         Found script directory -> $SCRIPT_DIR"
echo "PyHPC:         Relocating to $SCRIPT_DIR..."
cd "$SCRIPT_DIR" || echo "CD Failed"
echo "PyHPC:             [DONE]"

# Actually performing
#--------------------------------#
echo "PyHPC:     Producing the documentation..."
pdoc3 --html --force -c latex_math=True -o . ../PyHPC | tee html_docgen.log
pdoc3 --force -c latex_math=True -o . ../PyHPC | tee md_docgen.log
echo "PyHPC:     Documentation Production Finished."
