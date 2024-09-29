import http.client
import json
import socket
import uuid
import requests
import webSocket


def fetch_market_data(api_key, auth_token, local_ip, public_ip, mac_address, token):
    conn = http.client.HTTPSConnection("apiconnect.angelone.in")
    payload = json.dumps({
        "mode": "FULL",
        "exchangeTokens": {
            "NFO": [token]
        }
    })
    headers = {
        'X-PrivateKey': api_key,
        'Accept': 'application/json',
        'X-SourceID': 'WEB',
        'X-ClientLocalIP': local_ip,
        'X-ClientPublicIP': public_ip,
        'X-MACAddress': mac_address,
        'X-UserType': 'USER',
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/rest/secure/angelbroking/market/v1/quote/", payload, headers)
    
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    
    # Parse JSON response
    return json.loads(data)


if __name__=="__main__":
    defs=webSocket.sessionGeneration()
    publicip=requests.get('https://api64.ipify.org').text
    localip=socket.gethostbyname(socket.gethostname())
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    macaddress=":".join([mac[e:e+2] for e in range(0, 11, 2)])
    print(fetch_market_data(defs['api_key'],defs['authToken'],localip,publicip,macaddress,'26000'))