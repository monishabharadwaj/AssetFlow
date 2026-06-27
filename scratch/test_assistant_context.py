import urllib.request
import json

def send_chat(message, history=[]):
    url = "http://127.0.0.1:8000/api/v1/assistant/chat"
    data = {
        "message": message,
        "history": history
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            res = json.loads(response.read().decode())
            return res
    except Exception as e:
        print("Error:", e)
        return None

print("--- Test 1: High Risk Assets ---")
res1 = send_chat("Show high-risk assets")
if res1:
    print("Answer:", res1["answer"])
    print("Tools Used:", res1["tools_used"])
    print("Sources Count:", len(res1["sources"]))

print("\n--- Test 2: Follow-up Pronoun Heuristic ---")
# Simulate history
history = [
    {"role": "user", "content": "Show high-risk assets"},
    {"role": "assistant", "content": res1["answer"] if res1 else ""}
]
res2 = send_chat("Why are they risky?", history)
if res2:
    print("Answer:", res2["answer"])
    print("Tools Used:", res2["tools_used"])

print("\n--- Test 3: Healthy Assets Query ---")
res3 = send_chat("Which assets are in good condition?")
if res3:
    print("Answer:", res3["answer"])
    print("Tools Used:", res3["tools_used"])
