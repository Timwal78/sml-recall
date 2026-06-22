import os
import requests
import json
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# The user must provide their Gumroad access token
ACCESS_TOKEN = os.environ.get('GUMROAD_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    print("❌ Error: Please set your GUMROAD_ACCESS_TOKEN in the .env file")
    print("Get it from: https://app.gumroad.com/settings/advanced")
    sys.exit(1)

# Gumroad API Endpoint
URL = "https://api.gumroad.com/v2/products"

PRODUCTS = [
    {
        "name": "SML-RECALL Core Tier",
        "price": 2700,
        "description": "The essential scripts to manage your MASTER.md and context. Includes auto-updates, briefing generation, and gap-finding.",
        "permalink": "recall-core",
        "custom_receipt_instructions": "Your license key will be sent shortly via our automated webhook. Keep an eye on your inbox!"
    },
    {
        "name": "SML-RECALL Beastmode Tier",
        "price": 6700,
        "description": "Advanced context extraction and health scoring for power users. Includes everything in Core, plus impact-analysis, thread routing, and the Beastmode prompts.",
        "permalink": "recall-beastmode",
        "custom_receipt_instructions": "Your Beastmode license key will be sent shortly via our automated webhook. Keep an eye on your inbox!"
    },
    {
        "name": "SML-RECALL Bundle Tier",
        "price": 9700,
        "description": "Everything in Beastmode + Bonus SML Systems. Designed for power users and automation.",
        "permalink": "recall-bundle",
        "custom_receipt_instructions": "Your Bundle license key will be sent shortly via our automated webhook. Keep an eye on your inbox!"
    }
]

def create_products():
    print("=== SML-RECALL Gumroad Product Creator ===")
    for prod in PRODUCTS:
        print(f"Creating {prod['name']}...")
        payload = {
            "access_token": ACCESS_TOKEN,
            "name": prod['name'],
            "price": prod['price'],
            "description": prod['description'],
            "permalink": prod['permalink'],
            "custom_receipt_instructions": prod['custom_receipt_instructions'],
            "currency": "usd"
        }
        
        response = requests.post(URL, data=payload)
        if response.status_code == 201:
            data = response.json()
            short_url = data.get('product', {}).get('short_url')
            print(f"Success! Product URL: {short_url}")
        else:
            print(f"Failed to create product. Status: {response.status_code}")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response text: {response.text}")
            
    print("\nNext step: Go to https://app.gumroad.com/settings/advanced to setup your Webhook.")
    print("Point the 'Ping endpoint' to your deployed SML Rails URL: https://sml-rails.onrender.com/webhook/gumroad")

if __name__ == "__main__":
    create_products()
