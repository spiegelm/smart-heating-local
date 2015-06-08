#!/bin/bash
set -e
set -u

python3 -m unittest $@
