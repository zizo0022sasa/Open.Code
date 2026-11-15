import requests, json

url = 'http://127.0.0.1:8002/v1/chat/completions'
headers = {'Content-Type': 'application/json'}

# 1. Test Titling Request
print("--- 1. Testing Instant Titling Request ---")
titling_payload = {
    "model": "claude-sonnet-5-5",
    "messages": [
        {
            "role": "system",
            "content": "You name conversations so the user can find them later in a list of past sessions.\n\nReply with only the title."
        },
        {
            "role": "user",
            "content": "Here is the first message of the conversation:\n\n<message>\nأنشئ ملف جديد في المسار C:\\Users\\USER\\Downloads\\zizo اسمه test_success.txt واكتب جواه:\n\"تم بنجاح تشغيل موديل Claude\"\n</message>\n\nReply with only the title."
        }
    ],
    "stream": False
}
r1 = requests.post(url, headers=headers, json=titling_payload, timeout=5)
print("Titling Response:", r1.json()["choices"][0]["message"]["content"])

# 2. Test Full OpenCode Agent Request with 25KB System Prompt and Tools
print("\n--- 2. Testing OpenCode Agent Request with Tools & Full System Prompt ---")
with open(r"D:\SMS\.hRhR_gateway-service\last_opencode_system_prompt.txt", "r", encoding="utf-8") as f:
    full_sys_prompt = f.read()

agent_payload = {
    "model": "claude-sonnet-5-5",
    "messages": [
        {"role": "system", "content": full_sys_prompt},
        {"role": "user", "content": "أنشئ ملف جديد في المسار C:\\Users\\USER\\Downloads\\zizo اسمه test_success.txt واكتب جواه:\n\"تم بنجاح تشغيل موديل Claude من Upstage للتعامل مع ملفات جهازي عبر OpenCode!\""}
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "write",
                "description": "Writes a file to the local filesystem, overwriting if one exists.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "The path of the file to write"},
                        "content": {"type": "string", "description": "The content of the file"}
                    },
                    "required": ["path", "content"]
                }
            }
        }
    ],
    "stream": False
}

r2 = requests.post(url, headers=headers, json=agent_payload, timeout=60)
print("Agent Status:", r2.status_code)
resp_json = r2.json()
print("Agent Response:")
print(json.dumps(resp_json, indent=2, ensure_ascii=False))

