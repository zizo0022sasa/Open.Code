@echo off
chcp 65001 > nul
title 🛡️ بيئة عمل أنتيجرافيتي المعزولة - AI File Agent
color 0A

echo ======================================================================
echo       🛡️ بيئة عمل أنتيجرافيتي المعزولة (Isolated AI Workspace)
echo   (معزول تماماً عن جلسة الوكيل الآخر - DeepSeek لتجنب أي تعارض)
echo ======================================================================
echo.

if "%~1"=="" (
    python "%~dp0file_editor_agent.py"
) else (
    echo تم استلام الملف: %~1
    python "%~dp0file_editor_agent.py" "%~1"
)

echo.
pause

