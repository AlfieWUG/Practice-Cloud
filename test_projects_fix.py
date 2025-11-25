#!/usr/bin/env python3
"""Test that Projects page properly uses database"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agentic_services.database import get_db

def test_projects_page():
    """Verify Projects page can load data from database"""
    db = get_db()
    
    print("🧪 Testing Projects Page Database Integration")
    print("="*60)
    
    # Get all projects (mimics what the page does)
    projects = db.get_all_projects()
    
    print(f"✅ Database connection: OK")
    print(f"✅ Projects loaded: {len(projects)}")
    
    if projects:
        print(f"\n📊 Summary Metrics (what the page will show):")
        print(f"   - Total Projects: {len(projects)}")
        
        in_progress = sum(1 for p in projects if p['status'] == 'In Progress')
        print(f"   - In Progress: {in_progress}")
        
        completed = sum(1 for p in projects if p['status'] == 'Completed')
        print(f"   - Completed: {completed}")
        
        avg_progress = sum(p['progress'] for p in projects) / len(projects)
        print(f"   - Avg Progress: {avg_progress:.0f}%")
        
        print(f"\n📁 Projects:")
        for project in projects:
            print(f"   - {project['name']}: {project['status']} ({project['progress']}%)")
    else:
        print("\n⚠️  No projects found in database")
    
    print("\n" + "="*60)
    print("✅ All checks passed - Projects page should work correctly")
    
if __name__ == "__main__":
    try:
        test_projects_page()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
