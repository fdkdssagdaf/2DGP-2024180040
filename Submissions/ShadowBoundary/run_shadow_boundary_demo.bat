@echo off
setlocal
cd /d "%~dp0..\.."
python Submissions\ShadowBoundary\shadow_boundary_demo.py
if errorlevel 1 pause
