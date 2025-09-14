"""
번역 파일 유효성 검사 도구
Translation file validation utilities
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass

from .logger import get_logger

logger = get_logger(__name__)


@dataclass 
class ValidationResult:
    """유효성 검사 결과"""
    language_code: str
    is_valid: bool
    missing_keys: Set[str]
    extra_keys: Set[str]
    empty_values: Set[str]
    invalid_format_keys: Set[str]
    issues_count: int
    
    def __post_init__(self):
        self.issues_count = (
            len(self.missing_keys) + 
            len(self.extra_keys) + 
            len(self.empty_values) + 
            len(self.invalid_format_keys)
        )
        self.is_valid = self.issues_count == 0


class TranslationValidator:
    """번역 파일 유효성 검사기"""
    
    def __init__(self, translations_dir: Path):
        self.translations_dir = Path(translations_dir)
        self.template_file = self.translations_dir / "template.json"
        self.template_keys: Set[str] = set()
        self.template_data: Dict[str, Any] = {}
        
    def load_template(self) -> bool:
        """템플릿 파일 로드"""
        if not self.template_file.exists():
            logger.error(f"Template file not found: {self.template_file}")
            return False
        
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                self.template_data = json.load(f)
                self.template_keys = self._extract_keys(self.template_data)
            
            logger.info(f"Template loaded with {len(self.template_keys)} keys")
            return True
            
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return False
    
    def _extract_keys(self, obj: Any, prefix: str = "") -> Set[str]:
        """중첩된 딕셔너리에서 모든 키 추출"""
        keys = set()
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    keys.update(self._extract_keys(value, full_key))
                else:
                    keys.add(full_key)
        
        return keys
    
    def _find_empty_values(self, obj: Any, prefix: str = "") -> Set[str]:
        """빈 값을 가진 키 찾기"""
        empty_keys = set()
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    empty_keys.update(self._find_empty_values(value, full_key))
                elif not value or (isinstance(value, str) and not value.strip()):
                    empty_keys.add(full_key)
        
        return empty_keys
    
    def _find_format_issues(self, obj: Any, template_obj: Any, prefix: str = "") -> Set[str]:
        """포맷 문제가 있는 키 찾기 (플레이스홀더 불일치)"""
        format_issues = set()
        
        if isinstance(obj, dict) and isinstance(template_obj, dict):
            for key in obj.keys():
                if key in template_obj:
                    full_key = f"{prefix}.{key}" if prefix else key
                    
                    if isinstance(obj[key], dict) and isinstance(template_obj[key], dict):
                        format_issues.update(self._find_format_issues(
                            obj[key], template_obj[key], full_key
                        ))
                    elif isinstance(obj[key], str) and isinstance(template_obj[key], str):
                        # 플레이스홀더 체크 {0}, {1} 등
                        template_placeholders = self._extract_placeholders(template_obj[key])
                        translation_placeholders = self._extract_placeholders(obj[key])
                        
                        if template_placeholders != translation_placeholders:
                            format_issues.add(full_key)
        
        return format_issues
    
    def _extract_placeholders(self, text: str) -> Set[str]:
        """문자열에서 플레이스홀더 추출 {0}, {1} 등"""
        import re
        placeholders = set()
        
        # {숫자} 형태의 플레이스홀더 찾기
        pattern = r'\{(\d+)\}'
        matches = re.findall(pattern, text)
        placeholders.update(matches)
        
        # {변수명} 형태도 찾기 (선택사항)
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        matches = re.findall(pattern, text)
        placeholders.update(matches)
        
        return placeholders
    
    def validate_translation_file(self, language_code: str) -> ValidationResult:
        """단일 번역 파일 유효성 검사"""
        if not self.template_keys:
            if not self.load_template():
                return ValidationResult(
                    language_code=language_code,
                    is_valid=False,
                    missing_keys=set(),
                    extra_keys=set(),
                    empty_values=set(),
                    invalid_format_keys=set(),
                    issues_count=1
                )
        
        translation_file = self.translations_dir / f"{language_code}.json"
        
        if not translation_file.exists():
            logger.error(f"Translation file not found: {translation_file}")
            return ValidationResult(
                language_code=language_code,
                is_valid=False,
                missing_keys=self.template_keys.copy(),
                extra_keys=set(),
                empty_values=set(),
                invalid_format_keys=set(),
                issues_count=len(self.template_keys)
            )
        
        try:
            with open(translation_file, 'r', encoding='utf-8') as f:
                translation_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading translation file {translation_file}: {e}")
            return ValidationResult(
                language_code=language_code,
                is_valid=False,
                missing_keys=self.template_keys.copy(),
                extra_keys=set(),
                empty_values=set(),
                invalid_format_keys=set(),
                issues_count=len(self.template_keys)
            )
        
        # 키 추출
        translation_keys = self._extract_keys(translation_data)
        
        # 누락된 키
        missing_keys = self.template_keys - translation_keys
        
        # 추가된 키
        extra_keys = translation_keys - self.template_keys
        
        # 빈 값
        empty_values = self._find_empty_values(translation_data)
        
        # 포맷 문제
        invalid_format_keys = self._find_format_issues(
            translation_data, self.template_data
        )
        
        return ValidationResult(
            language_code=language_code,
            is_valid=len(missing_keys) == 0 and len(extra_keys) == 0 and 
                     len(empty_values) == 0 and len(invalid_format_keys) == 0,
            missing_keys=missing_keys,
            extra_keys=extra_keys,
            empty_values=empty_values,
            invalid_format_keys=invalid_format_keys,
            issues_count=0  # __post_init__에서 계산됨
        )
    
    def validate_all_translations(self) -> Dict[str, ValidationResult]:
        """모든 번역 파일 유효성 검사"""
        results = {}
        
        # 번역 파일들 찾기
        translation_files = list(self.translations_dir.glob("*.json"))
        translation_files = [f for f in translation_files if f.name != "template.json"]
        
        for translation_file in translation_files:
            language_code = translation_file.stem
            result = self.validate_translation_file(language_code)
            results[language_code] = result
        
        return results
    
    def generate_missing_keys_template(self, language_code: str) -> Dict[str, Any]:
        """누락된 키에 대한 템플릿 생성"""
        result = self.validate_translation_file(language_code)
        
        if not result.missing_keys:
            return {}
        
        # 누락된 키들을 템플릿 구조로 재구성
        missing_template = {}
        
        for key in result.missing_keys:
            self._set_nested_value(missing_template, key, f"[TRANSLATE: {key}]")
        
        return missing_template
    
    def _set_nested_value(self, obj: Dict[str, Any], key_path: str, value: Any):
        """중첩된 딕셔너리에 값 설정"""
        keys = key_path.split('.')
        current = obj
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def fix_translation_file(self, language_code: str, auto_fill: bool = False) -> bool:
        """번역 파일 수정 (누락된 키 추가)"""
        try:
            translation_file = self.translations_dir / f"{language_code}.json"
            
            # 기존 번역 데이터 로드
            translation_data = {}
            if translation_file.exists():
                with open(translation_file, 'r', encoding='utf-8') as f:
                    translation_data = json.load(f)
            
            # 누락된 키들 추가
            missing_template = self.generate_missing_keys_template(language_code)
            
            if missing_template:
                # 깊은 병합
                self._deep_merge(translation_data, missing_template)
                
                # 파일에 저장
                with open(translation_file, 'w', encoding='utf-8') as f:
                    json.dump(translation_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Fixed translation file: {translation_file}")
                return True
            
            return True  # 수정할 것이 없음
            
        except Exception as e:
            logger.error(f"Error fixing translation file {language_code}: {e}")
            return False
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """딕셔너리 깊은 병합"""
        for key, value in source.items():
            if key in target:
                if isinstance(target[key], dict) and isinstance(value, dict):
                    self._deep_merge(target[key], value)
                # 기존 값이 있으면 유지
            else:
                target[key] = value
    
    def print_validation_report(self, results: Dict[str, ValidationResult]):
        """유효성 검사 보고서 출력"""
        print("\n" + "="*60)
        print("Translation Validation Report")
        print("="*60)
        
        total_languages = len(results)
        valid_languages = sum(1 for r in results.values() if r.is_valid)
        
        print(f"\nSummary: {valid_languages}/{total_languages} languages are valid")
        
        for language_code, result in sorted(results.items()):
            print(f"\n--- {language_code} ---")
            
            if result.is_valid:
                print("✅ VALID")
            else:
                print("❌ INVALID")
                print(f"   Total issues: {result.issues_count}")
                
                if result.missing_keys:
                    print(f"   Missing keys ({len(result.missing_keys)}):")
                    for key in sorted(result.missing_keys):
                        print(f"     - {key}")
                
                if result.extra_keys:
                    print(f"   Extra keys ({len(result.extra_keys)}):")
                    for key in sorted(result.extra_keys):
                        print(f"     + {key}")
                
                if result.empty_values:
                    print(f"   Empty values ({len(result.empty_values)}):")
                    for key in sorted(result.empty_values):
                        print(f"     ∅ {key}")
                
                if result.invalid_format_keys:
                    print(f"   Format issues ({len(result.invalid_format_keys)}):")
                    for key in sorted(result.invalid_format_keys):
                        print(f"     ⚠ {key}")
        
        print("\n" + "="*60)


def main():
    """CLI 인터페이스"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Translation file validator")
    parser.add_argument("translations_dir", help="Path to translations directory")
    parser.add_argument("--fix", action="store_true", help="Fix missing keys")
    parser.add_argument("--lang", help="Validate specific language only")
    
    args = parser.parse_args()
    
    translations_dir = Path(args.translations_dir)
    if not translations_dir.exists():
        print(f"Error: Directory not found: {translations_dir}")
        sys.exit(1)
    
    validator = TranslationValidator(translations_dir)
    
    if args.lang:
        # 단일 언어 검사
        result = validator.validate_translation_file(args.lang)
        results = {args.lang: result}
    else:
        # 모든 언어 검사
        results = validator.validate_all_translations()
    
    # 보고서 출력
    validator.print_validation_report(results)
    
    # 수정 모드
    if args.fix:
        print("\nFixing translation files...")
        for language_code, result in results.items():
            if not result.is_valid and result.missing_keys:
                success = validator.fix_translation_file(language_code)
                if success:
                    print(f"✅ Fixed {language_code}")
                else:
                    print(f"❌ Failed to fix {language_code}")
    
    # 종료 코드 설정
    if any(not r.is_valid for r in results.values()):
        sys.exit(1)
    else:
        print("\n✅ All translations are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()