@echo off
pip install dlib-bin>=20.0 || goto :error
pip install --no-deps face-recognition>=1.3.0 || goto :error
pip install -r requirements.txt || goto :error
goto :eof

:error
echo ERROR: Installation failed. Check the output above for details.
exit /b 1
