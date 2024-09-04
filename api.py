import requests
import json

def send(action, payload):
    # URL
    url = f'http://localhost/api/handler.php?h='+action
    print(url)
    # Headers
    headers = {'Content-Type': 'application/json'}

    try:
        # Send POST request
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        return {
            'status_code': response.status_code,
            'response_body': response.text
        }
    
    except requests.exceptions.RequestException as result:

      if 'error' in result:
         print(f"Error: {result['error']}")
      else:
         print(f"Status Code: {result['status_code']}")
         return(f"Response Body: {result['response_body']}")

    