import httpx
import json
import re

try:
    r = httpx.get('https://platzi.com/categorias/', headers={'User-Agent':'Mozilla/5.0'})
    
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text, re.DOTALL)
    
    if match:
        data = json.loads(match.group(1))
        print("Found NEXT_DATA")
        
        # Let's see if categories are here
        cats = data.get('props',{}).get('pageProps',{}).get('initialState',{}).get('categories', {}).get('entities', {})
        if not cats:
            cats = data.get('props',{}).get('pageProps',{}).get('categories', [])
            
        print(f"Found {len(cats)} categories")
        if cats and isinstance(cats, list) and len(cats) > 0:
            print(f"First category has {len(cats[0].get('learning_paths', []))} learning paths")
        elif cats and isinstance(cats, dict) and len(cats) > 0:
            first_cat = list(cats.values())[0]
            print(f"First category has {len(first_cat.get('learning_paths', []))} learning paths")
    else:
        print("No NEXT_DATA found")
except Exception as e:
    print('Error:', str(e))
