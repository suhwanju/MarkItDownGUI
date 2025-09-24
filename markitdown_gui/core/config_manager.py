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

            # Advanced conversion settings
            self._config.include_metadata = conversion.getboolean(
                'include_metadata', self._config.include_metadata
            )
            self._config.preserve_formatting = conversion.getboolean(
                'preserve_formatting', self._config.preserve_formatting
            )
            self._config.extract_images = conversion.getboolean(
                'extract_images', self._config.extract_images
            )
            self._config.include_toc = conversion.getboolean(
                'include_toc', self._config.include_toc
            )
            self._config.max_workers = conversion.getint(
                'max_workers', self._config.max_workers
            )
            self._config.timeout = conversion.getint(
                'timeout', self._config.timeout
            )
            self._config.retry_count = conversion.getint(
                'retry_count', self._config.retry_count
            )
            self._config.ocr_quality = conversion.get(
                'ocr_quality', self._config.ocr_quality
            )
            self._config.image_quality = conversion.getint(
                'image_quality', self._config.image_quality
            )
            self._config.encoding = conversion.get(
                'encoding', self._config.encoding
            )
            self._config.line_ending = conversion.get(
                'line_ending', self._config.line_ending
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
            self._config.llm_system_prompt = llm.get('llm_system_prompt', getattr(self._config, 'llm_system_prompt', ''))

            # 토큰 사용량 추적
            self._config.track_token_usage = llm.getboolean('track_token_usage', getattr(self._config, 'track_token_usage', False))
            self._config.token_usage_limit_monthly = llm.getint('token_usage_limit_monthly', getattr(self._config, 'token_usage_limit_monthly', 1000000))

        # ImagePreprocessing section
        if config_parser.has_section('ImagePreprocessing'):
            preprocessing = config_parser['ImagePreprocessing']
            self._config.enable_image_preprocessing = preprocessing.getboolean(
                'enable_image_preprocessing', self._config.enable_image_preprocessing
            )
            self._config.preprocessing_mode = preprocessing.get(
                'preprocessing_mode', self._config.preprocessing_mode
            )
            self._config.preprocessing_quality_threshold = preprocessing.getfloat(
                'preprocessing_quality_threshold', self._config.preprocessing_quality_threshold
            )
            self._config.preprocessing_enable_parallel = preprocessing.getboolean(
                'preprocessing_enable_parallel', self._config.preprocessing_enable_parallel
            )
            self._config.preprocessing_cache_strategy = preprocessing.get(
                'preprocessing_cache_strategy', self._config.preprocessing_cache_strategy
            )
            self._config.preprocessing_max_processing_time = preprocessing.getfloat(
                'preprocessing_max_processing_time', self._config.preprocessing_max_processing_time
            )

            # 향상 기능 목록 (콤마로 구분된 문자열)
            enhancements_str = preprocessing.get('preprocessing_enabled_enhancements', '')
            if enhancements_str:
                self._config.preprocessing_enabled_enhancements = [
                    enhancement.strip() for enhancement in enhancements_str.split(',')
                    if enhancement.strip()
                ]
        
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

        # OCR Enhancements section
        if config_parser.has_section('ocr_enhancements'):
            ocr_enhancements = config_parser['ocr_enhancements']

            # OCR Enhancement 설정을 _config에 저장 (임시 저장소)
            if not hasattr(self._config, 'ocr_enhancements_config'):
                self._config.ocr_enhancements_config = {}

            # 모든 OCR enhancement 설정 로드
            self._config.ocr_enhancements_config.update({
                'enabled': ocr_enhancements.getboolean('enabled', False),
                'accuracy_boost_enabled': ocr_enhancements.getboolean('accuracy_boost_enabled', False),
                'preprocessing_enabled': ocr_enhancements.getboolean('preprocessing_enabled', True),
                'post_processing_enabled': ocr_enhancements.getboolean('post_processing_enabled', True),
                'language_detection_enabled': ocr_enhancements.getboolean('language_detection_enabled', True),
                'confidence_analysis_enabled': ocr_enhancements.getboolean('confidence_analysis_enabled', True),
                'layout_analysis_enabled': ocr_enhancements.getboolean('layout_analysis_enabled', False),
                'quality_assessment_enabled': ocr_enhancements.getboolean('quality_assessment_enabled', True),
                'max_concurrent_enhancements': ocr_enhancements.getint('max_concurrent_enhancements', 2),
                'enhancement_timeout': ocr_enhancements.getint('enhancement_timeout', 60),
                'cache_results': ocr_enhancements.getboolean('cache_results', True),
                'cache_ttl': ocr_enhancements.getint('cache_ttl', 3600),
                'min_confidence_threshold': ocr_enhancements.getfloat('min_confidence_threshold', 0.7),
                'retry_on_low_confidence': ocr_enhancements.getboolean('retry_on_low_confidence', True),
                'max_retry_attempts': ocr_enhancements.getint('max_retry_attempts', 2),
                'image_enhancement_enabled': ocr_enhancements.getboolean('image_enhancement_enabled', True),
                'noise_reduction_enabled': ocr_enhancements.getboolean('noise_reduction_enabled', True),
                'contrast_adjustment_enabled': ocr_enhancements.getboolean('contrast_adjustment_enabled', True),
                'spell_check_enabled': ocr_enhancements.getboolean('spell_check_enabled', False),
                'grammar_check_enabled': ocr_enhancements.getboolean('grammar_check_enabled', False),
                'formatting_cleanup_enabled': ocr_enhancements.getboolean('formatting_cleanup_enabled', True)
            })
    
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

        # Advanced conversion settings
        config_parser['Conversion']['include_metadata'] = str(self._config.include_metadata)
        config_parser['Conversion']['preserve_formatting'] = str(self._config.preserve_formatting)
        config_parser['Conversion']['extract_images'] = str(self._config.extract_images)
        config_parser['Conversion']['include_toc'] = str(self._config.include_toc)
        config_parser['Conversion']['max_workers'] = str(self._config.max_workers)
        config_parser['Conversion']['timeout'] = str(self._config.timeout)
        config_parser['Conversion']['retry_count'] = str(self._config.retry_count)
        config_parser['Conversion']['ocr_quality'] = str(self._config.ocr_quality)
        config_parser['Conversion']['image_quality'] = str(self._config.image_quality)
        config_parser['Conversion']['encoding'] = str(self._config.encoding)
        config_parser['Conversion']['line_ending'] = str(self._config.line_ending)
        
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

        # ImagePreprocessing section
        config_parser.add_section('ImagePreprocessing')
        config_parser['ImagePreprocessing']['enable_image_preprocessing'] = str(self._config.enable_image_preprocessing)
        config_parser['ImagePreprocessing']['preprocessing_mode'] = self._config.preprocessing_mode
        config_parser['ImagePreprocessing']['preprocessing_quality_threshold'] = str(self._config.preprocessing_quality_threshold)
        config_parser['ImagePreprocessing']['preprocessing_enable_parallel'] = str(self._config.preprocessing_enable_parallel)
        config_parser['ImagePreprocessing']['preprocessing_cache_strategy'] = self._config.preprocessing_cache_strategy
        config_parser['ImagePreprocessing']['preprocessing_max_processing_time'] = str(self._config.preprocessing_max_processing_time)
        config_parser['ImagePreprocessing']['preprocessing_enabled_enhancements'] = ','.join(self._config.preprocessing_enabled_enhancements)

        # UI section
        config_parser.add_section('UI')
        config_parser['UI']['window_width'] = str(self._config.window_width)
        config_parser['UI']['window_height'] = str(self._config.window_height)
        config_parser['UI']['recent_directories'] = ','.join(self._config.recent_directories)

        # OCR Enhancements section
        if hasattr(self._config, 'ocr_enhancements_config'):
            config_parser.add_section('ocr_enhancements')
            ocr_config = self._config.ocr_enhancements_config

            config_parser['ocr_enhancements']['enabled'] = str(ocr_config.get('enabled', False))
            config_parser['ocr_enhancements']['accuracy_boost_enabled'] = str(ocr_config.get('accuracy_boost_enabled', False))
            config_parser['ocr_enhancements']['preprocessing_enabled'] = str(ocr_config.get('preprocessing_enabled', True))
            config_parser['ocr_enhancements']['post_processing_enabled'] = str(ocr_config.get('post_processing_enabled', True))
            config_parser['ocr_enhancements']['language_detection_enabled'] = str(ocr_config.get('language_detection_enabled', True))
            config_parser['ocr_enhancements']['confidence_analysis_enabled'] = str(ocr_config.get('confidence_analysis_enabled', True))
            config_parser['ocr_enhancements']['layout_analysis_enabled'] = str(ocr_config.get('layout_analysis_enabled', False))
            config_parser['ocr_enhancements']['quality_assessment_enabled'] = str(ocr_config.get('quality_assessment_enabled', True))
            config_parser['ocr_enhancements']['max_concurrent_enhancements'] = str(ocr_config.get('max_concurrent_enhancements', 2))
            config_parser['ocr_enhancements']['enhancement_timeout'] = str(ocr_config.get('enhancement_timeout', 60))
            config_parser['ocr_enhancements']['cache_results'] = str(ocr_config.get('cache_results', True))
            config_parser['ocr_enhancements']['cache_ttl'] = str(ocr_config.get('cache_ttl', 3600))
            config_parser['ocr_enhancements']['min_confidence_threshold'] = str(ocr_config.get('min_confidence_threshold', 0.7))
            config_parser['ocr_enhancements']['retry_on_low_confidence'] = str(ocr_config.get('retry_on_low_confidence', True))
            config_parser['ocr_enhancements']['max_retry_attempts'] = str(ocr_config.get('max_retry_attempts', 2))
            config_parser['ocr_enhancements']['image_enhancement_enabled'] = str(ocr_config.get('image_enhancement_enabled', True))
            config_parser['ocr_enhancements']['noise_reduction_enabled'] = str(ocr_config.get('noise_reduction_enabled', True))
            config_parser['ocr_enhancements']['contrast_adjustment_enabled'] = str(ocr_config.get('contrast_adjustment_enabled', True))
            config_parser['ocr_enhancements']['spell_check_enabled'] = str(ocr_config.get('spell_check_enabled', False))
            config_parser['ocr_enhancements']['grammar_check_enabled'] = str(ocr_config.get('grammar_check_enabled', False))
            config_parser['ocr_enhancements']['formatting_cleanup_enabled'] = str(ocr_config.get('formatting_cleanup_enabled', True))

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

    def get_ocr_enhancement_config(self) -> Dict[str, Any]:
        """
        OCR Enhancement 설정 반환

        Returns:
            OCR Enhancement 설정 딕셔너리
        """
        # 기본값 설정
        default_config = {
            'enabled': False,
            'accuracy_boost_enabled': False,
            'preprocessing_enabled': True,
            'post_processing_enabled': True,
            'language_detection_enabled': True,
            'confidence_analysis_enabled': True,
            'layout_analysis_enabled': False,
            'quality_assessment_enabled': True,
            'max_concurrent_enhancements': 2,
            'enhancement_timeout': 60,
            'cache_results': True,
            'cache_ttl': 3600,
            'min_confidence_threshold': 0.7,
            'retry_on_low_confidence': True,
            'max_retry_attempts': 2,
            'image_enhancement_enabled': True,
            'noise_reduction_enabled': True,
            'contrast_adjustment_enabled': True,
            'spell_check_enabled': False,
            'grammar_check_enabled': False,
            'formatting_cleanup_enabled': True
        }

        if hasattr(self._config, 'ocr_enhancements_config'):
            # 기본값과 저장된 설정 병합
            default_config.update(self._config.ocr_enhancements_config)
        else:
            # 처음 호출시 기본값으로 초기화
            self._config.ocr_enhancements_config = default_config.copy()

        return default_config

    def update_ocr_enhancement_config(self, updates: Dict[str, Any]):
        """
        OCR Enhancement 설정 업데이트

        Args:
            updates: 업데이트할 설정 딕셔너리
        """
        # 기존 설정이 없으면 기본값으로 초기화
        if not hasattr(self._config, 'ocr_enhancements_config'):
            self._config.ocr_enhancements_config = self.get_ocr_enhancement_config()

        # 업데이트 적용
        for key, value in updates.items():
            if key in self._config.ocr_enhancements_config:
                self._config.ocr_enhancements_config[key] = value
            else:
                logger.warning(f"Unknown OCR enhancement setting: {key}")

    def is_ocr_enhancement_enabled(self) -> bool:
        """
        OCR Enhancement 모듈 활성화 여부 확인

        Returns:
            활성화 여부
        """
        config = self.get_ocr_enhancement_config()
        return config.get('enabled', False)

    def get_ocr_enhancement_model_config(self):
        """
        OCR Enhancement 모델 설정 객체 생성

        Returns:
            OCREnhancementConfig 객체 (모듈이 사용 가능한 경우)
        """
        try:
            from .ocr_enhancements.models import OCREnhancementConfig

            config_dict = self.get_ocr_enhancement_config()

            # 딕셔너리를 OCREnhancementConfig 객체로 변환
            return OCREnhancementConfig(**config_dict)

        except ImportError:
            logger.debug("OCR Enhancement module not available")
            return None
        except Exception as e:
            logger.error(f"Failed to create OCR Enhancement config: {e}")
            return None

    def get_preprocessing_config(self) -> Dict[str, Any]:
        """
        이미지 전처리 설정을 딕셔너리로 반환

        Returns:
            전처리 설정 딕셔너리
        """
        return {
            'mode': self._config.preprocessing_mode,
            'quality_threshold': self._config.preprocessing_quality_threshold,
            'enabled_enhancements': self._config.preprocessing_enabled_enhancements,
            'enable_parallel_processing': self._config.preprocessing_enable_parallel,
            'cache_strategy': self._config.preprocessing_cache_strategy,
            'max_processing_time': self._config.preprocessing_max_processing_time,
            'enable_preprocessing': self._config.enable_image_preprocessing
        }

    def update_preprocessing_config(self, **kwargs):
        """
        이미지 전처리 설정 업데이트

        Args:
            **kwargs: 전처리 설정 키-값 쌍
        """
        preprocessing_keys = [
            'enable_image_preprocessing', 'preprocessing_mode', 'preprocessing_quality_threshold',
            'preprocessing_enabled_enhancements', 'preprocessing_enable_parallel',
            'preprocessing_cache_strategy', 'preprocessing_max_processing_time'
        ]

        for key, value in kwargs.items():
            if key in preprocessing_keys and hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                logger.warning(f"Unknown preprocessing setting: {key}")

    def get_preprocessing_settings(self) -> Dict[str, Any]:
        """
        전처리 설정 반환 (UI용)

        Returns:
            전처리 설정 딕셔너리
        """
        return {
            'enable_image_preprocessing': self._config.enable_image_preprocessing,
            'preprocessing_mode': self._config.preprocessing_mode,
            'preprocessing_quality_threshold': self._config.preprocessing_quality_threshold,
            'preprocessing_enabled_enhancements': self._config.preprocessing_enabled_enhancements,
            'preprocessing_enable_parallel': self._config.preprocessing_enable_parallel,
            'preprocessing_cache_strategy': self._config.preprocessing_cache_strategy,
            'preprocessing_max_processing_time': self._config.preprocessing_max_processing_time
        }

    # API Key Management Methods
    def get_llm_api_key(self) -> Optional[str]:
        """
        Get LLM API key from secure storage or config file

        Returns:
            API key string if available, None otherwise
        """
        try:
            # Try keyring first (secure storage)
            try:
                import keyring
                api_key = keyring.get_password("markitdown_gui", "openai_api_key")
                if api_key and api_key.strip():
                    logger.debug("Retrieved API key from secure keyring storage")
                    return api_key.strip()
            except ImportError:
                logger.debug("Keyring not available, falling back to config file")
            except Exception as e:
                logger.debug(f"Keyring access failed: {e}, falling back to config file")

            # Fall back to config file (less secure but compatible)
            if hasattr(self._config, 'openai_api_key') and self._config.openai_api_key:
                api_key = self._config.openai_api_key.strip()
                if api_key and api_key != "[PLACEHOLDER]":
                    logger.debug("Retrieved API key from config file")
                    return api_key

            logger.debug("No API key found in either keyring or config file")
            return None

        except Exception as e:
            logger.error(f"Failed to retrieve API key: {e}")
            return None

    def set_llm_api_key(self, api_key: str) -> bool:
        """
        Store LLM API key in secure storage with config file fallback

        Args:
            api_key: The OpenAI API key to store

        Returns:
            True if successfully stored, False otherwise
        """
        try:
            if not api_key or not api_key.strip():
                logger.warning("Attempted to store empty API key")
                return False

            api_key = api_key.strip()

            # Try keyring first (preferred secure storage)
            try:
                import keyring
                keyring.set_password("markitdown_gui", "openai_api_key", api_key)
                logger.info("API key stored in secure keyring storage")

                # Clear from config file if keyring succeeds (security best practice)
                if hasattr(self._config, 'openai_api_key'):
                    self._config.openai_api_key = None

                return True

            except ImportError:
                logger.debug("Keyring not available, storing in config file")
            except Exception as e:
                logger.warning(f"Keyring storage failed: {e}, falling back to config file")

            # Fall back to config file storage
            self._config.openai_api_key = api_key
            logger.info("API key stored in config file (less secure)")
            return True

        except Exception as e:
            logger.error(f"Failed to store API key: {e}")
            return False

    def remove_llm_api_key(self) -> bool:
        """
        Remove LLM API key from all storage locations

        Returns:
            True if successfully removed, False otherwise
        """
        try:
            success = True

            # Remove from keyring
            try:
                import keyring
                keyring.delete_password("markitdown_gui", "openai_api_key")
                logger.debug("API key removed from keyring storage")
            except ImportError:
                pass  # Keyring not available
            except Exception as e:
                logger.debug(f"Keyring removal failed (may not exist): {e}")
                # Not a critical error if key doesn't exist

            # Remove from config file
            if hasattr(self._config, 'openai_api_key'):
                self._config.openai_api_key = None
                logger.debug("API key removed from config file")

            return success

        except Exception as e:
            logger.error(f"Failed to remove API key: {e}")
            return False

    def has_llm_api_key(self) -> bool:
        """
        Check if a valid LLM API key is available

        Returns:
            True if API key is available and non-empty, False otherwise
        """
        api_key = self.get_llm_api_key()
        return api_key is not None and len(api_key.strip()) > 0