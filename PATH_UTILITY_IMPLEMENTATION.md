# Path Utility Implementation Summary

## Overview
Successfully implemented the `resolve_markdown_output_path()` function in `markitdown_gui/core/file_manager.py` as a centralized path utility for resolving markdown output paths.

## Key Features Implemented

### 1. **Core Functionality**
- ✅ Takes source file path and optional preserve_structure flag
- ✅ Returns absolute path within the program's markdown directory
- ✅ Follows existing codebase patterns and conventions
- ✅ Cross-platform compatibility using pathlib

### 2. **Security Features**
- ✅ Path sanitization to prevent directory traversal attacks
- ✅ Validates all path components for filesystem safety
- ✅ Ensures output paths remain within designated markdown directory
- ✅ Handles Windows reserved names and invalid characters

### 3. **Edge Case Handling**
- ✅ Duplicate filename detection and resolution
- ✅ Invalid character sanitization
- ✅ Path length validation for cross-platform compatibility
- ✅ Permission checking for write access
- ✅ Fallback mechanisms for error recovery

### 4. **Performance Optimizations**
- ✅ Efficient path operations using pathlib
- ✅ Minimal filesystem access during path resolution
- ✅ Conservative memory usage patterns

## Function Signature

```python
def resolve_markdown_output_path(
    source_path: Path,
    preserve_structure: bool = True,
    output_base_dir: Optional[Path] = None,
    ensure_unique: bool = True
) -> Path
```

### Parameters:
- `source_path`: Path to the source file to be converted
- `preserve_structure`: Whether to preserve directory structure (default: True)
- `output_base_dir`: Base directory for output (default: program's markdown directory)
- `ensure_unique`: Whether to generate unique filenames for conflicts (default: True)

## Integration with Existing Code

### Relationship to Existing Functions
- **Enhanced Version**: More comprehensive than existing `create_markdown_output_path()` in models.py
- **Backward Compatible**: Can replace existing function calls with additional features
- **Secure by Default**: Adds security features not present in the original

### Usage Examples

```python
# Basic usage - flatten structure
from markitdown_gui.core.file_manager import resolve_markdown_output_path

source = Path("/home/user/docs/report.pdf")
output = resolve_markdown_output_path(source, preserve_structure=False)
# Result: /program/markdown/report.md

# Preserve directory structure  
output = resolve_markdown_output_path(source, preserve_structure=True)
# Result: /program/markdown/docs/report.md

# Custom output directory
custom_dir = Path("/custom/markdown")
output = resolve_markdown_output_path(source, output_base_dir=custom_dir)
# Result: /custom/markdown/report.md

# Disable unique filename generation
output = resolve_markdown_output_path(source, ensure_unique=False)
# Will return path even if file exists
```

## Security Validations

### Directory Traversal Prevention
- Validates that resolved paths remain within the designated output directory
- Prevents malicious path components like `../../../`
- Absolute path resolution to eliminate relative path vulnerabilities

### Filename Sanitization
- Removes/replaces invalid filesystem characters: `<>:"/\|?*`
- Handles Windows reserved names (CON, PRN, AUX, etc.)
- Strips control characters (ASCII 0-31)
- Enforces filesystem-appropriate length limits

### Permission Validation
- Checks write permissions before returning path
- Creates output directories with appropriate permissions
- Validates parent directory accessibility

## Testing Results

All test cases pass successfully:
- ✅ Basic functionality (flatten structure)
- ✅ Directory structure preservation
- ✅ Filename sanitization
- ✅ Security (directory traversal prevention)
- ✅ Unique filename generation

## Technical Implementation Details

### Error Handling
- Comprehensive exception handling with descriptive error messages
- Graceful fallback mechanisms for edge cases
- Input validation with clear error reporting

### Performance Characteristics
- O(1) path resolution for most operations
- Minimal filesystem I/O operations
- Memory-efficient using pathlib operations

### Cross-Platform Support
- Uses pathlib for OS-agnostic path operations
- Handles Windows/Linux path length limitations
- Respects filesystem-specific naming conventions

## Integration Notes

The function has been successfully integrated into the `markitdown_gui.core.file_manager` module and is ready for use throughout the application. It imports the necessary utilities and constants from the existing codebase and follows the established code patterns and documentation standards.

## Next Steps

This function can now be used by:
1. Conversion managers for determining output paths
2. File conflict handlers for path resolution
3. UI components for displaying output destinations
4. Configuration systems for path management

The implementation fulfills all technical requirements and provides a robust, secure, and efficient solution for markdown output path resolution.