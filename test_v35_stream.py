import requests, json

url = 'http://127.0.0.1:8002/v1/chat/completions'
headers = {'Content-Type': 'application/json'}

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
    "stream": True
}

print("Testing streaming agent request...")
r = requests.post(url, headers=headers, json=agent_payload, stream=True, timeout=60)
for line in r.iter_lines():
    if line:
        txt = line.decode('utf-8')
        if 'tool_calls' in txt or 'finish_reason' in txt or 'content' in txt:
            print(txt[:180])

