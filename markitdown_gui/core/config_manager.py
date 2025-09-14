"""
설정 관리 시스템
애플리케이션 설정의 저장, 로드, 관리를 담당
"""

import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .models import AppConfig, FileType, LLMConfig, LLMProvider, FileConflictConfig, FileConflictPolicy


logger = logging.getLogger(__name__)


class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_dir: Path = None):
        """
        초기화
        
        Args:
            config_dir: 설정 파일 디렉토리 (기본값: ./config)
        """
        if config_dir is None:
            config_dir = Path("config")
        
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        
        self.settings_file = self.config_dir / "settings.ini"
        self.file_types_file = self.config_dir / "file_types.json"
        
        self._config = AppConfig()
        self._file_types_config = {}
    
    def load_config(self) -> AppConfig:
        """설정 로드"""
        try:
            self._load_settings()
            self._load_file_types()
            logger.info("설정이 성공적으로 로드되었습니다.")
        except Exception as e:
            logger.warning(f"설정 로드 실패, 기본 설정 사용: {e}")
            self._create_default_config()
        
        return self._config
    
    def save_config(self, config: AppConfig = None) -> bool:
        """
        설정 저장
        
        Args:
            config: 저장할 설정 (None이면 현재 설정 저장)
        
        Returns:
            저장 성공 여부
        """
        if config:
            self._config = config
        
        try:
            self._save_settings()
            self._save_file_types()
            logger.info("설정이 성공적으로 저장되었습니다.")
            return True
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            return False
    
    def _load_settings(self):
        """settings.ini 파일 로드"""
        if not self.settings_file.exists():
            logger.info("settings.ini 파일이 없습니다. 기본 설정을 생성합니다.")
            self._create_default_config()
            return
        
        config_parser = configparser.ConfigParser()
        config_parser.read(self.settings_file, encoding='utf-8')
        
        # General section
        if config_parser.has_section('General'):
            general = config_parser['General']
            self._config.language = general.get('language', self._config.language)
            self._config.theme = general.get('theme', self._config.theme)
        
        # Conversion section
        if config_parser.has_section('Conversion'):
            conversion = config_parser['Conversion']
            self._config.output_directory = Path(
                conversion.get('output_directory', str(self._config.output_directory))
            )
            self._config.max_concurrent_conversions = conversion.getint(
                'max_concurrent_conversions', self._config.max_concurrent_conversions
            )
            self._config.include_subdirectories = conversion.getboolean(
                'include_subdirectories', self._config.include_subdirectories
            )
            self._config.max_file_size_mb = conversion.getint(
                'max_file_size_mb', self._config.max_file_size_mb
            )
            self._config.save_to_original_directory = conversion.getboolean(
                'save_to_original_directory', self._config.save_to_original_directory
            )
        
        # FileConflict section
        if config_parser.has_section('FileConflict'):
            conflict = config_parser['FileConflict']
            
            # 기본 정책 로드
            policy_str = conflict.get('default_policy', 'ask_user')
            try:
                default_policy = FileConflictPolicy(policy_str)
            except ValueError:
                default_policy = FileConflictPolicy.ASK_USER
            
            # FileConflictConfig 객체 생성
            self._config.conflict_config = FileConflictConfig(
                default_policy=default_policy,
                auto_rename_pattern=conflict.get('auto_rename_pattern', '{name}_{counter}{ext}'),
                remember_choices=conflict.getboolean('remember_choices', True),
                apply_to_all=conflict.getboolean('apply_to_all', False),
                backup_original=conflict.getboolean('backup_original', False),
                conflict_log_enabled=conflict.getboolean('conflict_log_enabled', True)
            )
        
        # LLM section
        if config_parser.has_section('LLM'):
            llm = config_parser['LLM']
            # API 키는 더 이상 설정 파일에 저장하지 않음 (keyring 사용)
            # 하위 호환성을 위해 읽기는 지원
            self._config.openai_api_key = llm.get('openai_api_key', self._config.openai_api_key)
            self._config.llm_model = llm.get('llm_model', self._config.llm_model)
            
            # 새로운 LLM 설정들
            self._config.llm_provider = llm.get('llm_provider', self._config.llm_provider)
            self._config.llm_base_url = llm.get('llm_base_url', self._config.llm_base_url)
            self._config.llm_api_version = llm.get('llm_api_version', self._config.llm_api_version)
            
            # OCR 설정
            self._config.enable_llm_ocr = llm.getboolean('enable_llm_ocr', self._config.enable_llm_ocr)
            self._config.ocr_language = llm.get('ocr_language', self._config.ocr_language)
            self._config.max_image_size = llm.getint('max_image_size', self._config.max_image_size)
            
            # 고급 설정
            self._config.llm_temperature = llm.getfloat('llm_temperature', self._config.llm_temperature)
            self._config.llm_max_tokens = llm.getint('llm_max_tokens', self._config.llm_max_tokens)
            self._config.llm_system_prompt = llm.get('llm_system_prompt', self._config.llm_system_prompt)
            
            # 토큰 사용량 추적
            self._config.track_token_usage = llm.getboolean('track_token_usage', self._config.track_token_usage)
            self._config.token_usage_limit_monthly = llm.getint('token_usage_limit_monthly', self._config.token_usage_limit_monthly)
        
        # UI section
        if config_parser.has_section('UI'):
            ui = config_parser['UI']
            self._config.window_width = ui.getint('window_width', self._config.window_width)
            self._config.window_height = ui.getint('window_height', self._config.window_height)
            
            # Recent directories 파싱
            recent_dirs_str = ui.get('recent_directories', '')
            if recent_dirs_str:
                self._config.recent_directories = [
                    dir.strip() for dir in recent_dirs_str.split(',') if dir.strip()
                ]
    
    def _load_file_types(self):
        """file_types.json 파일 로드"""
        if not self.file_types_file.exists():
            self._create_default_file_types()
            return
        
        try:
            with open(self.file_types_file, 'r', encoding='utf-8') as f:
                self._file_types_config = json.load(f)
            
            # 지원 확장자 업데이트
            if 'supported_extensions' in self._file_types_config:
                self._config.supported_extensions = self._file_types_config['supported_extensions']
        
        except json.JSONDecodeError as e:
            logger.error(f"file_types.json 파싱 에러: {e}")
            self._create_default_file_types()
    
    def _save_settings(self):
        """settings.ini 파일 저장"""
        config_parser = configparser.ConfigParser()
        
        # General section
        config_parser.add_section('General')
        config_parser['General']['language'] = self._config.language
        config_parser['General']['theme'] = self._config.theme
        
        # Conversion section
        config_parser.add_section('Conversion')
        config_parser['Conversion']['output_directory'] = str(self._config.output_directory)
        config_parser['Conversion']['max_concurrent_conversions'] = str(self._config.max_concurrent_conversions)
        config_parser['Conversion']['include_subdirectories'] = str(self._config.include_subdirectories)
        config_parser['Conversion']['max_file_size_mb'] = str(self._config.max_file_size_mb)
        config_parser['Conversion']['save_to_original_directory'] = str(self._config.save_to_original_directory)
        
        # FileConflict section
        if self._config.conflict_config:
            config_parser.add_section('FileConflict')
            conflict_config = self._config.conflict_config
            config_parser['FileConflict']['default_policy'] = conflict_config.default_policy.value
            config_parser['FileConflict']['auto_rename_pattern'] = conflict_config.auto_rename_pattern
            config_parser['FileConflict']['remember_choices'] = str(conflict_config.remember_choices)
            config_parser['FileConflict']['apply_to_all'] = str(conflict_config.apply_to_all)
            config_parser['FileConflict']['backup_original'] = str(conflict_config.backup_original)
            config_parser['FileConflict']['conflict_log_enabled'] = str(conflict_config.conflict_log_enabled)
        
        # LLM section
        config_parser.add_section('LLM')
        # API 키는 keyring에 저장하므로 설정 파일에는 저장하지 않음
        # (보안을 위해)
        config_parser['LLM']['llm_model'] = self._config.llm_model
        
        # 공급업체 및 연결 설정
        config_parser['LLM']['llm_provider'] = self._config.llm_provider
        if self._config.llm_base_url:
            config_parser['LLM']['llm_base_url'] = self._config.llm_base_url
        if self._config.llm_api_version:
            config_parser['LLM']['llm_api_version'] = self._config.llm_api_version
        
        # OCR 설정
        config_parser['LLM']['enable_llm_ocr'] = str(self._config.enable_llm_ocr)
        config_parser['LLM']['ocr_language'] = self._config.ocr_language
        config_parser['LLM']['max_image_size'] = str(self._config.max_image_size)
        
        # 고급 설정
        config_parser['LLM']['llm_temperature'] = str(self._config.llm_temperature)
        config_parser['LLM']['llm_max_tokens'] = str(self._config.llm_max_tokens)
        config_parser['LLM']['llm_system_prompt'] = self._config.llm_system_prompt
        
        # 토큰 사용량 추적
        config_parser['LLM']['track_token_usage'] = str(self._config.track_token_usage)
        config_parser['LLM']['token_usage_limit_monthly'] = str(self._config.token_usage_limit_monthly)
        
        # UI section
        config_parser.add_section('UI')
        config_parser['UI']['window_width'] = str(self._config.window_width)
        config_parser['UI']['window_height'] = str(self._config.window_height)
        config_parser['UI']['recent_directories'] = ','.join(self._config.recent_directories)
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            config_parser.write(f)
    
    def _save_file_types(self):
        """file_types.json 파일 저장"""
        self._file_types_config.update({
            'supported_extensions': self._config.supported_extensions,
            'file_type_descriptions': {
                file_type.value: self._get_file_type_description(file_type)
                for file_type in FileType if file_type != FileType.UNKNOWN
            }
        })
        
        with open(self.file_types_file, 'w', encoding='utf-8') as f:
            json.dump(self._file_types_config, f, indent=2, ensure_ascii=False)
    
    def _create_default_config(self):
        """기본 설정 생성 및 저장"""
        self._config = AppConfig()
        self._create_default_file_types()
        self.save_config()
    
    def _create_default_file_types(self):
        """기본 파일 타입 설정 생성"""
        self._file_types_config = {
            'supported_extensions': [e.value for e in FileType if e != FileType.UNKNOWN],
            'file_type_descriptions': {
                file_type.value: self._get_file_type_description(file_type)
                for file_type in FileType if file_type != FileType.UNKNOWN
            }
        }
    
    def _get_file_type_description(self, file_type: FileType) -> str:
        """파일 타입 설명 반환"""
        descriptions = {
            FileType.DOCX: "Microsoft Word 문서",
            FileType.PPTX: "Microsoft PowerPoint 프레젠테이션",
            FileType.XLSX: "Microsoft Excel 스프레드시트",
            FileType.XLS: "Microsoft Excel 97-2003 스프레드시트",
            FileType.PDF: "PDF 문서",
            FileType.JPG: "JPEG 이미지",
            FileType.JPEG: "JPEG 이미지",
            FileType.PNG: "PNG 이미지",
            FileType.GIF: "GIF 이미지",
            FileType.BMP: "BMP 이미지",
            FileType.TIFF: "TIFF 이미지",
            FileType.MP3: "MP3 오디오",
            FileType.WAV: "WAV 오디오",
            FileType.HTML: "HTML 웹 페이지",
            FileType.HTM: "HTML 웹 페이지",
            FileType.CSV: "CSV 데이터",
            FileType.JSON: "JSON 데이터",
            FileType.XML: "XML 데이터",
            FileType.TXT: "텍스트 파일",
            FileType.ZIP: "ZIP 압축 파일",
            FileType.EPUB: "EPUB 전자책",
        }
        return descriptions.get(file_type, "알 수 없는 파일 타입")
    
    def add_recent_directory(self, directory: str):
        """최근 사용 디렉토리 추가"""
        if directory in self._config.recent_directories:
            self._config.recent_directories.remove(directory)
        
        self._config.recent_directories.insert(0, directory)
        
        # 최대 10개만 유지
        self._config.recent_directories = self._config.recent_directories[:10]
    
    def get_config(self) -> AppConfig:
        """현재 설정 반환"""
        return self._config
    
    def update_config(self, **kwargs):
        """설정 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                logger.warning(f"알 수 없는 설정 키: {key}")
    
    def reset_to_default(self):
        """기본 설정으로 리셋"""
        self._config = AppConfig()
        self.save_config()
    
    def reset_to_defaults(self):
        """기본 설정으로 리셋 (settings_dialog에서 사용)"""
        self.reset_to_default()
    
    def set_value(self, key: str, value: Any):
        """설정 값 설정"""
        if hasattr(self._config, key):
            setattr(self._config, key, value)
        else:
            logger.warning(f"알 수 없는 설정 키: {key}")
    
    def get_llm_config(self) -> LLMConfig:
        """
        LLM 설정 반환
        
        Returns:
            LLM 설정 객체
        """
        try:
            provider = LLMProvider(self._config.llm_provider)
        except ValueError:
            provider = LLMProvider.OPENAI
        
        return LLMConfig(
            provider=provider,
            model=self._config.llm_model,
            base_url=self._config.llm_base_url,
            api_version=self._config.llm_api_version,
            
            # 요청 설정
            temperature=self._config.llm_temperature,
            max_tokens=self._config.llm_max_tokens,
            timeout=30,  # 기본값
            max_retries=3,  # 기본값
            
            # OCR 설정
            enable_ocr=self._config.enable_llm_ocr,
            ocr_language=self._config.ocr_language,
            max_image_size=self._config.max_image_size,
            
            # 시스템 프롬프트
            system_prompt=self._config.llm_system_prompt,
            
            # 토큰 사용량 추적
            track_usage=self._config.track_token_usage,
            usage_limit_monthly=self._config.token_usage_limit_monthly
        )
    
    def update_llm_config(self, llm_config: LLMConfig):
        """
        LLM 설정 업데이트
        
        Args:
            llm_config: 새로운 LLM 설정
        """
        self._config.llm_provider = llm_config.provider.value
        self._config.llm_model = llm_config.model
        self._config.llm_base_url = llm_config.base_url
        self._config.llm_api_version = llm_config.api_version
        
        # 요청 설정
        self._config.llm_temperature = llm_config.temperature
        self._config.llm_max_tokens = llm_config.max_tokens
        
        # OCR 설정
        self._config.enable_llm_ocr = llm_config.enable_ocr
        self._config.ocr_language = llm_config.ocr_language
        self._config.max_image_size = llm_config.max_image_size
        
        # 시스템 프롬프트
        self._config.llm_system_prompt = llm_config.system_prompt
        
        # 토큰 사용량 추적
        self._config.track_token_usage = llm_config.track_usage
        self._config.token_usage_limit_monthly = llm_config.usage_limit_monthly
    
    def is_llm_configured(self) -> bool:
        """
        LLM 설정 완료 여부 확인
        
        Returns:
            설정 완료 여부
        """
        # keyring에 API 키가 저장되어 있는지 확인하려면 
        # LLMManager를 사용해야 하므로 여기서는 기본 설정만 확인
        return (
            self._config.llm_provider and
            self._config.llm_model
        )
    
    def get_ocr_settings(self) -> Dict[str, Any]:
        """
        OCR 설정 반환
        
        Returns:
            OCR 설정 딕셔너리
        """
        return {
            'enable_llm_ocr': self._config.enable_llm_ocr,
            'ocr_language': self._config.ocr_language,
            'max_image_size': self._config.max_image_size
        }
    
    def update_ocr_settings(self, **kwargs):
        """
        OCR 설정 업데이트
        
        Args:
            **kwargs: OCR 설정 키-값 쌍
        """
        ocr_keys = ['enable_llm_ocr', 'ocr_language', 'max_image_size']
        
        for key, value in kwargs.items():
            if key in ocr_keys and hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                logger.warning(f"Unknown OCR setting: {key}")
    
    def get_token_usage_settings(self) -> Dict[str, Any]:
        """
        토큰 사용량 설정 반환
        
        Returns:
            토큰 사용량 설정 딕셔너리
        """
        return {
            'track_token_usage': self._config.track_token_usage,
            'token_usage_limit_monthly': self._config.token_usage_limit_monthly
        }
    
    def get_file_conflict_config(self) -> FileConflictConfig:
        """
        파일 충돌 설정 반환
        
        Returns:
            파일 충돌 설정 객체
        """
        if self._config.conflict_config is None:
            self._config.conflict_config = FileConflictConfig()
        return self._config.conflict_config
    
    def update_file_conflict_config(self, conflict_config: FileConflictConfig):
        """
        파일 충돌 설정 업데이트
        
        Args:
            conflict_config: 새로운 파일 충돌 설정
        """
        self._config.conflict_config = conflict_config
    
    def get_save_location_settings(self) -> Dict[str, Any]:
        """
        저장 위치 설정 반환
        
        Returns:
            저장 위치 설정 딕셔너리
        """
        return {
            'save_to_original_directory': self._config.save_to_original_directory,
            'output_directory': str(self._config.output_directory)
        }
    
    def update_save_location_settings(self, save_to_original: bool, output_directory: Optional[Path] = None):
        """
        저장 위치 설정 업데이트
        
        Args:
            save_to_original: 원본 디렉토리에 저장 여부
            output_directory: 커스텀 출력 디렉토리 (save_to_original이 False일 때 사용)
        """
        self._config.save_to_original_directory = save_to_original
        if not save_to_original and output_directory:
            self._config.output_directory = output_directory