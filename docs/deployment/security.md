# Security Guidelines

## Overview

This guide covers comprehensive security practices for the MarkItDown GUI application, including threat modeling, secure coding practices, data protection, and deployment security considerations.

## Security Architecture

### Security Principles
- **Defense in Depth**: Multiple layers of security controls
- **Least Privilege**: Minimal necessary permissions and access
- **Fail Secure**: Secure defaults and safe failure modes
- **Zero Trust**: Verify everything, trust nothing
- **Privacy by Design**: Data protection built into the system
- **Transparency**: Clear security practices and incident disclosure

### Threat Model

#### Assets to Protect
- **User Data**: Processed documents and converted files
- **Application Code**: Intellectual property and system integrity
- **System Resources**: CPU, memory, disk, and network
- **Configuration Data**: Settings and credentials
- **Temporary Files**: Processing artifacts and cache data

#### Threat Actors
- **Malicious Files**: Crafted documents designed to exploit vulnerabilities
- **Local Attackers**: Users with local system access
- **Network Attackers**: Remote attackers via network protocols
- **Insider Threats**: Authorized users exceeding permissions
- **Supply Chain**: Compromised dependencies or plugins

#### Attack Vectors
- **File Processing**: Malicious document exploitation
- **Plugin System**: Untrusted plugin execution
- **Network Communications**: Update and external service interactions
- **File System**: Unauthorized file access or modification
- **Memory Corruption**: Buffer overflows and memory leaks
- **Configuration**: Insecure settings and credential theft

## Input Validation and Sanitization

### File Validation Framework
```python
# markitdown_gui/core/security/file_validator.py
import hashlib
import magic
import os
import zipfile
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ValidationResult(Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"
    UNKNOWN = "unknown"

@dataclass
class FileValidation:
    file_path: str
    result: ValidationResult
    reasons: List[str]
    file_type: Optional[str] = None
    file_size: int = 0
    hash_sha256: Optional[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class FileSecurityValidator:
    def __init__(self):
        # Maximum file sizes by type (in bytes)
        self.max_file_sizes = {
            'application/pdf': 100 * 1024 * 1024,  # 100MB
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 50 * 1024 * 1024,  # 50MB
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 25 * 1024 * 1024,  # 25MB
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 100 * 1024 * 1024,  # 100MB
            'image/jpeg': 20 * 1024 * 1024,  # 20MB
            'image/png': 20 * 1024 * 1024,  # 20MB
            'application/zip': 200 * 1024 * 1024,  # 200MB
            'default': 10 * 1024 * 1024  # 10MB default
        }
        
        # Suspicious file patterns
        self.suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'data:text/html',
            b'<?xml version="1.0" encoding="UTF-8"?><XXE',
            b'<!DOCTYPE.*ENTITY',
            b'%PDF-1.',  # Check for PDF bombs
        ]
        
        # Known malicious hashes (in production, this would be from a threat intelligence feed)
        self.malicious_hashes = set()
        
        # Initialize libmagic for file type detection
        self.magic = magic.Magic(mime=True)
    
    def validate_file(self, file_path: str) -> FileValidation:
        """Comprehensive file validation"""
        reasons = []
        result = ValidationResult.SAFE
        
        try:
            # Basic file system checks
            if not os.path.exists(file_path):
                return FileValidation(
                    file_path=file_path,
                    result=ValidationResult.DANGEROUS,
                    reasons=["File does not exist"]
                )
            
            file_size = os.path.getsize(file_path)
            
            # File size validation
            if file_size == 0:
                reasons.append("Empty file")
                result = ValidationResult.SUSPICIOUS
            elif file_size > 500 * 1024 * 1024:  # 500MB absolute limit
                reasons.append("File too large (>500MB)")
                result = ValidationResult.DANGEROUS
            
            # File type detection
            detected_type = self.magic.from_file(file_path)
            
            # Extension vs content validation
            extension = os.path.splitext(file_path)[1].lower()
            expected_types = self._get_expected_types(extension)
            
            if expected_types and detected_type not in expected_types:
                reasons.append(f"File type mismatch: {extension} vs {detected_type}")
                result = max(result, ValidationResult.SUSPICIOUS)
            
            # Size validation by type
            max_size = self.max_file_sizes.get(detected_type, self.max_file_sizes['default'])
            if file_size > max_size:
                reasons.append(f"File too large for type: {file_size} > {max_size}")
                result = max(result, ValidationResult.SUSPICIOUS)
            
            # Calculate file hash
            file_hash = self._calculate_hash(file_path)
            
            # Check against known malicious hashes
            if file_hash in self.malicious_hashes:
                reasons.append("Known malicious file hash")
                result = ValidationResult.DANGEROUS
            
            # Content-based validation
            content_result, content_reasons = self._validate_content(file_path, detected_type)
            reasons.extend(content_reasons)
            result = max(result, content_result)
            
            # Archive-specific validation
            if detected_type == 'application/zip':
                archive_result, archive_reasons = self._validate_archive(file_path)
                reasons.extend(archive_reasons)
                result = max(result, archive_result)
            
            return FileValidation(
                file_path=file_path,
                result=result,
                reasons=reasons,
                file_type=detected_type,
                file_size=file_size,
                hash_sha256=file_hash
            )
            
        except Exception as e:
            return FileValidation(
                file_path=file_path,
                result=ValidationResult.UNKNOWN,
                reasons=[f"Validation error: {str(e)}"]
            )
    
    def _get_expected_types(self, extension: str) -> List[str]:
        """Get expected MIME types for file extension"""
        type_mapping = {
            '.pdf': ['application/pdf'],
            '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            '.pptx': ['application/vnd.openxmlformats-officedocument.presentationml.presentation'],
            '.jpg': ['image/jpeg'],
            '.jpeg': ['image/jpeg'],
            '.png': ['image/png'],
            '.gif': ['image/gif'],
            '.zip': ['application/zip'],
            '.txt': ['text/plain'],
            '.html': ['text/html'],
            '.csv': ['text/csv', 'application/csv'],
            '.json': ['application/json', 'text/json'],
            '.xml': ['application/xml', 'text/xml']
        }
        return type_mapping.get(extension, [])
    
    def _calculate_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        hasher = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _validate_content(self, file_path: str, file_type: str) -> Tuple[ValidationResult, List[str]]:
        """Validate file content for suspicious patterns"""
        reasons = []
        result = ValidationResult.SAFE
        
        try:
            # Read first 64KB for pattern matching
            with open(file_path, 'rb') as f:
                header = f.read(65536)
            
            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                if pattern in header.lower():
                    reasons.append(f"Suspicious pattern found: {pattern.decode('utf-8', errors='ignore')}")
                    result = ValidationResult.SUSPICIOUS
            
            # PDF-specific validation
            if file_type == 'application/pdf':
                pdf_result, pdf_reasons = self._validate_pdf_content(header)
                reasons.extend(pdf_reasons)
                result = max(result, pdf_result)
            
            # Office document validation
            elif 'officedocument' in file_type:
                office_result, office_reasons = self._validate_office_content(file_path)
                reasons.extend(office_reasons)
                result = max(result, office_result)
            
        except Exception as e:
            reasons.append(f"Content validation error: {str(e)}")
            result = ValidationResult.UNKNOWN
        
        return result, reasons
    
    def _validate_pdf_content(self, header: bytes) -> Tuple[ValidationResult, List[str]]:
        """Validate PDF-specific security concerns"""
        reasons = []
        result = ValidationResult.SAFE
        
        # Check for PDF version
        if not header.startswith(b'%PDF-'):
            reasons.append("Invalid PDF header")
            result = ValidationResult.SUSPICIOUS
        
        # Check for suspicious PDF elements
        suspicious_pdf_patterns = [
            b'/JavaScript',
            b'/JS',
            b'/OpenAction',
            b'/Launch',
            b'/URI',
            b'/SubmitForm',
            b'/ImportData'
        ]
        
        for pattern in suspicious_pdf_patterns:
            if pattern in header:
                reasons.append(f"Suspicious PDF element: {pattern.decode('utf-8', errors='ignore')}")
                result = ValidationResult.SUSPICIOUS
        
        return result, reasons
    
    def _validate_office_content(self, file_path: str) -> Tuple[ValidationResult, List[str]]:
        """Validate Office document security"""
        reasons = []
        result = ValidationResult.SAFE
        
        try:
            # Office documents are ZIP files
            with zipfile.ZipFile(file_path, 'r') as zf:
                # Check for suspicious files in the archive
                suspicious_files = [
                    'vbaProject.bin',  # VBA macros
                    'macros/',
                    '_rels/.rels'  # Check for external relationships
                ]
                
                for file_name in zf.namelist():
                    for suspicious in suspicious_files:
                        if suspicious in file_name:
                            reasons.append(f"Potentially dangerous content: {file_name}")
                            result = ValidationResult.SUSPICIOUS
                
                # Check content types
                try:
                    content_types = zf.read('[Content_Types].xml')
                    if b'application/vnd.ms-office.vbaProject' in content_types:
                        reasons.append("Document contains VBA macros")
                        result = ValidationResult.SUSPICIOUS
                except KeyError:
                    pass  # No content types file
                
        except zipfile.BadZipFile:
            reasons.append("Corrupted Office document")
            result = ValidationResult.SUSPICIOUS
        except Exception as e:
            reasons.append(f"Office validation error: {str(e)}")
            result = ValidationResult.UNKNOWN
        
        return result, reasons
    
    def _validate_archive(self, file_path: str) -> Tuple[ValidationResult, List[str]]:
        """Validate ZIP archive security"""
        reasons = []
        result = ValidationResult.SAFE
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # Check for zip bombs
                total_uncompressed = sum(info.file_size for info in zf.infolist())
                compressed_size = os.path.getsize(file_path)
                
                if compressed_size > 0:
                    compression_ratio = total_uncompressed / compressed_size
                    if compression_ratio > 100:  # Suspiciously high compression
                        reasons.append(f"High compression ratio: {compression_ratio:.1f}")
                        result = ValidationResult.SUSPICIOUS
                
                # Check for path traversal
                for info in zf.infolist():
                    if '..' in info.filename or info.filename.startswith('/'):
                        reasons.append(f"Path traversal attempt: {info.filename}")
                        result = ValidationResult.DANGEROUS
                
                # Check for excessive nesting
                max_depth = max(info.filename.count('/') for info in zf.infolist())
                if max_depth > 20:
                    reasons.append(f"Excessive directory nesting: {max_depth}")
                    result = ValidationResult.SUSPICIOUS
                
        except zipfile.BadZipFile:
            reasons.append("Corrupted ZIP file")
            result = ValidationResult.SUSPICIOUS
        except Exception as e:
            reasons.append(f"Archive validation error: {str(e)}")
            result = ValidationResult.UNKNOWN
        
        return result, reasons

# Global file validator
file_validator = FileSecurityValidator()
```

### Content Sanitization
```python
# markitdown_gui/core/security/content_sanitizer.py
import re
import html
import bleach
from typing import Dict, List, Optional
from urllib.parse import urlparse

class ContentSanitizer:
    def __init__(self):
        # Allowed HTML tags for markdown output
        self.allowed_tags = {
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'strong', 'em', 'u', 'del',
            'ul', 'ol', 'li',
            'blockquote', 'pre', 'code',
            'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'a', 'img'
        }
        
        # Allowed attributes
        self.allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'table': ['class'],
            'th': ['scope'],
            'td': ['colspan', 'rowspan']
        }
        
        # URL schemes that are considered safe
        self.safe_url_schemes = {'http', 'https', 'mailto'}
        
        # Patterns for dangerous content
        self.dangerous_patterns = [
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'data:(?!image/)', re.IGNORECASE),
            re.compile(r'<script.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers
            re.compile(r'<\s*iframe', re.IGNORECASE),
            re.compile(r'<\s*object', re.IGNORECASE),
            re.compile(r'<\s*embed', re.IGNORECASE),
            re.compile(r'<\s*form', re.IGNORECASE)
        ]
    
    def sanitize_markdown(self, content: str) -> str:
        """Sanitize markdown content for safe output"""
        if not content:
            return ""
        
        # Remove dangerous patterns
        sanitized = self._remove_dangerous_patterns(content)
        
        # Sanitize URLs in markdown links
        sanitized = self._sanitize_markdown_links(sanitized)
        
        # HTML escape any remaining HTML that's not markdown
        sanitized = self._escape_html_in_markdown(sanitized)
        
        return sanitized
    
    def sanitize_html(self, content: str) -> str:
        """Sanitize HTML content using bleach"""
        if not content:
            return ""
        
        # Use bleach to clean HTML
        clean_html = bleach.clean(
            content,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True,
            strip_comments=True
        )
        
        # Additional URL validation
        clean_html = self._validate_urls_in_html(clean_html)
        
        return clean_html
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not filename:
            return "unnamed_file"
        
        # Remove path separators
        sanitized = filename.replace('/', '_').replace('\\', '_')
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"|?*]', '_', sanitized)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        # Ensure not empty
        if not sanitized or sanitized.isspace():
            sanitized = "unnamed_file"
        
        return sanitized
    
    def _remove_dangerous_patterns(self, content: str) -> str:
        """Remove dangerous patterns from content"""
        for pattern in self.dangerous_patterns:
            content = pattern.sub('', content)
        
        return content
    
    def _sanitize_markdown_links(self, content: str) -> str:
        """Sanitize URLs in markdown links"""
        # Pattern for markdown links: [text](url)
        link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
        
        def sanitize_link(match):
            text = match.group(1)
            url = match.group(2)
            
            # Validate and sanitize URL
            safe_url = self._sanitize_url(url)
            if safe_url:
                return f'[{text}]({safe_url})'
            else:
                return text  # Remove link, keep text
        
        return link_pattern.sub(sanitize_link, content)
    
    def _sanitize_url(self, url: str) -> Optional[str]:
        """Sanitize and validate URL"""
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme and parsed.scheme.lower() not in self.safe_url_schemes:
                return None
            
            # Check for suspicious patterns
            if any(pattern.search(url) for pattern in self.dangerous_patterns):
                return None
            
            # Basic URL validation
            if parsed.scheme in ('http', 'https'):
                if not parsed.netloc:
                    return None
            
            return url
            
        except Exception:
            return None
    
    def _escape_html_in_markdown(self, content: str) -> str:
        """Escape HTML that's not part of markdown syntax"""
        # This is a simplified implementation
        # In practice, you'd want a more sophisticated parser
        
        # Escape HTML entities
        content = html.escape(content, quote=False)
        
        # Unescape markdown-specific HTML
        markdown_html = ['<br>', '<hr>']
        for tag in markdown_html:
            content = content.replace(html.escape(tag), tag)
        
        return content
    
    def _validate_urls_in_html(self, content: str) -> str:
        """Validate URLs in HTML attributes"""
        # Use BeautifulSoup for proper HTML parsing
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check all links
            for link in soup.find_all('a', href=True):
                safe_url = self._sanitize_url(link['href'])
                if safe_url:
                    link['href'] = safe_url
                else:
                    link.extract()  # Remove unsafe links
            
            # Check all images
            for img in soup.find_all('img', src=True):
                safe_url = self._sanitize_url(img['src'])
                if safe_url:
                    img['src'] = safe_url
                else:
                    img.extract()  # Remove unsafe images
            
            return str(soup)
            
        except ImportError:
            # Fallback if BeautifulSoup not available
            return content
        except Exception:
            # Return original content if parsing fails
            return content

# Global content sanitizer
content_sanitizer = ContentSanitizer()
```

## Access Control and Permissions

### File System Security
```python
# markitdown_gui/core/security/file_access.py
import os
import stat
import tempfile
from pathlib import Path
from typing import List, Optional, Set
import pwd
import grp

class FileAccessController:
    def __init__(self):
        # Load security configuration
        from ..config_manager import config_manager
        self.config = config_manager.get_section('security.file_access')
        
        # Initialize allowed directories
        self.allowed_directories = self._get_allowed_directories()
        self.restricted_paths = self._get_restricted_paths()
        
    def _get_allowed_directories(self) -> Set[Path]:
        """Get allowed directories based on configuration"""
        allowed = set()
        
        # Always allow user home directory
        allowed.add(Path.home())
        
        # Allow configured directories
        config_dirs = self.config.get('allowed_directories', [])
        for dir_path in config_dirs:
            allowed.add(Path(dir_path).resolve())
        
        # Application directories
        app_dirs = [
            'directories.output',
            'directories.temp', 
            'directories.cache'
        ]
        
        from ..config_manager import config_manager
        for dir_key in app_dirs:
            dir_path = config_manager.get(dir_key)
            if dir_path:
                allowed.add(Path(dir_path).resolve())
        
        return allowed
    
    def _get_restricted_paths(self) -> Set[Path]:
        """Get restricted system paths"""
        restricted = set()
        
        # System directories
        system_dirs = [
            '/etc', '/sys', '/proc', '/dev',
            '/boot', '/root', '/var/log',
            'C:\\Windows', 'C:\\System32',
            'C:\\Program Files', 'C:\\ProgramData'
        ]
        
        for dir_path in system_dirs:
            path = Path(dir_path)
            if path.exists():
                restricted.add(path.resolve())
        
        # Add configured restricted paths
        config_restricted = self.config.get('restricted_directories', [])
        for dir_path in config_restricted:
            restricted.add(Path(dir_path).resolve())
        
        return restricted
    
    def can_read_file(self, file_path: str) -> bool:
        """Check if file can be read safely"""
        try:
            path = Path(file_path).resolve()
            
            # Check if file exists
            if not path.exists():
                return False
            
            # Check if it's actually a file
            if not path.is_file():
                return False
            
            # Check against restricted paths
            if self._is_restricted_path(path):
                return False
            
            # Check if in allowed directories (if restrictions enabled)
            if self.config.get('restrict_to_user_dirs', False):
                if not self._is_in_allowed_directory(path):
                    return False
            
            # Check file permissions
            if not os.access(path, os.R_OK):
                return False
            
            # Check file size
            max_size = self.config.get('max_file_size_mb', 100) * 1024 * 1024
            if path.stat().st_size > max_size:
                return False
            
            return True
            
        except Exception:
            return False
    
    def can_write_to_directory(self, dir_path: str) -> bool:
        """Check if directory can be written to safely"""
        try:
            path = Path(dir_path).resolve()
            
            # Check against restricted paths
            if self._is_restricted_path(path):
                return False
            
            # Check if in allowed directories
            if not self._is_in_allowed_directory(path):
                return False
            
            # Check write permissions
            if not os.access(path, os.W_OK):
                return False
            
            return True
            
        except Exception:
            return False
    
    def create_secure_temp_file(self, suffix: str = '', prefix: str = 'markitdown_') -> str:
        """Create a secure temporary file"""
        temp_dir = self._get_secure_temp_dir()
        
        fd, temp_path = tempfile.mkstemp(
            suffix=suffix,
            prefix=prefix,
            dir=temp_dir
        )
        
        try:
            # Set secure permissions (owner read/write only)
            os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
        finally:
            os.close(fd)
        
        return temp_path
    
    def create_secure_temp_dir(self, prefix: str = 'markitdown_') -> str:
        """Create a secure temporary directory"""
        temp_parent = self._get_secure_temp_dir()
        
        temp_dir = tempfile.mkdtemp(prefix=prefix, dir=temp_parent)
        
        # Set secure permissions (owner access only)
        os.chmod(temp_dir, stat.S_IRWXU)
        
        return temp_dir
    
    def _get_secure_temp_dir(self) -> str:
        """Get secure temporary directory"""
        from ..config_manager import config_manager
        
        # Use configured temp directory
        temp_dir = config_manager.get('directories.temp', tempfile.gettempdir())
        
        # Ensure directory exists and has secure permissions
        os.makedirs(temp_dir, exist_ok=True)
        
        # Set secure permissions if we own the directory
        try:
            stat_info = os.stat(temp_dir)
            if stat_info.st_uid == os.getuid():
                os.chmod(temp_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
        except (OSError, AttributeError):
            pass  # Windows or permission error
        
        return temp_dir
    
    def _is_restricted_path(self, path: Path) -> bool:
        """Check if path is in restricted areas"""
        for restricted in self.restricted_paths:
            try:
                path.relative_to(restricted)
                return True
            except ValueError:
                continue
        return False
    
    def _is_in_allowed_directory(self, path: Path) -> bool:
        """Check if path is in allowed directories"""
        for allowed in self.allowed_directories:
            try:
                path.relative_to(allowed)
                return True
            except ValueError:
                continue
        return False
    
    def validate_output_path(self, output_path: str) -> Optional[str]:
        """Validate and sanitize output path"""
        try:
            path = Path(output_path).resolve()
            
            # Ensure parent directory is writable
            parent_dir = path.parent
            if not self.can_write_to_directory(str(parent_dir)):
                return None
            
            # Sanitize filename
            sanitized_name = content_sanitizer.sanitize_filename(path.name)
            sanitized_path = parent_dir / sanitized_name
            
            return str(sanitized_path)
            
        except Exception:
            return None

# Global file access controller
file_access_controller = FileAccessController()
```

## Secure Configuration Management

### Credential Protection
```python
# markitdown_gui/core/security/credential_manager.py
import keyring
import getpass
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any
import base64
import os

class CredentialManager:
    def __init__(self):
        self.service_name = "MarkItDown-GUI"
        self.cipher_suite = self._get_encryption_key()
    
    def _get_encryption_key(self) -> Optional[Fernet]:
        """Get or create encryption key for local credential storage"""
        try:
            # Try to get key from keyring
            key_b64 = keyring.get_password(self.service_name, "encryption_key")
            
            if not key_b64:
                # Generate new key
                key = Fernet.generate_key()
                key_b64 = base64.b64encode(key).decode()
                
                # Store in keyring
                keyring.set_password(self.service_name, "encryption_key", key_b64)
            else:
                key = base64.b64decode(key_b64.encode())
            
            return Fernet(key)
            
        except Exception:
            # Fallback to no encryption if keyring unavailable
            return None
    
    def store_credential(self, credential_name: str, value: str) -> bool:
        """Store credential securely"""
        try:
            if self.cipher_suite:
                # Encrypt the value
                encrypted_value = self.cipher_suite.encrypt(value.encode())
                storage_value = base64.b64encode(encrypted_value).decode()
            else:
                storage_value = value
            
            keyring.set_password(self.service_name, credential_name, storage_value)
            return True
            
        except Exception as e:
            app_logger.security_logger.error(
                "Failed to store credential",
                credential_name=credential_name,
                error=str(e)
            )
            return False
    
    def get_credential(self, credential_name: str) -> Optional[str]:
        """Retrieve credential securely"""
        try:
            storage_value = keyring.get_password(self.service_name, credential_name)
            
            if not storage_value:
                return None
            
            if self.cipher_suite:
                # Decrypt the value
                encrypted_data = base64.b64decode(storage_value.encode())
                decrypted_value = self.cipher_suite.decrypt(encrypted_data)
                return decrypted_value.decode()
            else:
                return storage_value
                
        except Exception as e:
            app_logger.security_logger.error(
                "Failed to retrieve credential",
                credential_name=credential_name,
                error=str(e)
            )
            return None
    
    def delete_credential(self, credential_name: str) -> bool:
        """Delete stored credential"""
        try:
            keyring.delete_password(self.service_name, credential_name)
            return True
        except Exception:
            return False
    
    def prompt_for_credential(self, credential_name: str, 
                            prompt_text: str = None) -> Optional[str]:
        """Prompt user for credential and store securely"""
        if not prompt_text:
            prompt_text = f"Enter {credential_name}: "
        
        try:
            value = getpass.getpass(prompt_text)
            if value:
                if self.store_credential(credential_name, value):
                    return value
        except KeyboardInterrupt:
            return None
        except Exception as e:
            app_logger.security_logger.error(
                "Failed to prompt for credential",
                credential_name=credential_name,
                error=str(e)
            )
        
        return None

# Global credential manager
credential_manager = CredentialManager()
```

## Network Security

### Secure HTTP Client
```python
# markitdown_gui/core/security/secure_http.py
import requests
import ssl
import certifi
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from typing import Dict, Any, Optional
import urllib3

class SecureHTTPClient:
    def __init__(self):
        self.session = requests.Session()
        self._setup_secure_session()
        
        # Load configuration
        from ..config_manager import config_manager
        self.config = config_manager.get_section('network')
        
        # Set up proxies if configured
        proxy_config = self.config.get('proxy', {})
        if proxy_config.get('enabled', False):
            self._setup_proxy(proxy_config)
    
    def _setup_secure_session(self):
        """Configure session for secure connections"""
        # Disable insecure SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set secure defaults
        self.session.verify = certifi.where()  # Use Mozilla CA bundle
        
        # Set security headers
        self.session.headers.update({
            'User-Agent': 'MarkItDown-GUI/1.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Set timeout
        self.session.timeout = self.config.get('timeout_seconds', 30)
    
    def _setup_proxy(self, proxy_config: Dict[str, Any]):
        """Set up proxy configuration"""
        proxy_host = proxy_config.get('host')
        proxy_port = proxy_config.get('port', 8080)
        
        if not proxy_host:
            return
        
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        
        # Add authentication if provided
        username = proxy_config.get('username')
        password = proxy_config.get('password')
        
        if username and password:
            # Get password from credential manager
            stored_password = credential_manager.get_credential(f"proxy_password_{username}")
            if stored_password:
                password = stored_password
            
            proxy_url = f"http://{username}:{password}@{proxy_host}:{proxy_port}"
        
        self.session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Secure GET request"""
        return self._make_request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Secure POST request"""
        return self._make_request('POST', url, **kwargs)
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make secure HTTP request with validation"""
        # Validate URL
        if not self._is_safe_url(url):
            raise ValueError(f"Unsafe URL: {url}")
        
        # Add security headers
        headers = kwargs.get('headers', {})
        headers.update({
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache'
        })
        kwargs['headers'] = headers
        
        # Log request (without sensitive data)
        app_logger.security_logger.info(
            f"HTTP {method} request",
            url=url,
            headers={k: v for k, v in headers.items() if 'auth' not in k.lower()}
        )
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Validate response
            self._validate_response(response)
            
            return response
            
        except requests.exceptions.SSLError as e:
            app_logger.security_logger.error(
                "SSL verification failed",
                url=url,
                error=str(e)
            )
            raise
        except requests.exceptions.ConnectionError as e:
            app_logger.security_logger.warning(
                "Connection failed",
                url=url,
                error=str(e)
            )
            raise
    
    def _is_safe_url(self, url: str) -> bool:
        """Validate URL for security"""
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            
            # Must use HTTPS for external requests
            if parsed.scheme not in ('https', 'http'):
                return False
            
            # Block internal/private networks
            if parsed.hostname:
                import ipaddress
                try:
                    ip = ipaddress.ip_address(parsed.hostname)
                    if ip.is_private or ip.is_loopback or ip.is_link_local:
                        return False
                except ValueError:
                    pass  # Hostname, not IP
            
            # Block localhost variants
            localhost_names = {'localhost', '127.0.0.1', '::1', '0.0.0.0'}
            if parsed.hostname in localhost_names:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_response(self, response: requests.Response):
        """Validate HTTP response for security"""
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        
        # Log suspicious content types
        suspicious_types = ['text/html', 'application/javascript']
        if any(stype in content_type for stype in suspicious_types):
            app_logger.security_logger.warning(
                "Suspicious content type in response",
                url=response.url,
                content_type=content_type
            )
        
        # Check for security headers
        security_headers = [
            'strict-transport-security',
            'x-content-type-options',
            'x-frame-options',
            'x-xss-protection'
        ]
        
        missing_headers = [h for h in security_headers if h not in response.headers]
        if missing_headers:
            app_logger.security_logger.info(
                "Response missing security headers",
                url=response.url,
                missing_headers=missing_headers
            )

# Global secure HTTP client
secure_http_client = SecureHTTPClient()
```

## Plugin Security

### Plugin Sandbox
```python
# markitdown_gui/core/security/plugin_sandbox.py
import subprocess
import tempfile
import os
import json
from typing import Dict, Any, Optional, List
import threading
import time

class PluginSandbox:
    def __init__(self):
        # Load security configuration
        from ..config_manager import config_manager
        self.config = config_manager.get_section('plugins.security')
        
        self.sandbox_enabled = self.config.get('sandbox_plugins', False)
        self.max_execution_time = self.config.get('max_execution_time', 300)  # 5 minutes
        self.max_memory_mb = self.config.get('max_memory_mb', 256)
        
    def execute_plugin_safely(self, plugin_path: str, plugin_function: str,
                             args: List[Any] = None, kwargs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute plugin in sandboxed environment"""
        if not self.sandbox_enabled:
            # Direct execution (not sandboxed)
            return self._execute_direct(plugin_path, plugin_function, args, kwargs)
        else:
            # Sandboxed execution
            return self._execute_sandboxed(plugin_path, plugin_function, args, kwargs)
    
    def _execute_direct(self, plugin_path: str, plugin_function: str,
                       args: List[Any], kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin directly (not sandboxed)"""
        try:
            # Load plugin module
            import importlib.util
            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            
            # Get function
            func = getattr(plugin_module, plugin_function)
            
            # Execute with timeout
            result = self._execute_with_timeout(func, args or [], kwargs or {})
            
            return {
                'success': True,
                'result': result,
                'error': None
            }
            
        except Exception as e:
            app_logger.security_logger.error(
                "Plugin execution failed",
                plugin_path=plugin_path,
                function=plugin_function,
                error=str(e)
            )
            
            return {
                'success': False,
                'result': None,
                'error': str(e)
            }
    
    def _execute_sandboxed(self, plugin_path: str, plugin_function: str,
                          args: List[Any], kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin in sandboxed environment using subprocess"""
        try:
            # Create sandbox script
            sandbox_script = self._create_sandbox_script(plugin_path, plugin_function, args, kwargs)
            
            # Execute in subprocess with resource limits
            result = self._run_subprocess_with_limits(sandbox_script)
            
            return result
            
        except Exception as e:
            app_logger.security_logger.error(
                "Sandboxed plugin execution failed",
                plugin_path=plugin_path,
                function=plugin_function,
                error=str(e)
            )
            
            return {
                'success': False,
                'result': None,
                'error': str(e)
            }
    
    def _create_sandbox_script(self, plugin_path: str, plugin_function: str,
                              args: List[Any], kwargs: Dict[str, Any]) -> str:
        """Create Python script for sandboxed execution"""
        script_template = '''
import sys
import json
import resource
import signal
import traceback

# Set resource limits
try:
    # Memory limit
    resource.setrlimit(resource.RLIMIT_AS, ({max_memory}, {max_memory}))
    
    # CPU time limit
    resource.setrlimit(resource.RLIMIT_CPU, ({max_time}, {max_time}))
    
    # File size limit
    resource.setrlimit(resource.RLIMIT_FSIZE, (10*1024*1024, 10*1024*1024))  # 10MB
    
    # Number of processes
    resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
    
except (ImportError, OSError):
    pass  # Resource limits not available on this platform

def timeout_handler(signum, frame):
    raise TimeoutError("Plugin execution timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({max_time})

try:
    # Load plugin
    import importlib.util
    spec = importlib.util.spec_from_file_location("plugin", "{plugin_path}")
    plugin_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin_module)
    
    # Get function
    func = getattr(plugin_module, "{plugin_function}")
    
    # Prepare arguments
    args = {args}
    kwargs = {kwargs}
    
    # Execute function
    result = func(*args, **kwargs)
    
    # Return result
    output = {{
        'success': True,
        'result': result,
        'error': None
    }}
    
    print(json.dumps(output))
    
except Exception as e:
    output = {{
        'success': False,
        'result': None,
        'error': str(e),
        'traceback': traceback.format_exc()
    }}
    
    print(json.dumps(output))

finally:
    signal.alarm(0)  # Cancel alarm
'''
        
        return script_template.format(
            max_memory=self.max_memory_mb * 1024 * 1024,
            max_time=self.max_execution_time,
            plugin_path=plugin_path,
            plugin_function=plugin_function,
            args=json.dumps(args or []),
            kwargs=json.dumps(kwargs or {})
        )
    
    def _run_subprocess_with_limits(self, script_content: str) -> Dict[str, Any]:
        """Run script in subprocess with resource limits"""
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            # Execute subprocess
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=tempfile.gettempdir(),  # Restrict working directory
                env=self._get_restricted_env()  # Restricted environment
            )
            
            # Wait with timeout
            try:
                stdout, stderr = process.communicate(timeout=self.max_execution_time)
                
                if process.returncode == 0:
                    # Parse result
                    try:
                        result = json.loads(stdout)
                        return result
                    except json.JSONDecodeError:
                        return {
                            'success': False,
                            'result': None,
                            'error': f"Invalid output: {stdout}"
                        }
                else:
                    return {
                        'success': False,
                        'result': None,
                        'error': f"Process failed: {stderr}"
                    }
                    
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return {
                    'success': False,
                    'result': None,
                    'error': "Plugin execution timed out"
                }
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(script_path)
            except OSError:
                pass
    
    def _get_restricted_env(self) -> Dict[str, str]:
        """Get restricted environment variables for subprocess"""
        # Start with minimal environment
        env = {
            'PATH': os.environ.get('PATH', ''),
            'PYTHONPATH': os.environ.get('PYTHONPATH', ''),
        }
        
        # Remove potentially dangerous variables
        dangerous_vars = [
            'LD_PRELOAD', 'LD_LIBRARY_PATH',
            'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH',
            'HOME', 'USER', 'USERNAME'
        ]
        
        for var in dangerous_vars:
            env.pop(var, None)
        
        return env
    
    def _execute_with_timeout(self, func, args: List[Any], kwargs: Dict[str, Any]):
        """Execute function with timeout"""
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        
        thread.join(timeout=self.max_execution_time)
        
        if thread.is_alive():
            # Thread is still running, timeout occurred
            raise TimeoutError("Function execution timed out")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]

# Global plugin sandbox
plugin_sandbox = PluginSandbox()
```

## Security Monitoring and Incident Response

### Security Event Monitoring
```python
# markitdown_gui/core/security/security_monitor.py
import time
import threading
from typing import Dict, Any, List, Callable
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum

class SecurityEventType(Enum):
    MALICIOUS_FILE = "malicious_file"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    PLUGIN_VIOLATION = "plugin_violation"
    NETWORK_ANOMALY = "network_anomaly"
    CONFIGURATION_CHANGE = "configuration_change"

@dataclass
class SecurityEvent:
    event_type: SecurityEventType
    severity: str
    source: str
    description: str
    details: Dict[str, Any]
    timestamp: float
    resolved: bool = False

class SecurityMonitor:
    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.event_counts: Dict[SecurityEventType, int] = defaultdict(int)
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque())
        self.monitoring = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
    
    def record_security_event(self, event_type: SecurityEventType, severity: str,
                             source: str, description: str, details: Dict[str, Any] = None):
        """Record a security event"""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source=source,
            description=description,
            details=details or {},
            timestamp=time.time()
        )
        
        self.events.append(event)
        self.event_counts[event_type] += 1
        
        # Log security event
        app_logger.security_logger.warning(
            f"Security event: {description}",
            event_type=event_type.value,
            severity=severity,
            source=source,
            details=details
        )
        
        # Check for rate limiting
        if self._check_rate_limit(event_type, source):
            # Create alert
            alert_manager.create_alert(
                AlertSeverity.ERROR if severity == "high" else AlertSeverity.WARNING,
                f"Security Event: {event_type.value}",
                description,
                "security_monitor",
                details
            )
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception:
                pass
    
    def _check_rate_limit(self, event_type: SecurityEventType, source: str) -> bool:
        """Check if event rate exceeds threshold"""
        rate_key = f"{event_type.value}_{source}"
        current_time = time.time()
        
        # Add current event
        self.rate_limits[rate_key].append(current_time)
        
        # Remove events older than 1 hour
        while (self.rate_limits[rate_key] and 
               current_time - self.rate_limits[rate_key][0] > 3600):
            self.rate_limits[rate_key].popleft()
        
        # Check rate (more than 5 events per hour triggers alert)
        return len(self.rate_limits[rate_key]) > 5
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Check for suspicious patterns
                self._check_suspicious_patterns()
                
                # Clean old events (keep last 1000)
                if len(self.events) > 1000:
                    self.events = self.events[-1000:]
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                app_logger.log_error(e, {"component": "security_monitor"})
                time.sleep(60)
    
    def _check_suspicious_patterns(self):
        """Check for suspicious activity patterns"""
        current_time = time.time()
        recent_events = [e for e in self.events if current_time - e.timestamp < 300]  # Last 5 minutes
        
        # Check for repeated malicious file attempts
        malicious_events = [e for e in recent_events if e.event_type == SecurityEventType.MALICIOUS_FILE]
        if len(malicious_events) > 3:
            self.record_security_event(
                SecurityEventType.SUSPICIOUS_ACTIVITY,
                "high",
                "pattern_detection",
                f"Multiple malicious file attempts: {len(malicious_events)} in 5 minutes",
                {"event_count": len(malicious_events)}
            )
        
        # Check for unauthorized access patterns
        access_events = [e for e in recent_events if e.event_type == SecurityEventType.UNAUTHORIZED_ACCESS]
        if len(access_events) > 5:
            self.record_security_event(
                SecurityEventType.SUSPICIOUS_ACTIVITY,
                "medium",
                "pattern_detection",
                f"Multiple unauthorized access attempts: {len(access_events)} in 5 minutes",
                {"event_count": len(access_events)}
            )
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security event summary"""
        current_time = time.time()
        
        # Events in last 24 hours
        recent_events = [e for e in self.events if current_time - e.timestamp < 86400]
        
        # Count by type
        type_counts = defaultdict(int)
        for event in recent_events:
            type_counts[event.event_type.value] += 1
        
        # Count by severity
        severity_counts = defaultdict(int)
        for event in recent_events:
            severity_counts[event.severity] += 1
        
        return {
            "total_events_24h": len(recent_events),
            "events_by_type": dict(type_counts),
            "events_by_severity": dict(severity_counts),
            "latest_event": recent_events[-1].description if recent_events else None,
            "timestamp": current_time
        }
    
    def add_alert_callback(self, callback: Callable):
        """Add security alert callback"""
        self.alert_callbacks.append(callback)

# Global security monitor
security_monitor = SecurityMonitor()

# Integration functions for other components
def log_file_security_event(file_path: str, validation_result: FileValidation):
    """Log file security events"""
    if validation_result.result == ValidationResult.DANGEROUS:
        security_monitor.record_security_event(
            SecurityEventType.MALICIOUS_FILE,
            "high",
            "file_validator",
            f"Dangerous file detected: {file_path}",
            {
                "file_path": file_path,
                "reasons": validation_result.reasons,
                "file_type": validation_result.file_type,
                "file_size": validation_result.file_size
            }
        )
    elif validation_result.result == ValidationResult.SUSPICIOUS:
        security_monitor.record_security_event(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            "medium",
            "file_validator",
            f"Suspicious file detected: {file_path}",
            {
                "file_path": file_path,
                "reasons": validation_result.reasons,
                "file_type": validation_result.file_type
            }
        )

def log_access_violation(operation: str, path: str, reason: str):
    """Log file access violations"""
    security_monitor.record_security_event(
        SecurityEventType.UNAUTHORIZED_ACCESS,
        "medium",
        "file_access_controller",
        f"Access denied: {operation} on {path}",
        {
            "operation": operation,
            "path": path,
            "reason": reason
        }
    )
```

## Security Configuration

### Security Configuration Template
```yaml
# config/security.yaml
security:
  # File access restrictions
  file_access:
    restrict_to_user_dirs: true
    allow_system_dirs: false
    max_file_size_mb: 100
    scan_for_malware: false
    allowed_directories:
      - "/home/user/Documents"
      - "/home/user/Downloads"
    restricted_directories:
      - "/etc"
      - "/sys"
      - "/proc"
  
  # Input validation
  validation:
    enable_file_validation: true
    enable_content_sanitization: true
    strict_type_checking: true
    reject_suspicious_files: true
  
  # Plugin security
  plugins:
    sandbox_plugins: true
    verify_signatures: false
    allow_unsigned: true
    max_execution_time: 300
    max_memory_mb: 256
  
  # Network security
  network:
    verify_ssl: true
    allow_http: false
    block_private_ips: true
    max_redirects: 3
  
  # Privacy settings
  privacy:
    collect_usage_stats: false
    crash_reporting: true
    share_error_logs: false
    anonymize_logs: true
  
  # Monitoring
  monitoring:
    enable_security_monitoring: true
    log_security_events: true
    alert_on_threats: true
    rate_limit_alerts: true
```

## Related Documentation

- 🚀 [Deployment Guide](deployment.md) - Production deployment
- ⚙️ [Configuration Management](configuration.md) - Environment settings
- 📊 [Performance Tuning](performance.md) - Optimization guidelines
- 📋 [Monitoring](monitoring.md) - System monitoring and alerts

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development