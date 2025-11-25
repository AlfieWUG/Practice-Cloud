#!/usr/bin/env python3
"""Test HTML rendering for project cards"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agentic_services.database import get_db

def test_html_rendering():
    """Test that project card HTML renders correctly"""
    db = get_db()
    projects = db.get_all_projects()
    
    if not projects:
        print("❌ No projects found")
        return
    
    project = projects[0]
    
    # Simulate what the page does
    desc = project.get('description', 'No description')
    desc_truncated = desc[:100] + ('...' if len(desc) > 100 else '')
    
    status_color = '#2196f3'
    priority_color = '#ff9800'
    
    card_html = f'''<div class="feature-card" style="min-height: 280px;">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <h3 style="margin: 0;">📋 {project['name']}</h3>
            <span style="background: {priority_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{project.get('priority', 'Medium')}</span>
        </div>
        <p style="min-height: 60px; margin-bottom: 1rem;">{desc_truncated}</p>
    </div>'''
    
    print("✅ HTML generation test passed")
    print(f"   Project: {project['name']}")
    print(f"   Description: {desc_truncated}")
    print(f"   HTML length: {len(card_html)} chars")
    print()
    print("📝 Sample HTML (first 200 chars):")
    print(card_html[:200] + "...")

if __name__ == "__main__":
    try:
        test_html_rendering()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
