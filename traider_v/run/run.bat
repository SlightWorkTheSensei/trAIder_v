@echo off
cd %~dp0
echo Compiling Go program...
go build -o run.exe run.go

if %ERRORLEVEL% neq 0 (
    echo Compilation failed!
    exit /b %ERRORLEVEL%
)

echo Starting Flask apps via Go...
start run.exe

:: Introduce a delay to ensure the server starts
timeout /t 15 > nul

echo Opening the server in the browser...
start "" http://127.0.0.1:8085

exit
