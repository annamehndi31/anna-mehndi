#!/usr/bin/env python3
import requests
import json
import sys
import re

def clean_number(num):
    num = re.sub(r'[^0-9]', '', num)
    if num.startswith('92'):
        return num
    elif num.startswith('0'):
        return '92' + num[1:]
    elif num.startswith('+92'):
        return num[1:]
    return '92' + num

def lookup_pk_number(number):
    num = clean_number(number)
    print(f"\n[*] Target: {num}")
    
    # Carrier info based on prefix mapping
    prefixes = {
        '30': 'Jazz (Mobilink)',
        '31': 'Zong',
        '32': 'Warid / Jazz',
        '33': 'Ufone',
        '34': 'Telenor',
        '35': 'Telenor',
        '36': 'Jazz',
        '37': 'Jazz',
        '38': 'Jazz',
        '39': 'Ufone',
        '40': 'Jazz',
        '41': 'Jazz',
        '42': 'Jazz',
    }
    
    prefix = num[2:4] if len(num) > 4 else num[2:]
    carrier = prefixes.get(prefix, "Unknown Carrier")
    print(f"[+] Carrier: {carrier}")
    print(f"[+] Country: Pakistan (+92)")
    
    # Try numverify API (free tier - no API key needed for basic)
    try:
        url = f"http://apilayer.net/api/validate?access_key=1e7a8c3d9b4f2a6c8e0d1b3a5c7e9f2d&number={num}&country_code=PK"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('valid'):
            print(f"[+] Line Type: {data.get('line_type', 'N/A')}")
            print(f"[+] Location: {data.get('location', 'N/A')}")
    except:
        print("[!] API lookup failed, using local data only")
    
    # Truecaller-lite style lookup via web scraping
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-G998B)'}
        search_url = f"https://www.truecaller.com/search/pk/{num}"
        resp = requests.get(search_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            print("[+] Truecaller: Lookup page accessible (manual verification recommended)")
    except:
        pass
    
    print("\n[*] Done. Stay ghost, Jack. ;)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lookup_pk_number(sys.argv[1])
    else:
        num = input("Enter Pakistani number: ")
        lookup_pk_number(num)
