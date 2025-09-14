#!/usr/bin/env python3
"""
Documentation Link Validation Script
Validates all internal markdown links in the project documentation.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Tuple, Dict, Set

class LinkValidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checked_files: Set[Path] = set()
        
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the project."""
        md_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue
                
            for file in files:
                if file.endswith('.md'):
                    md_files.append(Path(root) / file)
        return md_files
    
    def extract_links(self, content: str) -> List[Tuple[str, str]]:
        """Extract markdown links from content."""
        # Pattern for markdown links: [text](url)
        pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        return re.findall(pattern, content)
    
    def is_internal_link(self, url: str) -> bool:
        """Check if link is internal (relative or fragment)."""
        parsed = urlparse(url)
        return (
            not parsed.scheme and  # No protocol (http/https)
            not parsed.netloc and  # No domain
            not url.startswith('mailto:')  # Not email
        )
    
    def resolve_link_path(self, current_file: Path, link_url: str) -> Path:
        """Resolve relative link path to absolute path."""
        if link_url.startswith('#'):
            # Fragment link (same file)
            return current_file
        
        # Remove fragment if present
        if '#' in link_url:
            link_url = link_url.split('#')[0]
        
        # Resolve relative path
        current_dir = current_file.parent
        target_path = current_dir / link_url
        return target_path.resolve()
    
    def validate_fragment(self, file_path: Path, fragment: str) -> bool:
        """Validate that a fragment/anchor exists in the file."""
        if not fragment or not file_path.exists():
            return True  # Skip validation if no fragment or file doesn't exist
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert fragment to expected header format
            expected_header = fragment.lower().replace('-', ' ')
            
            # Look for headers that match the fragment
            header_pattern = r'^#+\s*(.+)$'
            for line in content.split('\n'):
                match = re.match(header_pattern, line)
                if match:
                    header_text = match.group(1).lower().strip()
                    # Simple header matching
                    if expected_header in header_text or header_text in expected_header:
                        return True
            
            return False
        except Exception:
            return True  # Skip validation on error
    
    def validate_file(self, file_path: Path) -> Dict:
        """Validate all links in a single markdown file."""
        file_errors = []
        file_warnings = []
        links_checked = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            file_errors.append(f"Could not read file: {e}")
            return {
                'errors': file_errors,
                'warnings': file_warnings,
                'links_checked': 0
            }
        
        links = self.extract_links(content)
        
        for link_text, link_url in links:
            links_checked += 1
            
            if not self.is_internal_link(link_url):
                continue  # Skip external links
            
            # Handle fragment links
            fragment = None
            if '#' in link_url:
                link_url, fragment = link_url.split('#', 1)
            
            if not link_url:  # Pure fragment link
                target_file = file_path
            else:
                target_file = self.resolve_link_path(file_path, link_url)
            
            # Check if target file exists
            if not target_file.exists():
                file_errors.append(f"Broken link: [{link_text}]({link_url}) -> {target_file}")
                continue
            
            # Check fragment if present
            if fragment and not self.validate_fragment(target_file, fragment):
                file_warnings.append(f"Fragment may not exist: [{link_text}]({link_url}#{fragment})")
        
        return {
            'errors': file_errors,
            'warnings': file_warnings,
            'links_checked': links_checked
        }
    
    def validate_all(self) -> Dict:
        """Validate all markdown files in the project."""
        md_files = self.find_markdown_files()
        
        total_files = len(md_files)
        total_links = 0
        total_errors = 0
        total_warnings = 0
        
        print(f"🔍 Found {total_files} markdown files to validate...")
        
        for file_path in md_files:
            relative_path = file_path.relative_to(self.project_root)
            print(f"  📄 Checking {relative_path}...")
            
            result = self.validate_file(file_path)
            total_links += result['links_checked']
            
            if result['errors']:
                total_errors += len(result['errors'])
                self.errors.extend([f"{relative_path}: {error}" for error in result['errors']])
            
            if result['warnings']:
                total_warnings += len(result['warnings'])
                self.warnings.extend([f"{relative_path}: {warning}" for warning in result['warnings']])
        
        return {
            'total_files': total_files,
            'total_links': total_links,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'errors': self.errors,
            'warnings': self.warnings
        }

def main():
    """Main validation function."""
    project_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print("📚 MarkItDown GUI - Documentation Link Validator")
    print("=" * 50)
    
    validator = LinkValidator(project_root)
    results = validator.validate_all()
    
    print("\n📊 Validation Results:")
    print(f"  Files checked: {results['total_files']}")
    print(f"  Links validated: {results['total_links']}")
    print(f"  Errors found: {results['total_errors']}")
    print(f"  Warnings: {results['total_warnings']}")
    
    if results['errors']:
        print("\n❌ ERRORS:")
        for error in results['errors']:
            print(f"  • {error}")
    
    if results['warnings']:
        print("\n⚠️  WARNINGS:")
        for warning in results['warnings']:
            print(f"  • {warning}")
    
    if results['total_errors'] == 0:
        print("\n✅ All internal links are valid!")
        return 0
    else:
        print(f"\n❌ Found {results['total_errors']} broken links that need fixing.")
        return 1

if __name__ == "__main__":
    exit(main())