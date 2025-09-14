#!/usr/bin/env python3
"""
Example script demonstrating the conversion settings functionality
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from markitdown_gui.core.models import FileConflictConfig, FileConflictPolicy
from markitdown_gui.core.config_manager import ConfigManager


def demonstrate_conversion_settings():
    """Demonstrate conversion settings functionality"""
    print("🔄 Conversion Settings Demonstration")
    print("=" * 50)
    
    # Create a ConfigManager instance
    config_manager = ConfigManager(Path("./config_test"))
    
    # Load existing config or create default
    app_config = config_manager.load_config()
    print(f"✅ Loaded config from: {config_manager.config_dir}")
    
    # Display current file conflict configuration
    conflict_config = config_manager.get_file_conflict_config()
    print(f"\n📋 Current File Conflict Settings:")
    print(f"  • Default Policy: {conflict_config.default_policy.value}")
    print(f"  • Auto Rename Pattern: {conflict_config.auto_rename_pattern}")
    print(f"  • Remember Choices: {conflict_config.remember_choices}")
    print(f"  • Apply to All: {conflict_config.apply_to_all}")
    print(f"  • Backup Original: {conflict_config.backup_original}")
    print(f"  • Conflict Logging: {conflict_config.conflict_log_enabled}")
    
    # Display save location settings
    save_settings = config_manager.get_save_location_settings()
    print(f"\n💾 Save Location Settings:")
    print(f"  • Save to Original Directory: {save_settings['save_to_original_directory']}")
    print(f"  • Output Directory: {save_settings['output_directory']}")
    
    # Demonstrate setting updates
    print(f"\n🔧 Updating Settings...")
    
    # Create a new file conflict configuration
    new_conflict_config = FileConflictConfig(
        default_policy=FileConflictPolicy.RENAME,
        auto_rename_pattern="{name}_copy_{counter}{ext}",
        remember_choices=True,
        apply_to_all=False,
        backup_original=True,
        conflict_log_enabled=True
    )
    
    # Update the configuration
    config_manager.update_file_conflict_config(new_conflict_config)
    config_manager.update_save_location_settings(
        save_to_original=False,
        output_directory=Path("./converted_files")
    )
    
    # Save the updated configuration
    success = config_manager.save_config()
    if success:
        print("✅ Settings updated and saved successfully")
    else:
        print("❌ Failed to save settings")
    
    # Display updated settings
    updated_conflict_config = config_manager.get_file_conflict_config()
    updated_save_settings = config_manager.get_save_location_settings()
    
    print(f"\n📋 Updated File Conflict Settings:")
    print(f"  • Default Policy: {updated_conflict_config.default_policy.value}")
    print(f"  • Auto Rename Pattern: {updated_conflict_config.auto_rename_pattern}")
    print(f"  • Remember Choices: {updated_conflict_config.remember_choices}")
    print(f"  • Apply to All: {updated_conflict_config.apply_to_all}")
    print(f"  • Backup Original: {updated_conflict_config.backup_original}")
    print(f"  • Conflict Logging: {updated_conflict_config.conflict_log_enabled}")
    
    print(f"\n💾 Updated Save Location Settings:")
    print(f"  • Save to Original Directory: {updated_save_settings['save_to_original_directory']}")
    print(f"  • Output Directory: {updated_save_settings['output_directory']}")
    
    # Demonstrate rename pattern functionality
    print(f"\n🏷️  Rename Pattern Examples:")
    pattern = updated_conflict_config.auto_rename_pattern
    examples = [
        ("document.md", "document_copy_1.md"),
        ("presentation.md", "presentation_copy_1.md"),
        ("report.md", "report_copy_1.md")
    ]
    
    for original, expected in examples:
        name = Path(original).stem
        ext = Path(original).suffix
        renamed = pattern.format(name=name, counter=1, ext=ext)
        status = "✅" if renamed == expected else "❌"
        print(f"  {status} {original} → {renamed}")
    
    print(f"\n🎉 Conversion Settings Demo Complete!")


def demonstrate_policy_descriptions():
    """Demonstrate different conflict resolution policies"""
    print("\n🔍 File Conflict Policy Descriptions:")
    print("=" * 50)
    
    policies = {
        FileConflictPolicy.ASK_USER: {
            "name": "Ask User",
            "description": "Prompt user for each conflict",
            "pros": ["Safe", "Flexible", "User control"],
            "cons": ["Requires manual intervention", "Slower for batch operations"]
        },
        FileConflictPolicy.SKIP: {
            "name": "Skip",
            "description": "Skip conflicting files",
            "pros": ["Safe", "Fast", "Preserves existing files"],
            "cons": ["Files may not be converted", "Lower completion rate"]
        },
        FileConflictPolicy.OVERWRITE: {
            "name": "Overwrite",
            "description": "Replace existing files",
            "pros": ["Fast", "Complete conversion", "Simple"],
            "cons": ["Data loss risk", "No backup by default"]
        },
        FileConflictPolicy.RENAME: {
            "name": "Rename",
            "description": "Auto-generate unique names",
            "pros": ["Complete conversion", "Preserves all files", "Automated"],
            "cons": ["Multiple file versions", "Requires pattern setup"]
        }
    }
    
    for policy, info in policies.items():
        print(f"\n📋 {info['name']} ({policy.value}):")
        print(f"  Description: {info['description']}")
        print(f"  Pros: {', '.join(info['pros'])}")
        print(f"  Cons: {', '.join(info['cons'])}")


if __name__ == "__main__":
    try:
        demonstrate_conversion_settings()
        demonstrate_policy_descriptions()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This example requires the full project dependencies to be installed.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()