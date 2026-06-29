import urllib.request
import json
import time

def get_url(path):
    url = f"http://127.0.0.1:8000/api/v1{path}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {path}: {e}")
        return None

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
        print("Chat Error:", e)
        return None

print("Waiting for server...")
time.sleep(3)

print("\n--- Test 1: Fetch Dashboard Summary (Warms Cache) ---")
summary = get_url("/dashboard/summary")
if summary:
    print("Dashboard summary successfully fetched!")
    print("Total active assets in summary:", summary.get("total_active_assets"))
    print("Attention items count:", len(summary.get("attention_items", [])))

print("\n--- Test 2: Check Cache Status ---")
status = get_url("/intelligence/cache-status")
if status:
    print("Cache Status:", status)

print("\n--- Test 3: Chat - High Risk Assets ---")
res1 = send_chat("Show high-risk assets")
if res1:
    print("Answer:", res1["answer"])
    print("Tools Used:", res1["tools_used"])
    print("Sources count:", len(res1["sources"]))

print("\n--- Test 4: Chat - Follow-up Pronoun Heuristic ---")
if res1:
    history = [
        {"role": "user", "content": "Show high-risk assets"},
        {"role": "assistant", "content": res1["answer"]}
    ]
    res2 = send_chat("Why are they risky?", history)
    if res2:
        print("Answer:", res2["answer"])
        print("Tools Used:", res2["tools_used"])

print("\n--- Test 5: Chat - Healthy Assets Query ---")
res3 = send_chat("Which assets are in good condition?")
if res3:
    print("Answer:", res3["answer"])
    print("Tools Used:", res3["tools_used"])
