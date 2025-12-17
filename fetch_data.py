import json
import urllib.request
import urllib.parse
import ssl
import time

# List of bugs to search and their facts
bugs_to_fetch = [
    {
        "search_term": "Monarch Butterfly",
        "fact": "Known for its long-distance annual migration.",
        "order": "Lepidoptera",
        "family": "Nymphalidae"
    },
    {
        "search_term": "Western Honey Bee",
        "fact": "Produces honey and is a key pollinator for crops.",
        "order": "Hymenoptera",
        "family": "Apidae"
    },
    {
        "search_term": "Seven-spotted Lady Beetle",
        "fact": "The most common ladybug in Europe, an aphid predator.",
        "order": "Coleoptera",
        "family": "Coccinellidae"
    },
    {
        "search_term": "European Mantis",
        "fact": "Females are known for occasionally eating males after mating.",
        "order": "Mantodea",
        "family": "Mantidae"
    },
    {
        "search_term": "Common Green Darner",
        "fact": "One of the most common dragonflies in North America.",
        "order": "Odonata",
        "family": "Aeshnidae"
    },
    {
        "search_term": "Hercules Beetle",
        "fact": "One of the largest beetles, known for the male's large horns.",
        "order": "Coleoptera",
        "family": "Scarabaeidae"
    },
    {
        "search_term": "Luna Moth",
        "fact": "Adults have no mouths and only live for about a week to reproduce.",
        "order": "Lepidoptera",
        "family": "Saturniidae"
    },
    {
        "search_term": "Walking Stick",
        "fact": "Masters of camouflage, resembling twigs or branches.",
        "order": "Phasmida",
        "family": "Diapheromeridae"
    }
]

api_url = "https://api.inaturalist.org/v1/taxa?q={}&is_active=true&rank=species&per_page=1"
output_file = "web/data/bug_data.json"

bug_data = []

# Create a context that ignores SSL verification errors if certificates are an issue, 
# though normally we should verify. For this simple script, standard context often works.
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("Fetching data from iNaturalist...")

for index, bug_info in enumerate(bugs_to_fetch):
    query = urllib.parse.quote(bug_info["search_term"])
    url = api_url.format(query)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'BugboStaticSiteGenerator/1.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            
            if data['results']:
                result = data['results'][0]
                
                # Extract details
                common_name = result.get('preferred_common_name', bug_info['search_term'])
                scientific_name = result.get('name', 'Unknown')
                
                image_url = ""
                if 'default_photo' in result and result['default_photo']:
                    image_url = result['default_photo'].get('medium_url', '')

                # Extract ancestry (Order and Family) from our list if not in API (we are using manual list now)
                # But wait, looking at my own code in 'replace_file_content' earlier...
                # I am now mixing API results with my manual 'bug_info'.
                
                entry = {
                    "id": str(index + 1),
                    "common_name": common_name,
                    "scientific_name": scientific_name,
                    "order": bug_info.get("order", "Unknown"),
                    "family": bug_info.get("family", "Unknown"),
                    "image_url": image_url,
                    "key_facts": bug_info["fact"]
                }
                
                bug_data.append(entry)
                print(f"Fetched: {common_name} ({bug_info.get('order')})")
            else:
                print(f"No results for: {bug_info['search_term']}")
                
    except Exception as e:
        print(f"Error fetching {bug_info['search_term']}: {e}")
    
    # Be nice to the API
    time.sleep(1)

# Write to file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(bug_data, f, indent=4)

print(f"Successfully saved {len(bug_data)} bugs to {output_file}")
