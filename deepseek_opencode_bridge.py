# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════════
🚀 DeepSeek to OpenCode Smart AI Bridge v4.0 (Unified Auto-Threaded)
════════════════════════════════════════════════════════════════════════════════
المميزات المبتكرة:
  1. الاستمرار التلقائي في نفس المحادثة (Auto Continuation):
     - يكمل في نفس الشات على DeepSeek تلقائياً بدون ما تحتاج تبدل بين موديلات.
     - لا يعيد إرسال System Instructions في كل رسالة؛ بيبعتها أول مرة فقط، والرسائل التالية يرسل سؤالك الجديد فقط.
  2. تسمية نظيفة للشات في DeepSeek Web:
     - يضع سؤالك الفعلي في أول البرومبت حتى يسمى الشات بموضوعك، وليس بـ [System Instructions].
  3. تصفير وبدء شات جديد بذكاء:
     - عبر كتابة `/new` أو `/reset` مباشرة في الشات.
     - أو تلقائياً عند بدء New Session في OpenCode.
     - أو عبر الرابط السريع: http://127.0.0.1:8001/v1/session/reset
  4. دعم التفكير العميق (DeepThink) والبحث الحي (Live Search) والبث المباشر (SSE).
════════════════════════════════════════════════════════════════════════════════
"""

import sys
import time
import uuid
import json
import pathlib
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# إضافة مسار محرك DeepSeek
DEEPSEEK_DIR = pathlib.Path(__file__).resolve().parent / ".AAA_GGG_iii_VIBE_CODING_مجلد_المزودين" / "بعدين" / "Deep Seek" / "DeepSeek"
if str(DEEPSEEK_DIR) not in sys.path:
    sys.path.insert(0, str(DEEPSEEK_DIR))

from deepseek_chat import DeepSeekChat, DeepSeekConfig

app = FastAPI(title="DeepSeek OpenCode Smart Bridge", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_REGISTRY = {
    "deepseek-v4-pro": {
        "id": "deepseek-v4-pro",
        "name": "🔥 DeepSeek V4 Pro (المحادثة الذكية المتكاملة)",
        "thinking": True,
        "search": True,
        "model_type": "default"
    },
    "deepseek-v4-pro-sticky": {
        "id": "deepseek-v4-pro-sticky",
        "name": "🔗 DeepSeek V4 Pro (إكمال المحادثة)",
        "thinking": True,
        "search": True,
        "model_type": "default"
    }
}

# عميل موحد ذكي للمحادثات
_smart_client = None
_last_messages_count = 0


def get_client() -> DeepSeekChat:
    global _smart_client
    if _smart_client is None:
        _smart_client = DeepSeekChat(DeepSeekConfig(
            model_type="default",
            thinking=True,
            search=True,
            multi_turn=True
        ))
    return _smart_client


@app.api_route("/v1/session/reset", methods=["GET", "POST"])
def reset_session():
    """تصفير المحادثة وبدء شات جديد فوراً"""
    global _smart_client, _last_messages_count
    if _smart_client:
        _smart_client.clear_history()
    _last_messages_count = 0
    return {"status": "ok", "message": "تم تصفير المحادثة وبدء جلسة جديدة نظيفة على DeepSeek بنجاح! ✅"}


def extract_user_and_system(messages: list):
    """استخراج سؤال المستخدم الحقيقي وتعليمات النظام بترتيب ذكي لتسمية الشات"""
    system_parts = []
    user_parts = []
    history_dialogue = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            text_pieces = [p.get("text", "") for p in content if isinstance(p, dict) and "text" in p]
            content = " ".join(text_pieces)
        content = str(content).strip()

        if role == "system":
            system_parts.append(content)
        elif role == "user":
            user_parts.append(content)
            history_dialogue.append(f"User: {content}")
        elif role == "assistant":
            history_dialogue.append(f"Assistant: {content}")

    latest_user_query = user_parts[-1] if user_parts else "محادثة جديدة"

    # نضع سؤال المستخدم أولاً لكي يسمي DeepSeek الشات باسم السؤال وليس باسم [System Instructions]
    formatted_prompt = f"الموضوع: {latest_user_query}\n\n"
    if system_parts:
        formatted_prompt += f"[System Instructions]:\n" + "\n".join(system_parts) + "\n\n"
    if len(history_dialogue) > 1:
        formatted_prompt += "[Conversation Context]:\n" + "\n".join(history_dialogue[:-1]) + "\n\n"
    formatted_prompt += f"[Current Task]:\n{latest_user_query}"

    return latest_user_query, formatted_prompt


@app.get("/v1/models")
def list_models():
    now = int(time.time())
    data = []
    for m_id, m_info in MODELS_REGISTRY.items():
        data.append({
            "id": m_id,
            "object": "model",
            "created": now,
            "owned_by": "deepseek-smart-session",
            "name": m_info["name"]
        })
    return {"object": "list", "data": data}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    global _last_messages_count
    try:
        body = await request.json()
    except Exception:
        raw = await request.body()
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": {"message": f"Invalid JSON: {str(e)}", "type": "bad_request"}})

    messages = body.get("messages", [])
    stream = body.get("stream", False)
    req_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created_time = int(time.time())

    # استخراج آخر رسالة من المستخدم
    last_msg = messages[-1].get("content", "") if messages else ""
    if isinstance(last_msg, list):
        last_msg = " ".join([p.get("text", "") for p in last_msg if isinstance(p, dict) and "text" in p])
    last_msg_str = str(last_msg).strip()

    # 1. فحص أمر تصفير الشات من المستخدم (بدون سلاش أو بسلاش)
    norm = last_msg_str.lower().lstrip("/").strip()
    if norm in ["new", "reset", "clear", "جديد", "شات جديد", "محادثة جديدة", "ابدا جديد", "ابدأ جديد", "تصفير"]:
        reset_session()
        reset_notice = (
            "✨ **تم تصفير المحادثة وبدء شات جديد نظيف على DeepSeek بنجاح!** 🚀\n\n"
            "💬 تفضل بسؤالك الجديد، وسيتم إنشاء محادثة جديدة في متصفحك مخصصة لموضوعك."
        )
        if stream:
            def reset_stream():
                chunk = {
                    "id": req_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": "deepseek-v4-pro",
                    "choices": [{"index": 0, "delta": {"content": reset_notice}, "finish_reason": None}]
                }
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                done = {"id": req_id, "object": "chat.completion.chunk", "created": created_time, "model": "deepseek-v4-pro", "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
                yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(reset_stream(), media_type="text/event-stream")
        else:
            return JSONResponse({
                "id": req_id,
                "object": "chat.completion",
                "created": created_time,
                "model": "deepseek-v4-pro",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": reset_notice}, "finish_reason": "stop"}]
            })

    client = get_client()

    # 2. الكشف التلقائي الذكي: هل المستخدم بدأ New Session في OpenCode؟
    # إذا كان عدد الرسائل الحالي أقل من السابق أو رسالة أولى فقط (<= 2)، نعتبرها بداية شات جديد
    current_count = len(messages)
    if current_count <= 2 or current_count < _last_messages_count:
        print(f"\n🔄 [Smart Bridge] تم اكتشاف بداية محادثة جديدة في OpenCode (عدد الرسائل: {current_count})")
        client.clear_history()

    _last_messages_count = current_count

    # 3. تحديد البرومبت: هل نكمل في نفس الشات أم نبدأ سياق جديد؟
    if client._session_id and client._last_msg_id and current_count > 2:
        # إكمال في نفس المحادثة: نرسل سؤال المستخدم الأخير فقط!
        prompt = last_msg_str
        print(f"\n🔗 [Smart Bridge] إكمال في نفس المحادثة على DeepSeek (Session: {client._session_id[:12]}...)")
        print(f"💬 السؤال المرسل: {prompt[:80]}...")
    else:
        # أول رسالة في الشات: نؤسس الشات مع وضع عنوان السؤال في البداية لتسمية الشات في المتصفح
        user_query, prompt = extract_user_and_system(messages)
        print(f"\n🆕 [Smart Bridge] تأسيس شات جديد على DeepSeek بعنوان: [{user_query[:50]}]")

    if stream:
        def sync_event_generator():
            try:
                for chunk_type, val in client.chat_stream(prompt):
                    if not val:
                        continue
                    if chunk_type == "think":
                        chunk = {
                            "id": req_id,
                            "object": "chat.completion.chunk",
                            "created": created_time,
                            "model": "deepseek-v4-pro",
                            "choices": [{"index": 0, "delta": {"reasoning_content": val}, "finish_reason": None}]
                        }
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    elif chunk_type == "content":
                        chunk = {
                            "id": req_id,
                            "object": "chat.completion.chunk",
                            "created": created_time,
                            "model": "deepseek-v4-pro",
                            "choices": [{"index": 0, "delta": {"content": val}, "finish_reason": None}]
                        }
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

                done_chunk = {
                    "id": req_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": "deepseek-v4-pro",
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
                }
                yield f"data: {json.dumps(done_chunk, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                err_chunk = {"error": {"message": str(e), "type": "server_error"}}
                yield f"data: {json.dumps(err_chunk)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(sync_event_generator(), media_type="text/event-stream")
    else:
        try:
            full_content = client.chat(prompt)
            return JSONResponse({
                "id": req_id,
                "object": "chat.completion",
                "created": created_time,
                "model": "deepseek-v4-pro",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": full_content},
                    "finish_reason": "stop"
                }]
            })
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": {"message": str(e), "type": "server_error"}})


if __name__ == "__main__":
    print("═" * 70)
    print("🚀 تشغيل كوبري DeepSeek الذكي الموحد (Smart Auto-Threaded Bridge v4.0)")
    print("🌐 الاستماع على: http://127.0.0.1:8001/v1")
    print("═" * 70)
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
