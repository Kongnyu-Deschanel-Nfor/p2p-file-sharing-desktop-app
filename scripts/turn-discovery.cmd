@echo off
:: Check for administrative privileges
:: If not run as admin, relaunch the script as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges.
    echo Restarting with elevated permissions...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Enable Network Discovery Services
echo Enabling required services...
sc config FDResPub start= auto
net start FDResPub

sc config SSDPSRV start= auto
net start SSDPSRV

sc config upnphost start= auto
net start upnphost

:: Enable Network Discovery Firewall Rules
echo Enabling firewall rules for Network Discovery...
netsh advfirewall firewall set rule group="Network Discovery" new enable=yes

:: Check for errors and display success message
if %errorlevel% equ 0 (
    echo Network Discovery has been successfully enabled.
) else (
    echo There was an error enabling Network Discovery. Please check the settings manually.
)

pause
