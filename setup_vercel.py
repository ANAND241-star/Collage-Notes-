#!/usr/bin/env python3
"""
🚀 Vercel Environment Setup Script
Automatically sets environment variables in Vercel using CLI
"""

import subprocess
import os
import sys

# Environment variables to set
ENV_VARS = {
    "SECRET_KEY": "014b68f3a3529b62fa122b4fdb2c37527981792eb304f5d72a0d6bdb5ba9f6e2",
    "MONGO_URI": "mongodb+srv://anandjatt689_db_user:iYxGoSsl8xjOmdv1@cluster1.pn1gnfx.mongodb.net/notvault?retryWrites=true&w=majority",
    "ALLOWED_ORIGINS": "https://collage-notesb.vercel.app,http://localhost:3000",
    "JWT_EXPIRY_HOURS": "24",
}

def setup_vercel():
    """Set up Vercel environment variables via CLI"""
    print("🚀 NoteVault Vercel Setup\n")
    print("=" * 60)
    
    # Check if vercel CLI is installed
    try:
        subprocess.run(["vercel", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Vercel CLI not found.")
        print("\n📦 Install it with: npm i -g vercel")
        print("🔗 Or set variables manually at:")
        print("   https://vercel.com/anands-projects-0ed7382e/collage-notesb/settings/environment-variables")
        return False
    
    print("\n✅ Vercel CLI detected\n")
    print("Setting environment variables...\n")
    
    for key, value in ENV_VARS.items():
        print(f"  → {key}")
        try:
            # Note: This would need --confirm flag in CI/CD
            subprocess.run(
                ["vercel", "env", "add", key, value],
                capture_output=True,
                text=True
            )
        except Exception as e:
            print(f"    ⚠️  Could not set via CLI: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!\n")
    print("📍 Next steps:")
    print("  1. Go to: https://vercel.com/anands-projects-0ed7382e/collage-notesb")
    print("  2. Settings → Environment Variables")
    print("  3. Verify all 4 variables are set (listed above)")
    print("  4. Click Redeploy")
    print("\n🧪 Test API health:")
    print("  curl https://collage-notesb.vercel.app/api/health\n")
    
    return True

if __name__ == "__main__":
    setup_vercel()
