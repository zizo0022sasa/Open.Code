@echo off
chcp 65001 >nul
title Upstage Auto Pilot - File Watcher (zizo/1)
cd /d "%~dp0"
echo =====================================================================
echo  ⚡ تشغيل Upstage Auto Pilot لمراقبة الملف zizo/1
echo  👁️ بمجرد تعديل وحفظ الملف (Ctrl+S)، الذكاء الاصطناعي هيعالجه فوراً!
echo =====================================================================
python "D:\SMS\.hRhR_gateway-service\.AAA_GGG_iii_VIBE_CODING_مجلد_المزودين\studio.upstage.ai\auto_pilot.py" --watch "D:\SMS\.hRhR_gateway-service\zizo\1"
pause

