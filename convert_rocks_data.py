import os
import json
import urllib.request
import urllib.parse
import ssl
import time
import glob

# Path to the Minerobo data
REPO_DATA_PATH = "minerobo_repo/data/categories"
OUTPUT_FILE = "rocks_web/data/rocks_data.json"

# Wikipedia API setup
WIKI_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"

# SSL Context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

rocks_data = []
rock_id_counter = 1

print(f"Reading data from {REPO_DATA_PATH}...")

# Get all .txt files
txt_files = glob.glob(os.path.join(REPO_DATA_PATH, "*.txt"))

for file_path in txt_files:
    # Filename is the Category (e.g., igneous.txt -> Igneous)
    filename = os.path.basename(file_path)
    # Clean up filename for display: "feldspar - plagioclase.txt" -> "Feldspar - Plagioclase"
    category_name = filename.replace(".txt", "").title()
    
    print(f"Processing Category: {category_name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        mineral_name = line.strip()
        if not mineral_name:
            continue
            
        # Clean title case
        mineral_name = mineral_name.title()
        
        # Manual Alias Map for Wikipedia Lookup
        ALIAS_MAP = {
            "Dolomite": "Dolomite (mineral)",
            "Anthracite,Anthracite Coal": "Anthracite",
            "Bituminous Coal,Bituminous": "Bituminous coal",
            "Orthoclase,Potassium Feldspar,Feldspar": "Orthoclase",
            "Apatite,Apatite Group": "Apatite",
            "Citrine": "Citrine (quartz)",
            "Chert,Flint": "Chert",
            "Conglomerate": "Conglomerate (geology)",
            "Rock Salt,Halite": "Halite",
            "Rock Gypsum,Gypsum": "Gypsum",
            "Tourmaline Group,Tourmaline": "Tourmaline",
            "Celestite,Celestine": "Celestine (mineral)",
        }
        
        # Use alias if present, otherwise split on comma and use first part
        lookup_name = ALIAS_MAP.get(mineral_name, mineral_name.split(',')[0].strip())
        
        image_url = ""
        description = ""
        wiki_url = ""
        
        # Fetch from Wikipedia
        try:
            # Search query needs to be URL safe
            query = urllib.parse.quote(lookup_name)
            url = WIKI_API_URL.format(query)
            
            req = urllib.request.Request(url, headers={'User-Agent': 'MineroboStaticSiteGenerator/1.0 (https://github.com/Slooquie/SciOlyBugWeb)'})
            with urllib.request.urlopen(req, context=ctx) as response:
                data = json.loads(response.read().decode())
                
                # Image
                if 'originalimage' in data:
                    image_url = data['originalimage'].get('source', '')
                elif 'thumbnail' in data:
                    image_url = data['thumbnail'].get('source', '')
                
                # Description (Fact)
                if 'extract' in data:
                    description = data['extract']
                    # Truncate if too long (first sentence or two)
                    if len(description) > 200:
                        description = description.split('.')[0] + '.'
                
                # Link
                if 'content_urls' in data and 'desktop' in data['content_urls']:
                    wiki_url = data['content_urls']['desktop']['page']
                    
        except Exception as e:
            print(f"  Error fetching {mineral_name}: {e}")
            # Try appending " (mineral)" or " (rock)" if failed might be needed, but usually simple name works
            
        # Add to list
        entry = {
            "id": str(rock_id_counter),
            "common_name": mineral_name,      # "Granite"
            "scientific_name": mineral_name,  # Rocks don't strictly have sci/common difference like bugs
            "category": category_name,        # "Igneous"
            "image_url": image_url,
            "source_url": wiki_url,
            "key_facts": description
        }
        
        if image_url:
            rocks_data.append(entry)
            rock_id_counter += 1
            print(f"  + Added: {mineral_name}")
        else:
            print(f"  - Skipped (no image): {mineral_name}")
            
        time.sleep(0.2) 

# Write to JSON
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(rocks_data, f, indent=4)

print(f"\nSuccessfully generated {OUTPUT_FILE} with {len(rocks_data)} entries.")
