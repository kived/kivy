#!/bin/bash


grep "^__version__ = '[^']*'" `dirname $0`/kivy/__init__.py \
	| awk -F"'" '{print $2}'
