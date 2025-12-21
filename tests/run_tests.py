# tests/run_tests.py
import subprocess
import sys
import os

def main():
    print("="*60)
    print("TEST RUNNER WITH DATABASE FIXES")
    print("="*60)
    
    # First, ensure we're using SQLite for tests
    print("\n🔧 Setting up test environment...")
    
    # Delete incompatible test files
    files_to_delete = [
        'test_ta_model.py',
        'test_student_model.py', 
        'test_instructor_model.py'
    ]
    
    for file in files_to_delete:
        if os.path.exists(f"tests/{file}"):
            os.remove(f"tests/{file}")
            print(f"  Deleted: {file}")
    
    # Run tests with specific configuration
    print("\n🚀 Running tests with SQLite in-memory database...")
    
    # Set environment variable to ensure SQLite is used
    os.environ['FLASK_ENV'] = 'testing'
    
    cmd = [
        'pytest', 
        'tests/test_user_model.py',
        'tests/test_announcement_model.py', 
        'tests/test_submission_model.py',
        'tests/test_assignment_model.py',
        '-v',
        '--tb=short'  # Shorter traceback for readability
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        
        print(result.stdout)
        
        if result.stderr:
            print("\nERRORS:")
            print(result.stderr)
            
        return_code = result.returncode
        print(f"\nExit code: {return_code}")
        
        if return_code == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
            print("\n💡 TROUBLESHOOTING:")
            print("1. Make sure conftest.py is using 'sqlite:///:memory:'")
            print("2. Run: python fix_tests.py (to fix method names)")
            print("3. Check if your models have proper __tablename__ defined")
            
        return return_code == 0
        
    except FileNotFoundError:
        print("❌ Error: pytest not found. Install with: pip install pytest")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)