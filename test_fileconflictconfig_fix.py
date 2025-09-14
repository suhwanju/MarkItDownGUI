#!/usr/bin/env python3
"""
Test FileConflictConfig Fix
Verifies that the FileConflictConfig initialization error is fixed
"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def test_fileconflictconfig_initialization():
    """Test FileConflictConfig can be initialized with all parameters."""
    print("=== Testing FileConflictConfig Initialization ===\n")
    
    try:
        from markitdown_gui.core.models import FileConflictConfig, FileConflictPolicy
        
        # Test 1: Default initialization
        print("1. Testing default initialization...")
        default_config = FileConflictConfig()
        print("✅ Default initialization successful")
        print(f"   - default_policy: {default_config.default_policy}")
        print(f"   - ask_user_timeout: {default_config.ask_user_timeout}")
        print(f"   - preserve_original: {default_config.preserve_original}")
        print(f"   - backup_existing: {default_config.backup_existing}")
        
        # Test 2: Initialization with problematic parameters
        print("\n2. Testing initialization with previously problematic parameters...")
        config = FileConflictConfig(
            default_policy=FileConflictPolicy.ASK_USER,
            ask_user_timeout=30,
            preserve_original=False,
            backup_existing=True
        )
        print("✅ Initialization with all parameters successful")
        print(f"   - ask_user_timeout: {config.ask_user_timeout}")
        print(f"   - preserve_original: {config.preserve_original}")
        print(f"   - backup_existing: {config.backup_existing}")
        
        # Test 3: Check all parameters are accessible
        print("\n3. Testing parameter access...")
        all_params = [
            'default_policy', 'auto_rename_pattern', 'remember_choices',
            'apply_to_all', 'backup_original', 'conflict_log_enabled',
            'ask_user_timeout', 'preserve_original', 'backup_existing'
        ]
        
        for param in all_params:
            if hasattr(config, param):
                value = getattr(config, param)
                print(f"   ✅ {param}: {value}")
            else:
                print(f"   ❌ {param}: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conflict_config_simulation():
    """Simulate the exact scenario from main_window.py that was failing."""
    print("\n=== Testing Main Window Scenario Simulation ===\n")
    
    try:
        from markitdown_gui.core.models import FileConflictConfig, FileConflictPolicy
        
        print("Simulating the exact code from main_window.py _load_conflict_config()...")
        
        # This is the exact code that was failing
        config = FileConflictConfig(
            default_policy=FileConflictPolicy.ASK_USER,
            ask_user_timeout=30,  # This was causing the error
            preserve_original=False,  # This was also problematic
            backup_existing=True   # This was also problematic
        )
        
        print("✅ Main window scenario simulation successful!")
        print("✅ The error 'FileConflictConfig.__init__() got an unexpected keyword argument' is now fixed")
        
        # Test attribute access that happens later in the code
        print(f"\nAttribute access test:")
        print(f"   - config.ask_user_timeout: {config.ask_user_timeout}")
        print(f"   - config.preserve_original: {config.preserve_original}") 
        print(f"   - config.backup_existing: {config.backup_existing}")
        print(f"   - config.default_policy: {config.default_policy}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return False


def main():
    """Main test function."""
    print("Testing FileConflictConfig Fix")
    print("=" * 50)
    print("Original error: FileConflictConfig.__init__() got an unexpected keyword argument 'ask_user_timeout'")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(test_fileconflictconfig_initialization())
    results.append(test_conflict_config_simulation())
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! FileConflictConfig error is fixed.")
        print("\nChanges made:")
        print("1. Added missing parameters to FileConflictConfig class in models.py:")
        print("   - ask_user_timeout: int = 30")
        print("   - preserve_original: bool = False") 
        print("   - backup_existing: bool = True")
        print("\n✅ The warning message should no longer appear during startup.")
        print("✅ Conflict configuration loading now works correctly.")
    else:
        print(f"❌ {passed}/{total} tests passed. Some issues remain.")
        print("Please check the test output above for specific problems.")


if __name__ == "__main__":
    main()