#!/bin/sh

rm -r ./build
rm sFunc.c sFunc.so
python setup.py build_ext -i