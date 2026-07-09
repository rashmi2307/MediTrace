import requests

def test_drug(name):
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json"
    try:
        r = requests.get(url, params={"name": name}, timeout=10)
        print(f"Name: {name}, Status: {r.status_code}")
        print("Response:", r.text)
    except Exception as e:
        print("Error:", e)

test_drug("warfarin")
test_drug("aspirin")
test_drug("ibuprofen")
