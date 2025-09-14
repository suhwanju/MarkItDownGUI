"""
국제화(i18n) 관리자
PyQt6의 QTranslator와 QLocale을 사용한 다국어 지원 시스템
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtCore import (
    QObject, QTranslator, QLocale, QCoreApplication, 
    pyqtSignal, QSettings, QStandardPaths, QLibraryInfo
)
from PyQt6.QtGui import QFont, QFontDatabase, QFontMetrics
from .font_manager import get_font_manager
from PyQt6.QtWidgets import QApplication

from .logger import get_logger
from .exceptions import ConfigurationError, ValidationError


logger = get_logger(__name__)


class SupportedLanguage(Enum):
    """지원되는 언어 코드"""
    ENGLISH = "en_US"
    KOREAN = "ko_KR"
    

@dataclass
class LanguageInfo:
    """언어 정보"""
    code: str
    name: str
    native_name: str
    locale: QLocale
    default_font_family: str
    font_size_adjustment: int = 0  # 기본 크기 대비 조정값
    requires_fallback_font: bool = False
    

@dataclass
class FontInfo:
    """폰트 정보"""
    family: str
    size: int
    weight: int = 50  # QFont.Weight.Normal
    italic: bool = False
    

class I18nManager(QObject):
    """국제화 관리자"""
    
    # 시그널
    language_changed = pyqtSignal(str)  # 언어 코드
    translation_loaded = pyqtSignal(str)  # 언어 코드
    translation_missing = pyqtSignal(str, str)  # 키, 언어 코드
    
    def __init__(self, app: Optional[QCoreApplication] = None):
        super().__init__()
        
        self.app = app or QCoreApplication.instance()
        if not self.app:
            raise ConfigurationError("QCoreApplication instance is required")
        
        # 현재 상태
        self.current_language: str = "en_US"
        self.current_translator: Optional[QTranslator] = None
        self.qt_translator: Optional[QTranslator] = None
        self.loaded_translations: Dict[str, Dict[str, Any]] = {}
        self.missing_keys: Set[str] = set()
        
        # 경로 설정
        try:
            self.translations_dir = Path(__file__).parent.parent / "resources" / "translations"
            self.translations_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating translations directory: {e}")
            # 대체 경로 사용
            self.translations_dir = Path.home() / ".markitdown_gui" / "translations"
            self.translations_dir.mkdir(parents=True, exist_ok=True)
        
        # 지원 언어 정보
        self.supported_languages = {
            "en_US": LanguageInfo(
                code="en_US",
                name="English",
                native_name="English",
                locale=QLocale(QLocale.Language.English, QLocale.Country.UnitedStates),
                default_font_family="Segoe UI",  # Windows 기본
                font_size_adjustment=0
            ),
            "ko_KR": LanguageInfo(
                code="ko_KR", 
                name="Korean",
                native_name="한국어",
                locale=QLocale(QLocale.Language.Korean, QLocale.Country.SouthKorea),
                default_font_family="Malgun Gothic",  # Windows 한글 폰트
                font_size_adjustment=1,  # 한글은 약간 큰 사이즈가 읽기 좋음
                requires_fallback_font=True
            )
        }
        
        # 폰트 설정
        self.font_cache: Dict[str, QFont] = {}
        self.translation_cache: Dict[str, str] = {}  # 번역 결과 캐시
        self.cache_size_limit = 1000  # 캐시 최대 크기
        self._init_fonts()
        
        # 설정 로드
        try:
            settings = QSettings()
            saved_language = settings.value("language", self._detect_system_language())
        except Exception as e:
            logger.warning(f"Error loading settings: {e}")
            saved_language = self._detect_system_language()
        
        # 초기 언어 설정
        if not self.set_language(saved_language):
            # 저장된 언어 로드 실패시 기본 언어로 대체
            logger.warning(f"Failed to load saved language {saved_language}, falling back to en_US")
            self.set_language("en_US")
        
        logger.info(f"I18n Manager initialized with language: {self.current_language}")
    
    def _detect_system_language(self) -> str:
        """시스템 로케일 기반 언어 감지"""
        try:
            system_locale = QLocale.system()
            language = system_locale.language()
            country = system_locale.country()
            
            # 한국어 감지
            if language == QLocale.Language.Korean:
                return "ko_KR"
            
            # 영어는 기본
            return "en_US"
            
        except Exception as e:
            logger.warning(f"System language detection failed: {e}")
            return "en_US"
    
    def _init_fonts(self):
        """폰트 초기화 및 최적 폰트 선택"""
        try:
            # PyQt6에서 QFontDatabase는 static 메서드로만 사용
            # font_db = QFontDatabase() 제거 - PyQt6에서는 인스턴스 생성 불가
            
            for lang_code, lang_info in self.supported_languages.items():
                # 기본 폰트 시도
                font_families = [lang_info.default_font_family]
                
                # 언어별 대체 폰트 추가
                if lang_code == "ko_KR":
                    font_families.extend([
                        "Noto Sans CJK KR",     # Google Noto 폰트
                        "Apple SD Gothic Neo",   # macOS
                        "맑은 고딕",             # Windows 한글명
                        "Malgun Gothic",         # Windows 영문명
                        "Nanum Gothic",          # 나눔 폰트
                        "Dotum",                 # 구형 Windows
                        "Arial Unicode MS"       # 유니코드 대체
                    ])
                elif lang_code == "en_US":
                    font_families.extend([
                        "Arial",
                        "Helvetica",
                        "Calibri",
                        "Tahoma",
                        "Verdana"
                    ])
                
                # 사용 가능한 첫 번째 폰트 선택
                selected_font_family = None
                # PyQt6에서는 QFontDatabase의 static 메서드 직접 호출
                available_families = QFontDatabase.families()
                
                for family in font_families:
                    # QStringList의 contains() 메서드 사용 또는 Python list로 변환하여 검사
                    if family in available_families:
                        selected_font_family = family
                        break
                
                if not selected_font_family:
                    # 시스템 기본 폰트 사용 - static 메서드 호출
                    selected_font_family = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
                    logger.warning(f"No specific font found for {lang_code}, using system default: {selected_font_family}")
                
                # 폰트 정보 업데이트
                lang_info.default_font_family = selected_font_family
                
                logger.debug(f"Font for {lang_code}: {selected_font_family}")
        
        except Exception as e:
            logger.error(f"Error initializing fonts: {e}")
            # 폰트 초기화 실패시 기본값 설정
            for lang_code, lang_info in self.supported_languages.items():
                if lang_code == "ko_KR":
                    lang_info.default_font_family = "Arial Unicode MS"
                else:
                    lang_info.default_font_family = "Arial"
    
    def get_supported_languages(self) -> Dict[str, LanguageInfo]:
        """지원되는 언어 목록 반환"""
        return self.supported_languages.copy()
    
    def get_current_language(self) -> str:
        """현재 언어 코드 반환"""
        return self.current_language
    
    def get_current_language_info(self) -> LanguageInfo:
        """현재 언어 정보 반환"""
        return self.supported_languages[self.current_language]
    
    def set_language(self, language_code: str) -> bool:
        """언어 설정 변경"""
        # 입력 검증
        if not language_code or not isinstance(language_code, str):
            logger.error(f"Invalid language code: {language_code}")
            return False
            
        if language_code not in self.supported_languages:
            logger.error(f"Unsupported language: {language_code}")
            return False
        
        if language_code == self.current_language:
            logger.debug(f"Language {language_code} already active")
            return True
        
        try:
            # 기존 번역기 제거
            self._remove_translators()
            
            # 새 번역 로드
            success = self._load_translation(language_code)
            if success:
                self.current_language = language_code
                
                # Qt 내장 번역 로드
                self._load_qt_translations(language_code)
                
                # 로케일 설정
                lang_info = self.supported_languages[language_code]
                QLocale.setDefault(lang_info.locale)
                
                # 설정 저장
                try:
                    settings = QSettings()
                    settings.setValue("language", language_code)
                    # 캐시 무효화 (언어 변경시)
                    self.translation_cache.clear()
                except Exception as e:
                    logger.warning(f"Error saving language setting: {e}")
                
                # 시그널 발송
                self.language_changed.emit(language_code)
                
                logger.info(f"Language changed to: {language_code}")
                return True
            else:
                logger.error(f"Failed to load translation for: {language_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting language {language_code}: {e}")
            return False
    
    def _remove_translators(self):
        """기존 번역기 제거"""
        if self.current_translator:
            self.app.removeTranslator(self.current_translator)
            self.current_translator = None
        
        if self.qt_translator:
            self.app.removeTranslator(self.qt_translator)
            self.qt_translator = None
    
    def _load_translation(self, language_code: str) -> bool:
        """번역 파일 로드"""
        try:
            if not language_code or not isinstance(language_code, str):
                logger.error(f"Invalid language code: {language_code}")
                return False
                
            translation_file = self.translations_dir / f"{language_code}.json"
            
            if not translation_file.exists():
                logger.error(f"Translation file not found: {translation_file}")
                return False
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # 번역 데이터 검증
            if not isinstance(translations, dict):
                logger.error(f"Invalid translation data structure in {language_code}.json")
                return False
                
            # 번역 데이터 저장
            self.loaded_translations[language_code] = translations
            
            # QTranslator 생성 및 설치
            translator = QTranslator()
            
            # JSON 데이터를 QTranslator로 변환하는 것은 복잡하므로
            # 우리만의 번역 시스템을 사용
            self.current_translator = translator
            self.app.installTranslator(translator)
            
            self.translation_loaded.emit(language_code)
            
            logger.info(f"Translation loaded: {language_code} with {len(self._extract_keys(translations))} keys")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {language_code}.json: {e}")
            return False
        except FileNotFoundError as e:
            logger.error(f"Translation file not found: {e}")
            return False
        except PermissionError as e:
            logger.error(f"Permission denied reading translation file: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading translation {language_code}: {e}")
            return False
    
    def _load_qt_translations(self, language_code: str):
        """Qt 내장 번역 로드"""
        try:
            if not language_code or not isinstance(language_code, str):
                logger.warning(f"Invalid language code for Qt translations: {language_code}")
                return
                
            # 언어 코드를 Qt 로케일 형식으로 변환
            if language_code == "ko_KR":
                qt_lang = "ko"
            elif language_code.startswith("en"):
                qt_lang = "en"
            else:
                qt_lang = language_code.split('_')[0]
            
            # Qt 번역기 생성
            qt_translator = QTranslator()
            
            # Qt 번역 파일 경로 찾기
            qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
            
            # Qt 번역 파일 로드 시도
            if qt_translator.load(f"qtbase_{qt_lang}", qt_translations_path):
                self.qt_translator = qt_translator
                self.app.installTranslator(qt_translator)
                logger.debug(f"Qt translations loaded for: {qt_lang}")
            else:
                logger.debug(f"Qt translations not found for: {qt_lang}")
                
        except Exception as e:
            logger.debug(f"Error loading Qt translations: {e}")
    
    def tr(self, key: str, context: str = "", *args) -> str:
        """번역 문자열 가져오기 (빠른 버전)"""
        # 캐시 확인
        if not args:  # 인수가 없는 경우만 캐시 사용
            cache_key = f"{self.current_language}:{context}:{key}"
            if cache_key in self.translation_cache:
                return self.translation_cache[cache_key]
        
        result = self.translate(key, context, *args)
        
        # 결과 캐싱 (arguments 없는 경우만)
        if not args and len(self.translation_cache) < self.cache_size_limit:
            cache_key = f"{self.current_language}:{context}:{key}"
            self.translation_cache[cache_key] = result
        
        return result
    
    def translate(self, key: str, context: str = "", *args) -> str:
        """번역 문자열 가져오기 (상세 버전)"""
        if not key:
            return ""
        
        try:
            # 현재 언어의 번역 데이터 가져오기
            translations = self.loaded_translations.get(self.current_language, {})
            
            # 번역 결과 찾기
            result = self._find_translation(translations, key, context)
            
            # 현재 언어에서 찾지 못한 경우 영어 대체 시도
            if result is None and self.current_language != "en_US":
                en_translations = self.loaded_translations.get("en_US", {})
                result = self._find_translation(en_translations, key, context)
                
                if result is not None:
                    logger.debug(f"Using English fallback for '{key}' in context '{context}'")
            
            # 모든 시도가 실패한 경우
            if result is None:
                result = key  # 키 자체를 반환
                self._track_missing_key(key, context)
                logger.warning(f"Translation not found: key='{key}', context='{context}'")
            
            # 문자열 포매팅 (Python style)
            if args and isinstance(result, str):
                try:
                    result = result.format(*args)
                except (IndexError, KeyError, ValueError) as e:
                    logger.warning(f"Translation formatting error for key '{key}': {e}")
                    # 포매팅 실패 시 원본 문자열 반환
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error for key '{key}', context '{context}': {e}")
            return key  # 에러 시 키 자체 반환
    
    def _find_translation(self, translations: Dict[str, Any], key: str, context: str = "") -> Optional[str]:
        """번역 데이터에서 키 찾기"""
        if not isinstance(translations, dict):
            return None
        
        try:
            # 컨텍스트가 있는 경우 계층적 검색
            if context:
                # 컨텍스트 경로를 따라 이동
                current_level = translations
                search_path = context.split('.')
                
                for path_part in search_path:
                    if isinstance(current_level, dict) and path_part in current_level:
                        current_level = current_level[path_part]
                    else:
                        return None  # 컨텍스트 경로가 존재하지 않음
                
                # 최종 레벨에서 키 검색
                if isinstance(current_level, dict) and key in current_level:
                    value = current_level[key]
                    return str(value) if value is not None else None
            
            # 컨텍스트가 없는 경우 직접 검색
            else:
                if key in translations:
                    value = translations[key]
                    return str(value) if value is not None else None
            
            return None
            
        except Exception as e:
            logger.debug(f"Error finding translation: key='{key}', context='{context}', error={e}")
            return None
    
    def _track_missing_key(self, key: str, context: str = ""):
        """누락된 번역 키 추적"""
        try:
            full_key = f"{context}.{key}" if context else key
            if full_key not in self.missing_keys:
                self.missing_keys.add(full_key)
                self.translation_missing.emit(full_key, self.current_language)
                logger.debug(f"Missing translation: {full_key} for {self.current_language}")
        except Exception as e:
            logger.error(f"Error tracking missing key '{key}': {e}")
    
    def get_font_for_language(self, language_code: str = None, base_size: int = 10) -> QFont:
        """언어에 최적화된 폰트 반환"""
        try:
            # 입력 검증
            if base_size <= 0 or base_size > 72:
                logger.warning(f"Invalid font size {base_size}, using default 10")
                base_size = 10
                
            if language_code is None:
                language_code = self.current_language
            
            if not isinstance(language_code, str) or language_code not in self.supported_languages:
                logger.warning(f"Invalid language code {language_code}, using en_US")
                language_code = "en_US"
            
            # 캐시 확인
            cache_key = f"{language_code}_{base_size}"
            if cache_key in self.font_cache:
                return QFont(self.font_cache[cache_key])
            
            # 언어 정보 가져오기
            lang_info = self.supported_languages[language_code]
            
            # 안전한 폰트 생성 (DirectWrite 오류 방지)
            try:
                font_manager = get_font_manager()
                
                # 언어별 선호 폰트 목록
                preferred_fonts = [lang_info.default_font_family]
                if language_code == "ko_KR":
                    preferred_fonts.extend(["Malgun Gothic", "맑은 고딕", "Dotum", "굴림"])
                elif language_code == "ja_JP":
                    preferred_fonts.extend(["Meiryo", "Yu Gothic", "MS Gothic"])
                
                # 안전한 폰트 가져오기
                font = font_manager.get_safe_font(
                    preferred_families=preferred_fonts,
                    point_size=base_size + lang_info.font_size_adjustment,
                    weight=QFont.Weight.Medium if language_code == "ko_KR" else QFont.Weight.Normal
                )
                
                # 한국어의 경우 추가 최적화
                if language_code == "ko_KR":
                    font.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
                
            except Exception as font_error:
                logger.warning(f"Font manager error, using fallback: {font_error}")
                # 기본 폰트 생성 방식으로 fallback
                font = QFont()
                font.setFamily(lang_info.default_font_family)
                font.setPointSize(base_size + lang_info.font_size_adjustment)
                
                if language_code == "ko_KR":
                    font.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
                    if font.weight() == QFont.Weight.Normal:
                        font.setWeight(QFont.Weight.Medium)
            
            # 캐시 저장
            self.font_cache[cache_key] = font
            
            return QFont(font)  # 복사본 반환
            
        except Exception as e:
            logger.error(f"Error creating font for {language_code}: {e}")
            # 기본 폰트 반환
            fallback_font = QFont()
            fallback_font.setPointSize(base_size)
            return fallback_font
    
    def get_current_font(self, base_size: int = 10) -> QFont:
        """현재 언어의 폰트 반환"""
        return self.get_font_for_language(self.current_language, base_size)
    
    def format_number(self, number: float, decimals: int = 2) -> str:
        """현재 로케일에 맞는 숫자 형식"""
        try:
            if not isinstance(number, (int, float)):
                logger.warning(f"Invalid number type: {type(number)}")
                return str(number)
                
            if decimals < 0 or decimals > 10:
                decimals = 2
                
            locale = self.supported_languages[self.current_language].locale
            return locale.toString(float(number), 'f', decimals)
        except Exception as e:
            logger.error(f"Error formatting number {number}: {e}")
            return str(number)
    
    def format_currency(self, amount: float, currency: str = "") -> str:
        """현재 로케일에 맞는 통화 형식"""
        try:
            if not isinstance(amount, (int, float)):
                logger.warning(f"Invalid amount type: {type(amount)}")
                return str(amount)
                
            locale = self.supported_languages[self.current_language].locale
            if currency and isinstance(currency, str):
                return f"{locale.toString(float(amount), 'f', 2)} {currency}"
            else:
                return locale.toCurrencyString(float(amount))
        except Exception as e:
            logger.error(f"Error formatting currency {amount}: {e}")
            return str(amount)
    
    def format_date(self, date, format_type: str = "short") -> str:
        """현재 로케일에 맞는 날짜 형식"""
        try:
            if date is None:
                return ""
                
            locale = self.supported_languages[self.current_language].locale
            
            if format_type == "short":
                format_str = locale.dateFormat(QLocale.FormatType.ShortFormat)
            elif format_type == "long":
                format_str = locale.dateFormat(QLocale.FormatType.LongFormat)
            else:
                format_str = str(format_type)
            
            return locale.toString(date, format_str)
        except Exception as e:
            logger.error(f"Error formatting date {date}: {e}")
            return str(date) if date else ""
    
    def format_time(self, time, format_type: str = "short") -> str:
        """현재 로케일에 맞는 시간 형식"""
        try:
            if time is None:
                return ""
                
            locale = self.supported_languages[self.current_language].locale
            
            if format_type == "short":
                format_str = locale.timeFormat(QLocale.FormatType.ShortFormat)
            elif format_type == "long":
                format_str = locale.timeFormat(QLocale.FormatType.LongFormat)
            else:
                format_str = str(format_type)
            
            return locale.toString(time, format_str)
        except Exception as e:
            logger.error(f"Error formatting time {time}: {e}")
            return str(time) if time else ""
    
    def validate_translation_files(self) -> Dict[str, List[str]]:
        """번역 파일 유효성 검사"""
        validation_results = {}
        
        # 템플릿 키 로드 (영어 기준)
        template_file = self.translations_dir / "en_US.json"
        if not template_file.exists():
            return {"error": ["Template file en_US.json not found"]}
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template = json.load(f)
        except Exception as e:
            return {"error": [f"Error loading template: {e}"]}
        
        # 모든 키 추출 (중첩 구조 포함)
        template_keys = self._extract_keys(template)
        
        # 각 언어 파일 검사
        for lang_code in self.supported_languages.keys():
            lang_file = self.translations_dir / f"{lang_code}.json"
            issues = []
            
            if not lang_file.exists():
                issues.append(f"Translation file {lang_file.name} not found")
                validation_results[lang_code] = issues
                continue
            
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                
                # 키 추출
                translation_keys = self._extract_keys(translations)
                
                # 누락된 키 찾기
                missing_keys = template_keys - translation_keys
                if missing_keys:
                    issues.append(f"Missing keys: {', '.join(sorted(missing_keys))}")
                
                # 추가된 키 찾기
                extra_keys = translation_keys - template_keys
                if extra_keys:
                    issues.append(f"Extra keys: {', '.join(sorted(extra_keys))}")
                
                # 빈 값 찾기
                empty_values = self._find_empty_values(translations)
                if empty_values:
                    issues.append(f"Empty values: {', '.join(sorted(empty_values))}")
                
                validation_results[lang_code] = issues
                
            except Exception as e:
                validation_results[lang_code] = [f"Error loading file: {e}"]
        
        return validation_results
    
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
    
    def get_missing_keys(self) -> Set[str]:
        """런타임에 감지된 누락 키 목록"""
        return self.missing_keys.copy()
    
    def clear_missing_keys(self):
        """누락 키 목록 초기화"""
        self.missing_keys.clear()
    
    def clear_cache(self):
        """번역 및 폰트 캐시 청소"""
        try:
            self.translation_cache.clear()
            self.font_cache.clear()
            logger.debug("Translation and font caches cleared")
        except Exception as e:
            logger.error(f"Error clearing caches: {e}")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """캐시 통계 정보 반환"""
        return {
            "translation_cache_size": len(self.translation_cache),
            "font_cache_size": len(self.font_cache),
            "missing_keys_count": len(self.missing_keys)
        }
    
    def reload_translations(self) -> bool:
        """번역 파일 다시 로드"""
        try:
            current_lang = self.current_language
            self.loaded_translations.clear()
            self.missing_keys.clear()
            self.clear_cache()
            return self.set_language(current_lang)
        except Exception as e:
            logger.error(f"Error reloading translations: {e}")
            return False


# 전역 인스턴스
_i18n_manager: Optional[I18nManager] = None


def get_i18n_manager() -> Optional[I18nManager]:
    """전역 i18n 매니저 인스턴스 가져오기"""
    return _i18n_manager


def init_i18n(app: QCoreApplication = None) -> I18nManager:
    """i18n 매니저 초기화"""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager(app)
    return _i18n_manager


def tr(key: str, context: str = "", *args) -> str:
    """전역 번역 함수 - 매개변수 검증 포함"""
    try:
        # 매개변수 검증
        if not key or not isinstance(key, str):
            logger.warning(f"Invalid translation key: {key}")
            return str(key) if key else ""
            
        if context is not None and not isinstance(context, str):
            logger.warning(f"Invalid translation context: {context}")
            context = str(context)
        
        if _i18n_manager:
            return _i18n_manager.tr(key, context, *args)
        else:
            logger.warning("I18n manager not initialized")
            return key
            
    except Exception as e:
        logger.error(f"Error in global tr() function: {e}")
        return str(key) if key else ""


# 편의 함수들
def set_language(language_code: str) -> bool:
    """언어 설정 변경"""
    try:
        if _i18n_manager:
            return _i18n_manager.set_language(language_code)
        else:
            logger.error("I18n manager not initialized")
            return False
    except Exception as e:
        logger.error(f"Error setting language {language_code}: {e}")
        return False


def get_current_language() -> str:
    """현재 언어 코드 반환"""
    try:
        if _i18n_manager:
            return _i18n_manager.get_current_language()
        else:
            logger.warning("I18n manager not initialized")
            return "en_US"
    except Exception as e:
        logger.error(f"Error getting current language: {e}")
        return "en_US"


def get_current_font(base_size: int = 10) -> Optional[QFont]:
    """현재 언어의 최적 폰트 반환"""
    try:
        if _i18n_manager:
            return _i18n_manager.get_current_font(base_size)
        else:
            logger.warning("I18n manager not initialized, returning default font")
            return QFont()
    except Exception as e:
        logger.error(f"Error getting current font: {e}")
        return QFont()