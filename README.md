# 🌐 OpenCode Browser Gateway & Upstage Smart Bridge v3.5

كوبري محلي ذكي (Local AI Gateway Bridge) لربط محرر وبيئة عمل **OpenCode** بنماذج الذكاء الاصطناعي القوية في **Upstage Studio** (مثل Claude Sonnet 5.5, GPT-5.4, Solar Pro 4) مع محاكي استدعاء الأدوات الميداني (Tool Emulation Engine) لدعم قراءة وتعديل الملفات وتشغيل أوامر الشل مباشرة كـ Autonomous Agent.

---

## ⚡ المميزات الرئيسية (Key Architecture)

1. **محاكي الأدوات المتطور (Tool Emulation Engine v3.5):**
   - تحويل استجابات النماذج التي تقترح تشغيل أدوات إلى معيارية OpenAI `tool_calls` متوافقة 100% مع OpenCode.
   - حقن بروتوكول سيادي صريح في مقدمة البرومبت لإلزام الموديل بصيغة `tool_call`.
   - مرونة كاملة في معالجة مسارات الويندوز (`\t` Tab-Resilience) لمنع انهيار JSON.

2. **عازل التسمية اللحظي (Instant Zero-Latency Titling Resolver):**
   - الرد اللحظي خلال 1ms على طلبات التسمية المتوازية من OpenCode دون لمس السيرفر السحابي، لمنع تداخل الجلسات وتصادم `_active_chat_id`.

3. **دعم أوضاع الأذونات (Permission Modes):**
   - `bypass`: تفعيل وضع **`⚡ Skip permissions`** افتراضياً لتنفيذ الأدوات وأوامر الملفات فوراً دون مقاطعة.
   - `auto`: وضع متوازن يسأل فقط عند العمليات الحرجة.
   - `manual`: وضع الحذر الذي يطلب الإذن قبل كل خطوة.

4. **بث حي فائق السرعة (SSE Streaming):**
   - دعم كامل لبروتوكول Server-Sent Events مع تزويد حقول `index` الدقيقة لمصفوفات الأدوات.

---

## 🚀 البدء السريع (Quick Start)

### 1. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

### 2. ضبط الجلسة (Environment Variables):
انسخ ملف `.env.example` إلى `.env`:
```bash
cp .env.example .env
```
وقم بملء بيانات الجلسة:
- `UPSTAGE_SESSION_COOKIE`: كوكي الجلسة من `studio.upstage.ai`.
- `UPSTAGE_ORG_ID`: معرف المنظمة النشط.
- `UPSTAGE_PERMISSION_MODE`: الوضع المفضل (الافتراضي: `bypass` لتفعيل `Skip permissions`).

### 3. تشغيل الكوبري:
يمكنك التشغيل بنقرة واحدة عبر:
- `تشغيل_كوبري_ابستيج.bat`
أو من سطر الأوامر:
```bash
python upstage_opencode_bridge.py
```
سيعمل الخادم المحلي على: `http://127.0.0.1:8002/v1`

### 4. ربط OpenCode:
انسخ إعدادات `opencode.json` إلى مسار إعدادات OpenCode الخاص بك:
`%USERPROFILE%\.config\opencode\opencode.json`

---

## 🧪 التحقق والاختبار (Verification)

لاختبار استدعاء الأدوات والتأكد من استجابة Claude Sonnet 5.5 بـ `tool_calls` لأداة `write`:
```bash
python test_v35_bulletproof.py
```
المخرجات المتوقعة:
- استجابة سريعة لطلب التسمية في 1ms.
- إرجاع استدعاء أداة سليم مع `finish_reason: "tool_calls"`.

---

## 🔒 الأمان وحماية البيانات (Security Policy)
- الكوبري لا يقوم بحفظ أو تخزين أي مفاتيح أو أسرار داخل المستودع.
- كافة الجلسات والتوكنات تُدار حصرياً عبر متغيرات البيئة أو ملفات `.env` المحلية المستبعدة في `.gitignore`.
