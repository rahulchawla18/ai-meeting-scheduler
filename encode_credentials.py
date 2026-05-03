"""
Helper script to encode credentials for deployment
Run this locally before deploying to get base64 encoded credentials
"""

import base64
import os

def encode_file(filename):
    """Encode a file to base64"""
    if not os.path.exists(filename):
        print(f"❌ {filename} not found!")
        return None
    
    with open(filename, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode()
    
    print(f"✅ {filename} encoded successfully!")
    print(f"\nAdd this to your Render environment variables:\n")
    
    if filename == 'credentials.json':
        print(f"GOOGLE_CREDENTIALS_JSON={encoded}\n")
    elif filename == 'token.pickle':
        print(f"TOKEN_PICKLE_BASE64={encoded}\n")
    
    return encoded

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 Encoding credentials for deployment")
    print("=" * 60)
    print()
    
    # Encode credentials.json
    print("1. Encoding credentials.json...")
    encode_file('credentials.json')
    
    print("-" * 60)
    
    # Encode token.pickle
    print("2. Encoding token.pickle...")
    if os.path.exists('token.pickle'):
        encode_file('token.pickle')
    else:
        print("⚠️  token.pickle not found!")
        print("   Run the app locally first to authenticate and generate token.pickle")
        print("   Then run this script again.")
    
    print("=" * 60)
    print("📋 Copy the environment variables above to Render dashboard")
    print("=" * 60)
