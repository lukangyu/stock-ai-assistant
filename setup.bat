@echo off
echo Installing Python dependencies...
cd /d "%~dp0ai-service"
pip install -r requirements.txt
echo.
echo Installing Java dependencies...
cd /d "%~dp0"
mvn dependency:resolve
echo.
echo Setup complete!
echo.
echo Please configure your email settings in src\main\resources\application.yml
echo Then run start-ai-service.bat and start-java.bat
pause
