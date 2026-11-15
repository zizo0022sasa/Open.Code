@echo off
chcp 65001 > nul
title Upstage Studio - Auto Pilot
color 0b

echo ========================================================
echo        ⚡ UPSTAGE STUDIO - الوضع التلقائي الذكي (Auto Pilot)
echo ========================================================
echo.
echo  1. شات تفاعلي أوتو (Auto Chat - أفضل موديل وأذونات تلقائية)
echo  2. مراقبة وتعديل ملف zizo\1 تلقائياً بمجرد الحفظ (Auto Watcher)
echo.
set /p choice="اختر الوضع (1 أو 2): "

if "%choice%"=="2" (
    echo.
    echo [*] جاري تشغيل مراقبة الملف: D:\SMS\.hRhR_gateway-service\zizo\1
    python "D:\SMS\.hRhR_gateway-service\.AAA_GGG_iii_VIBE_CODING_مجلد_المزودين\studio.upstage.ai\auto_pilot.py" --watch "D:\SMS\.hRhR_gateway-service\zizo\1"
) else (
    echo.
    echo [*] جاري تشغيل الشات التفاعلي Auto...
    python "D:\SMS\.hRhR_gateway-service\.AAA_GGG_iii_VIBE_CODING_مجلد_المزودين\studio.upstage.ai\auto_pilot.py"
)

pause

