#!/usr/bin/env python3
"""
Comprehensive validation script for dashboard integration
Tests all database operations and data flow
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agentic_services.database import get_db
from datetime import datetime

def test_database_connection():
    """Test 1: Database Connection"""
    print("\n" + "="*60)
    print("TEST 1: Database Connection")
    print("="*60)
    
    try:
        db = get_db()
        print(f"✅ Database connection successful")
        print(f"📁 Location: {db.db_path}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_project_creation():
    """Test 2: Create Project"""
    print("\n" + "="*60)
    print("TEST 2: Project Creation")
    print("="*60)
    
    try:
        db = get_db()
        
        # Create test project
        project_data = {
            'name': 'Validation Test Project',
            'description': 'Automated validation test',
            'requirements': 'Test requirements',
            'timeline': '1-3 months',
            'priority': 'High',
            'budget': '$100K - $500K',
            'complexity': 'Simple',
            'status': 'Planning',
            'phase': 'Discovery',
            'progress': 0,
            'demo_mode': True
        }
        
        project_id = db.create_project(project_data)
        print(f"✅ Project created with ID: {project_id}")
        
        # Verify project exists
        project = db.get_project(project_id)
        if project:
            print(f"✅ Project retrieved: {project['name']}")
            return project_id
        else:
            print(f"❌ Could not retrieve project")
            return None
            
    except Exception as e:
        print(f"❌ Project creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_agent_execution(project_id):
    """Test 3: Agent Execution Recording"""
    print("\n" + "="*60)
    print("TEST 3: Agent Execution Recording")
    print("="*60)
    
    try:
        db = get_db()
        
        # Create execution
        execution_data = {
            'project_id': project_id,
            'agent_name': 'discovery',
            'phase': 'Discovery',
            'status': 'running',
            'progress': 50,
            'started_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        execution_id = db.create_execution(execution_data)
        print(f"✅ Execution created with ID: {execution_id}")
        
        # Update execution to completed
        updates = {
            'status': 'completed',
            'progress': 100,
            'completed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'duration_seconds': 2.5
        }
        
        db.update_execution(execution_id, updates)
        print(f"✅ Execution updated to completed")
        
        # Verify execution
        executions = db.get_project_executions(project_id)
        if executions and len(executions) > 0:
            print(f"✅ Retrieved {len(executions)} execution(s)")
            return True
        else:
            print(f"❌ No executions found")
            return False
            
    except Exception as e:
        print(f"❌ Agent execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_activity_log():
    """Test 4: Activity Log"""
    print("\n" + "="*60)
    print("TEST 4: Activity Log")
    print("="*60)
    
    try:
        db = get_db()
        
        # Get recent activity
        activity = db.get_recent_activity(limit=10)
        print(f"✅ Retrieved {len(activity)} activity log entries")
        
        if activity:
            latest = activity[0]
            print(f"   Latest: {latest['action_description']}")
            print(f"   Time: {latest.get('created_at', 'N/A')}")
        
        return True
            
    except Exception as e:
        print(f"❌ Activity log test failed: {e}")
        return False

def test_execution_stats(project_id):
    """Test 5: Execution Statistics"""
    print("\n" + "="*60)
    print("TEST 5: Execution Statistics")
    print("="*60)
    
    try:
        db = get_db()
        
        # Get overall stats
        stats = db.get_execution_stats()
        print(f"✅ Overall execution stats:")
        print(f"   Total: {stats.get('total', 0)}")
        print(f"   Completed: {stats.get('completed', 0)}")
        print(f"   Failed: {stats.get('failed', 0)}")
        
        # Get project-specific stats
        project_stats = db.get_execution_stats(project_id)
        print(f"✅ Project-specific stats:")
        print(f"   Total: {project_stats.get('total', 0)}")
        print(f"   Completed: {project_stats.get('completed', 0)}")
        
        return True
            
    except Exception as e:
        print(f"❌ Execution stats test failed: {e}")
        return False

def test_datetime_parsing():
    """Test 6: Datetime Parsing"""
    print("\n" + "="*60)
    print("TEST 6: Datetime Parsing")
    print("="*60)
    
    try:
        # Test SQLite format
        test_date = "2025-11-18 14:29:51"
        parsed = datetime.strptime(test_date, "%Y-%m-%d %H:%M:%S")
        print(f"✅ SQLite format parsed: {test_date}")
        
        # Test ISO format
        test_date_iso = "2025-11-18T14:29:51"
        parsed_iso = datetime.fromisoformat(test_date_iso)
        print(f"✅ ISO format parsed: {test_date_iso}")
        
        # Test time difference
        now = datetime.now()
        diff = (now - parsed).total_seconds()
        print(f"✅ Time difference calculation works: {diff:.1f}s")
        
        return True
            
    except Exception as e:
        print(f"❌ Datetime parsing test failed: {e}")
        return False

def cleanup_test_data():
    """Cleanup: Remove Test Project"""
    print("\n" + "="*60)
    print("CLEANUP: Removing Test Data")
    print("="*60)
    
    try:
        db = get_db()
        
        # Find and delete test project
        projects = db.get_all_projects()
        for project in projects:
            if project['name'] == 'Validation Test Project':
                db.delete_project(project['id'])
                print(f"✅ Deleted test project (ID: {project['id']})")
        
        return True
            
    except Exception as e:
        print(f"⚠️ Cleanup failed (not critical): {e}")
        return False

def main():
    print("\n" + "🧪 "*30)
    print("     DASHBOARD INTEGRATION VALIDATION SUITE")
    print("🧪 "*30)
    
    results = {}
    
    # Test 1: Database Connection
    results['connection'] = test_database_connection()
    
    # Test 2: Project Creation
    project_id = test_project_creation()
    results['project_creation'] = project_id is not None
    
    if project_id:
        # Test 3: Agent Execution
        results['agent_execution'] = test_agent_execution(project_id)
        
        # Test 5: Execution Stats
        results['execution_stats'] = test_execution_stats(project_id)
    else:
        results['agent_execution'] = False
        results['execution_stats'] = False
    
    # Test 4: Activity Log
    results['activity_log'] = test_activity_log()
    
    # Test 6: Datetime Parsing
    results['datetime_parsing'] = test_datetime_parsing()
    
    # Cleanup
    if project_id:
        cleanup_test_data()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    print("\n" + "="*60)
    print(f"RESULT: {passed_tests}/{total_tests} tests passed")
    print("="*60)
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Dashboard is ready to use.")
        print("\n📝 Next steps:")
        print("  1. Run: streamlit run app_streamlit.py")
        print("  2. Create a project via 📋 Onboarding")
        print("  3. Execute agents via ⚙️ Agent Execution")
        print("  4. View results in 📈 Analytics")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
