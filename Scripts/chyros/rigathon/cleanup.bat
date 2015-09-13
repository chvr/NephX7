@echo off

del /s *.bak
del /s *.pyc
del /q generated\*
del /q script\__pycache__*
rmdir script\__pycache__
