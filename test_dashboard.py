#!/usr/bin/env python3
"""Quick test script for database integration"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agentic_services.database import get_db

def test_database():
    print("🧪 Testing Database Integration\n")
    
    # Get database instance
    db = get_db()
    print("✅ Database connection established")
    print(f"📁 Database location: {db.db_path}\n")
    
    # Check existing projects
    projects = db.get_all_projects()
    print(f"📊 Found {len(projects)} existing project(s)")
    
    if projects:
        for p in projects:
            print(f"  • {p['name']} - {p['status']} ({p['progress']}% complete)")
    
    print("\n" + "="*60)
    print("🎉 Database is working correctly!")
    print("="*60)
    print("\n💡 Next steps:")
    print("  1. Run: streamlit run app_streamlit.py")
    print("  2. Create a project via 📋 Onboarding")
    print("  3. View analytics in 📈 Analytics")
    print()

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
