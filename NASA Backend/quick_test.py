import requests

# Test API authentication
try:
    # Test WITH API key
    response = requests.get(
        'http://127.0.0.1:8000/api/search/?query=test&limit=1',
        headers={'x-api-key': 'i31G2AKUI24gGq2oaw8w8sYGryZEjMArrJEjffcT'}
    )
    
    print(f"✅ API Test Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Results found: {data.get('count', 0)}")
        print("🎉 API Key authentication is working!")
    else:
        print(f"❌ Error: {response.text}")
        
    # Test WITHOUT API key (should fail)
    response_no_key = requests.get('http://127.0.0.1:8000/api/search/?query=test&limit=1')
    print(f"🔒 No API Key Status: {response_no_key.status_code} (should be 401)")
    
except Exception as e:
    print(f"💥 Error: {e}")