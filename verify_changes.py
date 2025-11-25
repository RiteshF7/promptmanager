import urllib.request
import urllib.parse
import json
import threading
import time
import sys

BASE_URL = "http://127.0.0.1:5000/api/prompts"

def make_request(method, url, data=None):
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return 500, {}

def test_add_valid_prompt():
    print("Testing add valid prompt...", end=" ")
    status, _ = make_request('POST', BASE_URL, {"shortcut": "!valid", "text": "Valid Text"})
    if status == 201:
        print("PASS")
    else:
        print(f"FAIL ({status})")
        sys.exit(1)

def test_add_invalid_prompt():
    print("Testing add prompt with spaces...", end=" ")
    status, _ = make_request('POST', BASE_URL, {"shortcut": "!invalid space", "text": "Invalid"})
    if status == 400:
        print("PASS")
    else:
        print(f"FAIL ({status})")
        sys.exit(1)

def test_delete_prompt():
    print("Testing delete prompt...", end=" ")
    # Encode the shortcut for the URL
    shortcut = urllib.parse.quote("!valid")
    status, _ = make_request('DELETE', f"{BASE_URL}/{shortcut}")
    if status == 200:
        print("PASS")
    else:
        print(f"FAIL ({status})")
        sys.exit(1)

def concurrent_worker(i):
    status, _ = make_request('POST', BASE_URL, {"shortcut": f"!thread{i}", "text": f"Thread {i}"})
    if status != 201:
        print(f"Thread {i} failed with {status}")

def test_concurrency():
    print("Testing concurrency...", end=" ")
    threads = []
    for i in range(10):
        t = threading.Thread(target=concurrent_worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
        
    # Verify all were added
    status, prompts = make_request('GET', BASE_URL)
    count = sum(1 for k in prompts if k.startswith("!thread"))
    if count == 10:
        print("PASS")
    else:
        print(f"FAIL (Expected 10, got {count})")
    
    # Cleanup
    for i in range(10):
        shortcut = urllib.parse.quote(f"!thread{i}")
        make_request('DELETE', f"{BASE_URL}/{shortcut}")

if __name__ == "__main__":
    try:
        test_add_valid_prompt()
        test_add_invalid_prompt()
        test_delete_prompt()
        test_concurrency()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nFAIL: {e}")
