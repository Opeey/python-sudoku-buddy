#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import ast

def parse_log(filename):
    with open(filename) as input:
        lines = input.readlines()
    events = [ast.literal_eval(l) for l in lines]
    return events

if __name__ == '__main__':
    events = parse_log(sys.argv[1])
    for evt in events:
        print evt
