#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════════
💬 UPSTAGE STUDIO CHAT — المحرك الذكي المتكامل v2.0
════════════════════════════════════════════════════════════════════════════════
المميزات:
  1. سحب وتحديث تلقائي لكتالوج الموديلات وقدرات التفكير كل 24 ساعة (أو فوري بـ --sync).
  2. دعم كامل لجميع مستويات جهد التفكير (Thinking Effort):
     [none, minimal, low, medium, high, xhigh, max]
  3. دعم كامل لأوضاع الأذونات الثلاثة (Permission Modes):
     - manual: Ask for permission (يسأل قبل كل خطوة)
     - auto: Auto (يتصرف بذكاء ويسأل عند الحاجة)
     - bypass: Skip permissions (تخطي الأذونات والتنفيذ الفوري المباشر)
  4. دفق مباشر لحظي (SSE Stream) فائق السرعة عبر Pure Requests بدون متصفح.
════════════════════════════════════════════════════════════════════════════════
"""

import urllib.request
import json
import os
import sys
import time
import argparse

# ضبط UTF-8 لويندوز
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, "accounts_upstage.json")
CATALOG_FILE = os.path.join(BASE_DIR, "upstage_models_capabilities.json")


def load_session():
    """تحميل الجلسة النشطة"""
    session_cookie = os.environ.get("UPSTAGE_SESSION", "")
    org_id = os.environ.get("UPSTAGE_ORG_ID", "")
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data and isinstance(data, list):
                    acc = data[-1]
                    session_cookie = acc.get("session", session_cookie)
                    org_id = acc.get("org_id", org_id)
        except Exception:
            pass
    return session_cookie, org_id


def sync_catalog(force: bool = False):
    """سحب وتحديث كتالوج الموديلات تلقائياً كل 24 ساعة أو عند الطلب"""
    if os.path.exists(CATALOG_FILE) and not force:
        age_hours = (time.time() - os.path.getmtime(CATALOG_FILE)) / 3600
        if age_hours < 24:
            try:
                with open(CATALOG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

    session_cookie, org_id = load_session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Cookie': f'session={session_cookie}; studio_active_org={org_id}',
        'Accept': 'application/json',
        'Referer': 'https://studio.upstage.ai/'
    }

    try:
        req = urllib.request.Request('https://studio.upstage.ai/api/chat/models', headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = json.loads(resp.read().decode('utf-8'))

        current_mode = "bypass"
        try:
            req_m = urllib.request.Request('https://studio.upstage.ai/api/grace/approval-mode', headers=headers)
            with urllib.request.urlopen(req_m, timeout=5) as resp_m:
                current_mode = json.loads(resp_m.read().decode('utf-8')).get("mode", "bypass")
        except Exception:
            pass

        catalog = {
            "metadata": {
                "last_synced_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "sync_interval": "auto_refresh_every_24_hours",
                "total_models": len(raw.get("models", [])),
                "current_active_permission_mode": current_mode,
                "permission_modes": {
                    "manual": {"ui_label": "Ask for permission", "description": "Asks before each action that needs approval"},
                    "auto": {"ui_label": "Auto", "description": "Proceeds when the request is clear, asks only when needed"},
                    "bypass": {"ui_label": "Skip permissions", "description": "Runs right away without asking"}
                }
            },
            "models": []
        }

        for m in raw.get("models", []):
            prof = m.get("requestProfile", {})
            catalog["models"].append({
                "id": m.get("id"),
                "name": m.get("label"),
                "is_default": m.get("isDefault", False),
                "execution_mode": m.get("executionMode", "MANAGED_ONLY"),
                "capabilities": m.get("capabilities", []),
                "thinking_effort": {
                    "default": prof.get("reasoningEffort", "none"),
                    "supported_levels": prof.get("reasoningEfforts", [])
                },
                "parameters": {
                    "supports_temperature": prof.get("supportsTemperature", False),
                    "supports_top_p": prof.get("supportsTopP", False),
                    "supports_forced_tool_choice": prof.get("supportsForcedToolChoice", False)
                }
            })

        with open(CATALOG_FILE, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        return catalog
    except Exception as e:
        if os.path.exists(CATALOG_FILE):
            with open(CATALOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        raise RuntimeError(f"تعذر تحديث كتالوج الموديلات: {e}")


def set_permission_mode(mode: str, headers: dict):
    """تعديل وضع الأذونات (manual, auto, bypass)"""
    if mode not in ["manual", "auto", "bypass"]:
        return
    try:
        req = urllib.request.Request(
            'https://studio.upstage.ai/api/grace/approval-mode',
            data=json.dumps({"mode": mode}).encode('utf-8'),
            headers=headers,
            method='PATCH'
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def ask_upstage(prompt: str, model: str = "gpt-5.4", thinking: str = None, permission: str = "bypass") -> str:
    session_cookie, org_id = load_session()
    cookie_str = f"NEXT_BROWSER_TIMEZONE=Africa%2FCairo; session={session_cookie}; studio_active_org={org_id}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Cookie': cookie_str,
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Origin': 'https://studio.upstage.ai',
        'Referer': 'https://studio.upstage.ai/'
    }

    # 1. تحديث وضع الأذونات إذا حُدد
    if permission in ["manual", "auto", "bypass"]:
        set_permission_mode(permission, headers)

    # 2. إعداد Response Settings لجهد التفكير (Thinking Effort)
    response_settings = {}
    if thinking and thinking.lower() != "default":
        response_settings["reasoningEffort"] = thinking.lower()

    # 3. إنشاء الشات
    create_payload = {
        "title": prompt[:30],
        "model": model,
        "responseSettings": response_settings,
        "graceApprovalMode": permission,
        "messages": [{"role": "user", "content": prompt}]
    }

    req1 = urllib.request.Request(
        'https://studio.upstage.ai/api/chats',
        data=json.dumps(create_payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    with urllib.request.urlopen(req1, timeout=15) as resp1:
        data1 = json.loads(resp1.read().decode('utf-8'))
        chat_id = data1.get("chat", {}).get("id")

    if not chat_id:
        raise RuntimeError("فشل إنشاء جلسة الشات على السيرفر")

    # 4. إرسال السؤال عبر مسار الدفق اللحظي /api/chat/pi
    headers_pi = dict(headers)
    headers_pi['x-studio-chat-entry-point'] = 'home_create'
    headers_pi['Accept'] = 'text/event-stream'

    payload_pi = {
        "chatId": chat_id,
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "responseSettings": response_settings,
        "locale": "ar",
        "timezone": "Africa/Cairo",
        "canvasEnabled": True
    }

    req2 = urllib.request.Request(
        'https://studio.upstage.ai/api/chat/pi',
        data=json.dumps(payload_pi).encode('utf-8'),
        headers=headers_pi,
        method='POST'
    )

    full_answer = []
    with urllib.request.urlopen(req2, timeout=60) as resp2:
        for line in resp2:
            line_str = line.decode('utf-8', errors='ignore').strip()
            if line_str.startswith("data: "):
                data_part = line_str[6:].strip()
                if data_part == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_part)
                    ctype = chunk.get("type")
                    if ctype in ["delta", "text"]:
                        content = chunk.get("content", "")
                        full_answer.append(content)
                        print(content, end="", flush=True)
                except Exception:
                    pass

    return "".join(full_answer)


def print_models_catalog(catalog):
    print("\n" + "=" * 65)
    print("📋 كشف كتالوج موديلات Upstage Studio وقدرات التفكير والأذونات")
    print("=" * 65)
    meta = catalog.get("metadata", {})
    print(f"🕒 آخر تحديث: {meta.get('last_synced_at')} (تحديث تلقائي كل 24 ساعة)")
    print(f"🔒 وضع الأذونات النشط: {meta.get('current_active_permission_mode')}\n")

    print("🛡️ أوضاع الأذونات المتاحة (Permission Modes):")
    for k, v in meta.get("permission_modes", {}).items():
        print(f"  • {k:8} ❯ {v['ui_label']:20} ({v['description']})")

    print("\n🤖 الموديلات المتاحة وأوضاع التفكير (Thinking Efforts):")
    for m in catalog.get("models", []):
        levels = ", ".join(m["thinking_effort"]["supported_levels"]) if m["thinking_effort"]["supported_levels"] else "بدون تحكم إضافي"
        def_level = m["thinking_effort"]["default"]
        print(f"  • [{m['id']:22}] ❯ {m['name']:20} | التفكير الافتراضي: {def_level:7} | الخيارات: [{levels}]")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upstage Studio Live AI Client v2.0")
    parser.add_argument("--prompt", type=str, default="", help="Question or prompt to ask")
    parser.add_argument("--model", type=str, default="gpt-5.4", help="Model ID (default: gpt-5.4)")
    parser.add_argument("--thinking", type=str, default=None, choices=["none", "minimal", "low", "medium", "high", "xhigh", "max"], help="Thinking effort level")
    parser.add_argument("--permission", type=str, default="bypass", choices=["manual", "auto", "bypass"], help="Permission mode: manual=Ask for permission, auto=Auto, bypass=Skip permissions")
    parser.add_argument("--list-models", action="store_true", help="List all available models and thinking capabilities")
    parser.add_argument("--sync", action="store_true", help="Force refresh models catalog from server")
    parser.add_argument("--edit-file", type=str, default=None, help="Path to local file to read, modify via AI, and save back")

    args = parser.parse_args()

    cat = sync_catalog(force=args.sync)

    if args.list_models:
        print_models_catalog(cat)
        sys.exit(0)

    # وضع تعديل الملفات المحلية
    if args.edit_file:
        if not os.path.exists(args.edit_file):
            print(f"❌ الملف غير موجود: {args.edit_file}")
            sys.exit(1)

        with open(args.edit_file, "r", encoding="utf-8", errors="ignore") as f:
            old_file_content = f.read()

        user_task = args.prompt or "قم بتصحيح وتنسيق محتوى هذا الملف وإكماله بالشكل الأنسب."
        combined_prompt = f"""أمامك محتوى ملف محلي من جهاز المستخدم:
```
{old_file_content}
```

المهمة المطلوبة لتعديل الملف:
{user_task}

تعليمات صارمة: أخرج فقط المحتوى النهائي المحدث للملف بدون أي شروحات أو مقدمات أو خاتمة، لكي يتم حفظه مباشرة في الملف."""

        print(f"\n📂 وضع تعديل الملف المحلي:")
        print(f"   📄 الملف المستهدف: {args.edit_file}")
        print(f"   🤖 الموديل: {args.model}")
        print(f"   🧠 جهد التفكير: {args.thinking or 'Default'}")
        print(f"   💬 المهمة: {user_task}")
        print("\n   [جاري توليد التعديل وحفظه]:\n")

        new_content = ask_upstage(combined_prompt, model=args.model, thinking=args.thinking, permission=args.permission)
        
        # تنظيف علامات الماركداون الكودية إذا وضعها الموديل كـ block كامل
        cleaned_content = new_content.strip()
        if cleaned_content.startswith("```") and cleaned_content.endswith("```"):
            lines = cleaned_content.splitlines()
            if len(lines) >= 2:
                cleaned_content = "\n".join(lines[1:-1]).strip()

        with open(args.edit_file, "w", encoding="utf-8") as f:
            f.write(cleaned_content + "\n")

        print(f"\n\n✅ تم تعديل وحفظ الملف محلياً بنجاح في: {args.edit_file}")
        print(f"🌐 كما تم إنشاء المحادثة وتسجيلها في متصفحك في Upstage Studio!\n")
        sys.exit(0)

    if not args.prompt:
        parser.print_help()
        sys.exit(0)

    if not args.prompt:
        parser.print_help()
        sys.exit(0)

    print(f"\n🚀 إرسال الطلب إلى Upstage Studio:")
    print(f"   🤖 الموديل: {args.model}")
    print(f"   🧠 جهد التفكير: {args.thinking or 'Default'}")
    print(f"   🛡️ وضع الإذن: {args.permission}")
    print(f"   💬 السؤال: {args.prompt}")
    print("\n   [الإجابة اللحظية]: ", end="", flush=True)

    ans = ask_upstage(args.prompt, model=args.model, thinking=args.thinking, permission=args.permission)
    print(f"\n\n✅ اكتملت الإجابة وظهرت في متصفحك بنجاح!\n")
