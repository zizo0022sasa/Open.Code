@echo off
chcp 65001 > nul
title 🤖 معدل وصانع الملفات الذكي - Upstage AI File Agent
color 0B

echo ======================================================================
echo           🤖 مشغل معدل الملفات الذكي الشامل (AI File Agent)
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

