import os
import json
import urllib.request
import urllib.parse
import ssl
import time
import glob

# Path to the repo's taxon data
REPO_DATA_PATH = "bugbo_repo/data/taxon"
OUTPUT_FILE = "web/data/bug_data.json"

# API setup
API_URL = "https://api.inaturalist.org/v1/taxa?q={}&is_active=true&rank=family,subfamily&per_page=1"

# SSL Context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

bug_data = []
bug_id_counter = 1

print(f"Reading data from {REPO_DATA_PATH}...")

# Get all .txt files in the taxon directory
txt_files = glob.glob(os.path.join(REPO_DATA_PATH, "*.txt"))

for file_path in txt_files:
    # Filename is the Order (e.g., coleoptera.txt -> Coleoptera)
    filename = os.path.basename(file_path)
    order_name = filename.replace(".txt", "").capitalize()
    
    print(f"Processing Order: {order_name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split(',')
        scientific_family_name = parts[0].strip().capitalize()
        
        # Common names are the rest, take the first one as primary
        common_name = parts[1].strip().title() if len(parts) > 1 else scientific_family_name
        
        # Prepare fact (just using aliases as facts for now)
        aliases = ", ".join([p.strip().title() for p in parts[1:]])
        key_fact = f"Also known as: {aliases}" if aliases else "No common aliases listed."

        # Fetch Image from iNaturalist
        # We search for the Scientific Family Name to get a representative image
        query = urllib.parse.quote(scientific_family_name)
        url = API_URL.format(query)
        
        image_url = ""
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'BugboStaticSiteGenerator/1.0'})
            with urllib.request.urlopen(req, context=ctx) as response:
                data = json.loads(response.read().decode())
                
                if data['results']:
                    result = data['results'][0]
                    if 'default_photo' in result and result['default_photo']:
                        image_url = result['default_photo'].get('medium_url', '')
                        
                        # Sometimes the API returns a common name for the family we can use if ours is missing
                        if common_name == scientific_family_name and result.get('preferred_common_name'):
                            common_name = result.get('preferred_common_name').title()
                    
                    # Capture iNaturalist URL
                    taxon_id = result.get('id')
                    inat_url = f"https://www.inaturalist.org/taxa/{taxon_id}" if taxon_id else ""
                else:
                    print(f"  No API results for {scientific_family_name}")
                    inat_url = ""

        except Exception as e:
            print(f"  Error fetching {scientific_family_name}: {e}")
            
        # Add to list
        entry = {
            "id": str(bug_id_counter),
            "common_name": common_name,       # "Ground Beetles"
            "scientific_name": scientific_family_name, # "Carabidae"
            "order": order_name,              # "Coleoptera"
            "family": scientific_family_name, # "Carabidae" (Redundant but useful for game logic)
            "image_url": image_url,
            "inat_url": inat_url,
            "key_facts": key_fact
        }
        
        # Only add if we found an image (or we can include placeholders)
        if image_url:
            bug_data.append(entry)
            bug_id_counter += 1
            print(f"  + Added: {scientific_family_name} ({common_name})")
        else:
            print(f"  - Skipped (no image): {scientific_family_name}")
            
        # Be nice to API
        time.sleep(0.5)

# Write to JSON
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(bug_data, f, indent=4)

print(f"\nSuccessfully generated {OUTPUT_FILE} with {len(bug_data)} entries.")
