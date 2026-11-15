# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════════
🚀 Upstage Studio to OpenCode Smart AI Bridge v3.5 (Bulletproof Tool Engine)
════════════════════════════════════════════════════════════════════════════════
صمامات الأمان الميدانية المطبقة:
  1. Instant Zero-Latency Titling Resolver: عزل تام لطلبات التسمية ومنع سباق الجلسات.
  2. System Prompt Sanitizer & Override: نسف كود مود وتنصيب بروتوكول الأدوات المحلي الصارم.
  3. Windows Path Resilient JSON Parser: حماية مسارات الويندوز من كارثة الـ Tab والهروب الخاطئ.
  4. Multi-Turn Tool History Reconstructor: إعادة بناء كروت الأدوات لرسائل الـ Assistant لضمان استمرار الحوار.
  5. Strict OpenAI SSE Streaming Compliance: دعم كامل لـ index في مصفوفات الـ tool_calls المتدفقة.
════════════════════════════════════════════════════════════════════════════════
"""

import sys
import json
import time
import uuid
import re
import urllib.request
import pathlib
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# ضبط ترميز UTF-8 لويندوز
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os
import sys
import json
import time
import uuid
import re
import urllib.request
import pathlib
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# ضبط ترميز UTF-8 لويندوز
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def load_session():
    """تحميل الجلسة النشطة من متغيرات البيئة أو ملف .env أو التخزين المحلي الآمن"""
    session_cookie = os.environ.get("UPSTAGE_SESSION_COOKIE", "")
    org_id = os.environ.get("UPSTAGE_ORG_ID", "")

    # فحص ملف .env المحلي لو موجود
    env_file = pathlib.Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k == "UPSTAGE_SESSION_COOKIE" and not session_cookie:
                            session_cookie = v
                        elif k == "UPSTAGE_ORG_ID" and not org_id:
                            org_id = v
        except Exception:
            pass

    # فحص ملف حسابات Upstage محلي
    session_file = pathlib.Path(__file__).resolve().parent / "upstage_session.json"
    if session_file.exists():
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    session_cookie = session_cookie or data.get("session", "")
                    org_id = org_id or data.get("org_id", "")
                elif isinstance(data, list) and data:
                    session_cookie = session_cookie or data[-1].get("session", "")
                    org_id = org_id or data[-1].get("org_id", "")
        except Exception:
            pass

    # الاحتياطي من مجلد المزودين لو وجد محلياً
    if not session_cookie:
        legacy_acc = pathlib.Path(__file__).resolve().parent / ".AAA_GGG_iii_VIBE_CODING_مجلد_المزودين" / "studio.upstage.ai" / "accounts_upstage.json"
        if legacy_acc.exists():
            try:
                with open(legacy_acc, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        session_cookie = data[-1].get("session", "")
                        org_id = data[-1].get("org_id", "")
            except Exception:
                pass

    return session_cookie, org_id

def set_permission_mode(mode: str, headers: dict):
    """تعديل وضع الأذونات (manual, auto, bypass) - bypass = ⚡ Skip permissions"""
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

app = FastAPI(title="Upstage Studio Smart Bridge", version="3.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_REGISTRY = {
    "auto": {"id": "auto", "name": "⚡ Upstage Auto", "internal_model": "auto"},
    "gpt-5.4": {"id": "gpt-5.4", "name": "🧠 GPT-5.4 (Thinking)", "internal_model": "gpt-5.4"},
    "claude-sonnet-5-5": {"id": "claude-sonnet-5-5", "name": "🎭 Claude Sonnet 5.5", "internal_model": "claude-sonnet-5-5"},
    "gemini-3.1-pro-preview": {"id": "gemini-3.1-pro-preview", "name": "🌐 Gemini 3.1 Pro", "internal_model": "gemini-3.1-pro-preview"},
    "solar-pro4": {"id": "solar-pro4", "name": "☀️ Solar Pro 4", "internal_model": "solar-pro4"},
    "grok-4.7": {"id": "grok-4.7", "name": "🚀 Grok 4.7", "internal_model": "grok-4.7"}
}

_active_chat_id = None
_last_messages_count = 0


@app.api_route("/v1/session/reset", methods=["GET", "POST"])
def reset_session():
    """تصفير المحادثة وبدء شات جديد فوراً"""
    global _active_chat_id, _last_messages_count
    _active_chat_id = None
    _last_messages_count = 0
    return {"status": "ok", "message": "تم تصفير محادثة Upstage Studio بنجاح! ✅"}


# ─────────────────────────────────────────────────────────────────────────────
# 🛡️ 1. كاشف ومعالج طلبات التسمية الفوري (Anti-Race Condition Titling)
# ─────────────────────────────────────────────────────────────────────────────

def is_titling_request(messages: list) -> bool:
    """كشف إذا كان الطلب عبارة عن طلب تسمية جانبي من OpenCode"""
    for msg in messages:
        c = str(msg.get("content", ""))
        if "You name conversations so the user can find them later" in c:
            return True
        if "Reply with only the title" in c:
            return True
    return False


def generate_instant_title(messages: list) -> str:
    """استخراج عنوان ذكي ونظيف في 1ms بدون إزعاج Upstage Studio"""
    user_text = ""
    for msg in messages:
        if msg.get("role") == "user":
            user_text = str(msg.get("content", ""))
            break

    # فحص وسم <message>...</message>
    m = re.search(r'<message>(.*?)</message>', user_text, re.DOTALL)
    raw = m.group(1).strip() if m else user_text.strip()

    # تنظيف الأكواد والسطور الزائدة
    lines = [line.strip() for line in raw.split('\n') if line.strip() and not line.strip().startswith('```')]
    first_line = lines[0] if lines else "Coding Session"
    first_line = re.sub(r'["\'`\(\)\[\]\{\}]', '', first_line).strip()

    # مسح كلمات البداية المعتادة
    first_line = re.sub(r'^(من فضلك|لو سمحت|ممكن|قم بـ|اعمل|أنشئ|انشئ|please|can you|could you)\s+', '', first_line, flags=re.IGNORECASE).strip()
    words = first_line.split()
    if len(words) > 5:
        return " ".join(words[:5])
    return first_line or "Coding Task"


# ─────────────────────────────────────────────────────────────────────────────
# 🛠️ 2. محلل JSON واستدعاء الأدوات المقاوم لأخطاء مسارات الويندوز
# ─────────────────────────────────────────────────────────────────────────────

def parse_tool_json(raw_text: str):
    """تحليل واستخراج JSON استدعاء الأداة بأمان تام مع معالجة مسارات الويندوز"""
    # صمام 1: إصلاح مسارات محركات أقراص الويندوز (مثل C:\Users) قبل أن تتحول \t إلى Tab
    safe_text = re.sub(
        r'([A-Za-z]:\\[^"\'\n\r]+)',
        lambda m: m.group(1).replace('\\', '/'),
        raw_text
    )

    try:
        return json.loads(safe_text)
    except Exception:
        pass

    # صمام 2: إصلاح أي باك سلاش منفرد غير مهروب
    try:
        fixed = re.sub(r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', safe_text)
        return json.loads(fixed)
    except Exception:
        pass

    # صمام 3: محاولة أخيرة بالنص الأصلي
    try:
        return json.loads(raw_text)
    except Exception:
        pass

    return None


def parse_emulated_tools(full_text: str, declared_tools: list = None):
    """استخراج استدعاءات الأدوات والتأكد أنها أدوات حقيقية معلنة وليست JSON عشوائي"""
    valid_tool_names = set()
    if declared_tools:
        for t in declared_tools:
            name = t.get("function", {}).get("name")
            if name:
                valid_tool_names.add(name)

    pattern = re.compile(r'```(?:tool_call|tool-call|tool_calls|json)?\s*?\n(.*?)```', re.DOTALL)
    matches = list(pattern.finditer(full_text))
    tool_calls = []
    first_tool_start = -1

    for m in matches:
        raw_content = m.group(1).strip()
        parsed = parse_tool_json(raw_content)
        if not parsed:
            continue

        items = parsed if isinstance(parsed, list) else [parsed]
        for item in items:
            if not isinstance(item, dict):
                continue
            t_name = item.get("name")
            if not t_name:
                continue

            # التحقق إن كانت الأداة معلنة رسمياً لمنع الالتباس
            if valid_tool_names and t_name not in valid_tool_names:
                continue

            if first_tool_start == -1:
                first_tool_start = m.start()

            t_args = item.get("arguments", {})
            args_str = json.dumps(t_args, ensure_ascii=False) if isinstance(t_args, dict) else str(t_args)
            tool_calls.append({
                "id": f"call_{uuid.uuid4().hex[:12]}",
                "type": "function",
                "function": {
                    "name": t_name,
                    "arguments": args_str
                }
            })

    clean_text = full_text[:first_tool_start].strip() if first_tool_start != -1 else full_text.strip()
    return clean_text, tool_calls


# ─────────────────────────────────────────────────────────────────────────────
# 🧹 3. مطهر ومعد برومبت النظام الفائق (Sanitizer & Preemption Engine)
# ─────────────────────────────────────────────────────────────────────────────

def build_authoritative_system_prompt(raw_system: str, tools: list) -> str:
    """بناء تعليمات نظام سيادية وموجزة تلغي أي قيود ويب وتلزم الموديل بتنفيذ الأدوات محلياً"""
    # 1. استخراج سياق البيئة والمسار الحالي فقط
    env_match = re.search(r'<env>.*?</env>', raw_system, re.DOTALL)
    env_block = env_match.group(0) if env_match else ""

    # 2. بناء كتالوج الأدوات المتاحة الصريح
    tool_lines = []
    if tools:
        for t in tools:
            fn = t.get("function", {})
            name = fn.get("name", "")
            desc = fn.get("description", "")
            params = fn.get("parameters", {}).get("properties", {})
            param_list = ", ".join(params.keys()) if params else "none"
            tool_lines.append(f"- `{name}`: {desc} (Parameters: {param_list})")
    tools_str = "\n".join(tool_lines) if tool_lines else "- read, write, edit, shell, grep, glob"

    # 3. صياغة التعليمات السيادية
    system_text = f"""You are OpenCode Autonomous Coding Agent executing directly on the user's local Windows workstation.

══════════════════════════════════════════════════════════════
🚨 CRITICAL OPERATIONAL DIRECTIVES (STRICT COMPLIANCE REQUIRED):
1. LOCAL WORKSTATION ACCESS: You have FULL filesystem and shell execution rights via OpenCode local harness. NEVER state you lack local permissions or that you are an AI assistant in a browser.
2. TOOL CALL PROTOCOL: API function calling is emulated via Markdown blocks. To execute ANY action (read, write, edit, shell), you MUST output your call in this EXACT syntax:
```tool_call
{{
  "name": "<tool_name>",
  "arguments": {{
    "<param_key>": "<param_value>"
  }}
}}
```
3. EXECUTION LOOP:
   - Provide brief technical reasoning, then output the ```tool_call block.
   - STOP immediately after closing the ```tool_call block. Do NOT simulate or fabricate results.
   - The harness executes the tool on Windows and returns: `[Tool Output (<call_id>)]:\n<result>`.
   - Iterate tool calls turn-by-turn until the user request is 100% completed.
   - For creating files, use `write`. For surgical edits on existing files, use `edit`.
══════════════════════════════════════════════════════════════

AVAILABLE LOCAL TOOLS:
{tools_str}

{f"LOCAL ENVIRONMENT:\n{env_block}" if env_block else ""}
"""
    return system_text.strip()


def extract_user_and_system(messages: list, tools: list = None):
    """استخراج وترتيب الرسائل مع إعادة بناء تاريخ الـ tool_calls والتعامل مع الأدوات"""
    clean_messages = []
    user_queries = []
    raw_system_content = ""

    # استخراج الـ system الأصلي إن وجد
    for msg in messages:
        if msg.get("role") == "system":
            raw_system_content = str(msg.get("content", ""))
            break

    authoritative_system = build_authoritative_system_prompt(raw_system_content, tools)
    clean_messages.append({"role": "system", "content": authoritative_system})

    pending_tool_outputs = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            text_pieces = [p.get("text", "") for p in content if isinstance(p, dict) and "text" in p]
            content = " ".join(text_pieces)
        content = str(content).strip()

        if role == "system":
            continue

        elif role == "user":
            if pending_tool_outputs:
                merged_tools = "\n\n".join(pending_tool_outputs)
                content = f"{merged_tools}\n\n{content}".strip()
                pending_tool_outputs.clear()

            user_queries.append(content)
            clean_messages.append({"role": "user", "content": content})

        elif role == "assistant":
            if pending_tool_outputs:
                merged_tools = "\n\n".join(pending_tool_outputs)
                clean_messages.append({"role": "user", "content": merged_tools})
                user_queries.append(merged_tools)
                pending_tool_outputs.clear()

            # 🛠️ صمام أمان حاسم: إعادة بناء استدعاءات الأدوات في رسالة الـ Assistant
            tool_calls = msg.get("tool_calls", [])
            assistant_content = content
            if tool_calls:
                blocks = []
                for tc in tool_calls:
                    fn = tc.get("function", {})
                    fn_name = fn.get("name", "")
                    raw_args = fn.get("arguments", "{}")
                    try:
                        p_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except Exception:
                        p_args = raw_args
                    card = json.dumps({"name": fn_name, "arguments": p_args}, indent=2, ensure_ascii=False)
                    blocks.append(f"```tool_call\n{card}\n```")

                tools_payload = "\n".join(blocks)
                assistant_content = f"{assistant_content}\n\n{tools_payload}".strip() if assistant_content else tools_payload

            clean_messages.append({"role": "assistant", "content": assistant_content or "Executing tool..."})

        elif role == "tool":
            tool_id = msg.get("tool_call_id", "")
            tool_text = f"[Tool Output ({tool_id})]:\n{content}"
            pending_tool_outputs.append(tool_text)

    # إذا انتهت الرسائل بمخرجات أدوات
    if pending_tool_outputs:
        merged_tools = "\n\n".join(pending_tool_outputs)
        clean_messages.append({"role": "user", "content": merged_tools})
        user_queries.append(merged_tools)
        pending_tool_outputs.clear()

    latest_query = user_queries[-1] if user_queries else "محادثة جديدة"
    return latest_query, clean_messages


# ─────────────────────────────────────────────────────────────────────────────
# 🌐 4. محرك الدفق والتواصل مع Upstage Studio
# ─────────────────────────────────────────────────────────────────────────────

def stream_upstage_smart(messages: list, model: str = "auto", permission: str = None, tools: list = None):
    """دفق الرد بذكاء مع دعم إكمال نفس الشات أو فتح شات جديد"""
    global _active_chat_id

    if not permission:
        permission = os.environ.get("UPSTAGE_PERMISSION_MODE", "bypass")

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

    if permission in ["manual", "auto", "bypass"]:
        set_permission_mode(permission, headers)

    latest_query, clean_msgs = extract_user_and_system(messages, tools=tools)

    # 1. إذا لم يكن هناك شات نشط: ننشئ شات جديد
    if not _active_chat_id:
        chat_title = latest_query[:45].replace("\n", " ").strip() or "محادثة جديدة"
        print(f"\n🆕 [Upstage Smart Bridge] فتح شات جديد بعنوان: [{chat_title}]")

        create_payload = {
            "title": chat_title,
            "model": model,
            "responseSettings": {},
            "graceApprovalMode": permission,
            "messages": clean_msgs
        }

        req_create = urllib.request.Request(
            'https://studio.upstage.ai/api/chats',
            data=json.dumps(create_payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req_create, timeout=15) as resp:
            data_res = json.loads(resp.read().decode('utf-8'))
            _active_chat_id = data_res.get("chat", {}).get("id")

        if not _active_chat_id:
            raise RuntimeError("تعذر إنشاء شات جديد على Upstage Studio")
        entry_point = "home_create"
    else:
        print(f"\n🔗 [Upstage Smart Bridge] إكمال في نفس الشات: [{_active_chat_id}]")
        print(f"💬 السؤال المرسل: {latest_query[:60]}...")
        entry_point = "chat"

    # 2. إرسال السؤال عبر مسار الدفق اللحظي /api/chat/pi
    headers_pi = dict(headers)
    headers_pi['x-studio-chat-entry-point'] = entry_point
    headers_pi['Accept'] = 'text/event-stream'

    payload_pi = {
        "chatId": _active_chat_id,
        "messages": clean_msgs,
        "model": model,
        "responseSettings": {},
        "locale": "ar",
        "timezone": "Africa/Cairo",
        "canvasEnabled": True
    }

    req_pi = urllib.request.Request(
        'https://studio.upstage.ai/api/chat/pi',
        data=json.dumps(payload_pi).encode('utf-8'),
        headers=headers_pi,
        method='POST'
    )

    with urllib.request.urlopen(req_pi, timeout=60) as resp2:
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
                        if content:
                            yield content
                except Exception:
                    pass


# ─────────────────────────────────────────────────────────────────────────────
# 🚀 5. نقطة الاتصال الرئيسية المتوافقة مع OpenAI API
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/v1/models")
def list_models():
    now = int(time.time())
    data = []
    for m_id, m_info in MODELS_REGISTRY.items():
        data.append({
            "id": m_id,
            "object": "model",
            "created": now,
            "owned_by": "upstage-studio-session",
            "name": m_info["name"]
        })
    return {"object": "list", "data": data}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    global _active_chat_id, _last_messages_count
    try:
        body = await request.json()
    except Exception:
        raw = await request.body()
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": {"message": f"Invalid JSON: {str(e)}", "type": "bad_request"}})

    raw_model = body.get("model", "auto").lower()
    messages = body.get("messages", [])
    tools = body.get("tools", [])
    stream = body.get("stream", False)
    req_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created_time = int(time.time())

    # 🛡️ صمام 1: معالجة طلبات الـ Titling فورياً بدون تلويث الجلسة الأساسية
    if is_titling_request(messages):
        title = generate_instant_title(messages)
        print(f"🏷️ [Titling Handler] تم استخراج عنوان الشات فورياً: [{title}]")
        if stream:
            def title_stream():
                chunk = {"id": req_id, "object": "chat.completion.chunk", "created": created_time, "model": raw_model, "choices": [{"index": 0, "delta": {"content": title}, "finish_reason": None}]}
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                done = {"id": req_id, "object": "chat.completion.chunk", "created": created_time, "model": raw_model, "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
                yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(title_stream(), media_type="text/event-stream")
        else:
            return JSONResponse({"id": req_id, "object": "chat.completion", "created": created_time, "model": raw_model, "choices": [{"index": 0, "message": {"role": "assistant", "content": title}, "finish_reason": "stop"}]})

    # استخراج آخر رسالة
    last_msg = messages[-1].get("content", "") if messages else ""
    if isinstance(last_msg, list):
        last_msg = " ".join([p.get("text", "") for p in last_msg if isinstance(p, dict) and "text" in p])
    last_msg_str = str(last_msg).strip()

    # صمام 2: أمر التصفير اليدوي الصريح
    norm = last_msg_str.lower().lstrip("/").strip()
    if norm in ["new", "reset", "clear", "جديد", "شات جديد", "محادثة جديدة", "تصفير"]:
        reset_session()
        notice = "✨ **تم تصفير محادثة Upstage Studio بنجاح!** 🚀\n💬 تفضل بسؤالك الجديد وسننشئ شات نظيف."
        return JSONResponse({"id": req_id, "object": "chat.completion", "created": created_time, "model": raw_model, "choices": [{"index": 0, "message": {"role": "assistant", "content": notice}, "finish_reason": "stop"}]})

    # صمام 3: كشف بدء جلسة عمل جديدة حقيقية في OpenCode
    current_count = len(messages)
    if current_count <= 2 or current_count < _last_messages_count:
        print(f"\n🔄 [Upstage Smart Bridge] تم اكتشاف New Session في OpenCode (عدد الرسائل: {current_count})")
        _active_chat_id = None

    _last_messages_count = current_count

    # مطابقة الموديل المطلوب
    target_info = MODELS_REGISTRY.get(raw_model, MODELS_REGISTRY["auto"])
    target_model_id = target_info["internal_model"]

    target_permission = os.environ.get("UPSTAGE_PERMISSION_MODE", "bypass")

    if stream:
        def sse_generator():
            try:
                full_text_pieces = []
                in_tool_block = False

                for piece in stream_upstage_smart(messages, model=target_model_id, permission=target_permission, tools=tools):
                    full_text_pieces.append(piece)
                    current_so_far = "".join(full_text_pieces)

                    # منع تسريب كود استدعاء الأداة لواجهة المستخدم
                    if "```tool" in current_so_far:
                        in_tool_block = True

                    if not in_tool_block:
                        chunk = {
                            "id": req_id,
                            "object": "chat.completion.chunk",
                            "created": created_time,
                            "model": target_info["id"],
                            "choices": [{"index": 0, "delta": {"content": piece}, "finish_reason": None}]
                        }
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

                entire_resp = "".join(full_text_pieces)
                clean_text, emulated_tools = parse_emulated_tools(entire_resp, declared_tools=tools)

                if emulated_tools:
                    print(f"⚡ [Tool Emulator] تم اكتشاف {len(emulated_tools)} استدعاء أداة وتحويله لـ OpenCode!")
                    # ضبط معيارية OpenAI: إضافة index لكل أداة
                    indexed_tools = []
                    for idx, t in enumerate(emulated_tools):
                        t_copy = dict(t)
                        t_copy["index"] = idx
                        indexed_tools.append(t_copy)

                    tool_chunk = {
                        "id": req_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": target_info["id"],
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "tool_calls": indexed_tools
                            },
                            "finish_reason": "tool_calls"
                        }]
                    }
                    yield f"data: {json.dumps(tool_chunk, ensure_ascii=False)}\n\n"
                else:
                    done_chunk = {
                        "id": req_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": target_info["id"],
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
                    }
                    yield f"data: {json.dumps(done_chunk, ensure_ascii=False)}\n\n"

                yield "data: [DONE]\n\n"
            except Exception as e:
                err_chunk = {"error": {"message": str(e), "type": "server_error"}}
                yield f"data: {json.dumps(err_chunk)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(sse_generator(), media_type="text/event-stream")
    else:
        try:
            full_text = []
            for piece in stream_upstage_smart(messages, model=target_model_id, permission=target_permission, tools=tools):
                full_text.append(piece)
            entire_resp = "".join(full_text)
            clean_text, emulated_tools = parse_emulated_tools(entire_resp, declared_tools=tools)

            if emulated_tools:
                print(f"⚡ [Tool Emulator] تم اكتشاف {len(emulated_tools)} استدعاء أداة!")
                return JSONResponse({
                    "id": req_id,
                    "object": "chat.completion",
                    "created": created_time,
                    "model": target_info["id"],
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": clean_text,
                            "tool_calls": emulated_tools
                        },
                        "finish_reason": "tool_calls"
                    }]
                })
            else:
                return JSONResponse({
                    "id": req_id,
                    "object": "chat.completion",
                    "created": created_time,
                    "model": target_info["id"],
                    "choices": [{
                        "index": 0,
                        "message": {"role": "assistant", "content": entire_resp},
                        "finish_reason": "stop"
                    }]
                })
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": {"message": str(e), "type": "server_error"}})


if __name__ == "__main__":
    print("═" * 70)
    print("🚀 تشغيل كوبري Upstage Studio الذكي الموحد (Bulletproof v3.5)")
    print("🌐 الاستماع على: http://127.0.0.1:8002/v1")
    print("⚡ صمامات أمان Titling و Windows Paths و Tool Reconstructing نشطة")
    print("═" * 70)
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="info")
