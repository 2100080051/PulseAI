import os
import sys
import json
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv()

CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/callback"

# Scopes needed for posting to personal pages
SCOPES = "openid profile email w_member_social"

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        if "code" in params:
            code = params["code"][0]
            self.wfile.write(b"<h1>Success!</h1><p>Authorization code received. You can close this window. Check your terminal!</p>")
            
            print(f"\n[+] Received Authorization Code!")
            print("[+] Exchanging code for Access Token...")
            
            # Exchange code for access token
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
            
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                access_token = response.json().get("access_token")
                print("\n[SUCCESS] Access token generated!\n")
                
                # Append to .env
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
                
                with open(env_path, "a") as f:
                    f.write(f"\nLINKEDIN_ACCESS_TOKEN={access_token}\n")
                    
                print(f"✅ Saved LINKEDIN_ACCESS_TOKEN to {env_path}")
            else:
                print("\n[ERROR] Failed to get access token.")
                print(response.text)
                
            # Stop the local server
            def kill_server():
                self.server.shutdown()
            import threading
            threading.Thread(target=kill_server).start()
            
        elif "error" in params:
            error = params.get("error")[0]
            error_desc = params.get("error_description", [""])[0]
            self.wfile.write(b"<h1>Authentication Failed!</h1><p>Check the terminal.</p>")
            print(f"\n[ERROR] User rejected or error occurred: {error} - {error_desc}")
            
            def kill_server():
                self.server.shutdown()
            import threading
            threading.Thread(target=kill_server).start()

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_SECRET is missing in .env")
        return
        
    print("\n" + "="*60)
    print("PulseAI — LinkedIn Token Generator")
    print("="*60)
    print("IMPORTANT: Before you continue, go to the LinkedIn Developer Portal:")
    print("1. Go to your App -> Auth tab")
    print(f"2. Under 'OAuth 2.0 settings', add this exactly as an Authorized Redirect URL:")
    print(f"   {REDIRECT_URI}")
    print("3. Click Update/Save.")
    print("\nPress ENTER when you have done this...")
    input()
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&state=DCEeFWf45A53sdfKef424&scope={urllib.parse.quote(SCOPES)}"
    
    print("\nOpening your browser to authenticate with LinkedIn...")
    webbrowser.open(auth_url)
    
    print("\nWaiting for callback on http://localhost:8080/callback ...")
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    server.serve_forever()
    print("Shutdown complete.")

if __name__ == "__main__":
    main()
