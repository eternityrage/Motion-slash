"""
Get Instagram Business Account from Facebook Page
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

fb_page_id = os.getenv('FACEBOOK_PAGE_ID')
fb_token = os.getenv('FACEBOOK_ACCESS_TOKEN')

print("=" * 70)
print("📍 FINDING INSTAGRAM BUSINESS ACCOUNT FROM FACEBOOK PAGE")
print("=" * 70)

print(f"\nFacebook Page ID: {fb_page_id}")
print(f"Facebook Token: {fb_token[:30]}...")

# Step 1: Get Instagram Business Account ID from Facebook Page
print("\n" + "=" * 70)
print("Step 1: Getting Instagram Business Account ID")
print("=" * 70)

url = f"https://graph.facebook.com/v21.0/{fb_page_id}?fields=instagram_business_account&access_token={fb_token}"
print(f"URL: {url}")

resp = requests.get(url, timeout=15)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    print(f"Response: {data}")
    
    ig_account = data.get('instagram_business_account', {})
    if ig_account:
        ig_id = ig_account.get('id')
        print(f"\n✅ INSTAGRAM BUSINESS ACCOUNT FOUND!")
        print(f"   Instagram ID: {ig_id}")
        
        # Step 2: Get Instagram username
        print("\n" + "=" * 70)
        print("Step 2: Getting Instagram Username")
        print("=" * 70)
        
        url2 = f"https://graph.facebook.com/v21.0/{ig_id}?fields=username,name&access_token={fb_token}"
        print(f"URL: {url2}")
        
        resp2 = requests.get(url2, timeout=15)
        print(f"Status: {resp2.status_code}")
        
        if resp2.status_code == 200:
            ig_data = resp2.json()
            print(f"Response: {ig_data}")
            print(f"\n✅ Instagram Username: @{ig_data.get('username', 'N/A')}")
            print(f"✅ Instagram Name: {ig_data.get('name', 'N/A')}")
            
            print("\n" + "=" * 70)
            print("📝 UPDATE YOUR .ENV FILE:")
            print("=" * 70)
            print(f"INSTAGRAM_ACCESS_TOKEN={fb_token}")
            print(f"INSTAGRAM_ACCOUNT_ID={ig_id}")
            print("\n💡 Use the Facebook Access Token for Instagram!")
            print("   The Instagram Business Account is managed through Facebook.")
        else:
            print(f"Error: {resp2.text}")
    else:
        print("\n⚠️  NO INSTAGRAM BUSINESS ACCOUNT CONNECTED TO THIS FACEBOOK PAGE")
        print("   You need to connect an Instagram Business Account to your Facebook Page:")
        print("   1. Go to Facebook Page Settings")
        print("   2. Click 'Linked Accounts'")
        print("   3. Connect Instagram Business Account")
else:
    print(f"Error: {resp.text}")
