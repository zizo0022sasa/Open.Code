@echo off
chcp 65001 >nul
title DeepSeek - OpenCode Local Gateway Bridge
cd /d "%~dp0"
echo =====================================================================
echo  🚀 تشغيل كوبري DeepSeek لـ OpenCode (جلسات مجانية وبث مباشر)
echo  🌐 العنوان المحلي: http://127.0.0.1:8001/v1
echo =====================================================================
python deepseek_opencode_bridge.py
pause

