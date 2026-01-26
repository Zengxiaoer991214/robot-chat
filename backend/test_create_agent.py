import json
import urllib.request
import urllib.error
import time

BASE_URL = "http://localhost:8000/api"

def test_create_agent():
    time.sleep(2)
    print(f"Testing Agent Creation at {BASE_URL}...")
    
    url = f"{BASE_URL}/agents"
    payload = {
        "name": "Test Agent with Key",
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "system_prompt": "You are a test agent.",
        "temperature": 0.7,
        "api_key_config": "sk-test-key-12345"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            print(f"Status Code: {status_code}")
            
            if status_code == 201:
                response_body = response.read().decode('utf-8')
                data = json.loads(response_body)
                print("Success!")
                print(f"Agent ID: {data.get('id')}")
                print(f"Name: {data.get('name')}")
                print(f"API Key Config: {data.get('api_key_config')}")
            else:
                print("Failed (unexpected status code)!")
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_agent()
