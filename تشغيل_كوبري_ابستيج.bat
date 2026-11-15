@echo off
chcp 65001 >nul
title Upstage Studio - OpenCode Local Gateway Bridge
cd /d "%~dp0"
echo =====================================================================
echo  🚀 تشغيل كوبري Upstage Studio لـ OpenCode (وضع Auto وبث مباشر)
echo  🌐 العنوان المحلي: http://127.0.0.1:8002/v1
echo =====================================================================
python upstage_opencode_bridge.py
pause

