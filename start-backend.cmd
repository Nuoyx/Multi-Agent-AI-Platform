@echo off
start "Gateway" /D "%~dp0ALiceAI\backend\gateway" cmd.exe /k mvnw.cmd spring-boot:run
start "Auth" /D "%~dp0ALiceAI\backend\services\auth" cmd.exe /k mvnw.cmd spring-boot:run
