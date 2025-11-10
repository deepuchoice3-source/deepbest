"""
Helper script to generate Upstox Access Token
"""
import requests
import webbrowser
from urllib.parse import parse_qs, urlparse

print("=" * 80)
print("Upstox Access Token Generator")
print("=" * 80)
print()

# Get API credentials
api_key = input("Enter your Upstox API Key: ").strip()
api_secret = input("Enter your Upstox API Secret: ").strip()

if not api_key or not api_secret:
    print("Error: API Key and Secret are required!")
    exit(1)

# Step 1: Generate authorization URL
redirect_uri = "http://localhost:5000"
auth_url = (
    f"https://api.upstox.com/v2/login/authorization/dialog"
    f"?response_type=code"
    f"&client_id={api_key}"
    f"&redirect_uri={redirect_uri}"
)

print()
print("Step 1: Authorization")
print("-" * 80)
print("Opening browser for authorization...")
print()
print("If browser doesn't open automatically, visit this URL:")
print(auth_url)
print()

# Open browser
try:
    webbrowser.open(auth_url)
except:
    pass

print("After authorization, you'll be redirected to:")
print("http://localhost:5000?code=YOUR_AUTH_CODE")
print()
print("Copy the FULL redirect URL from your browser address bar")
redirect_url = input("Paste the redirect URL here: ").strip()

# Extract auth code
try:
    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)
    auth_code = params.get('code', [None])[0]
    
    if not auth_code:
        print("Error: Could not extract authorization code from URL")
        exit(1)
        
    print(f"\n✓ Authorization code extracted: {auth_code[:20]}...")
    
except Exception as e:
    print(f"Error parsing URL: {e}")
    exit(1)

# Step 2: Exchange code for token
print()
print("Step 2: Exchanging code for access token...")
print("-" * 80)

try:
    response = requests.post(
        "https://api.upstox.com/v2/login/authorization/token",
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "code": auth_code,
            "client_id": api_key,
            "client_secret": api_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        print()
        print("=" * 80)
        print("✅ SUCCESS! Access Token Generated")
        print("=" * 80)
        print()
        print("Access Token:")
        print(access_token)
        print()
        print("Add this to your .env file:")
        print(f"UPSTOX_ACCESS_TOKEN={access_token}")
        print()
        
        # Offer to update .env file
        update_env = input("Update .env file automatically? (y/n): ").strip().lower()
        
        if update_env == 'y':
            try:
                # Read existing .env or create from template
                try:
                    with open('.env', 'r') as f:
                        env_content = f.read()
                except FileNotFoundError:
                    with open('.env.example', 'r') as f:
                        env_content = f.read()
                
                # Update token
                lines = env_content.split('\n')
                updated = False
                for i, line in enumerate(lines):
                    if line.startswith('UPSTOX_ACCESS_TOKEN='):
                        lines[i] = f'UPSTOX_ACCESS_TOKEN={access_token}'
                        updated = True
                    elif line.startswith('UPSTOX_API_KEY='):
                        lines[i] = f'UPSTOX_API_KEY={api_key}'
                
                # Write back
                with open('.env', 'w') as f:
                    f.write('\n'.join(lines))
                
                print("✅ .env file updated successfully!")
                print()
                print("You can now run the application:")
                print("  python3 app.py")
                
            except Exception as e:
                print(f"Error updating .env file: {e}")
                print("Please update manually.")
        
        print()
        print("Note: Access tokens are valid for 24 hours.")
        print("You'll need to regenerate after expiry.")
        print()
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
    exit(1)
