"""
LLM 통합 관리자
LLM API 통신, 키 관리, 사용량 추적을 담당
"""

import asyncio
import json
import keyring
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import asdict
import logging

from .models import (
    LLMProvider, LLMConfig, LLMResponse, LLMStats, 
    TokenUsage, TokenUsageType, OCRRequest, OCRResult
)
from .api_client import APIClientFactory, APIClient
from .logger import get_logger
from .memory_optimizer import MemoryOptimizer


logger = get_logger(__name__)


class SecureKeyManager:
    """안전한 키 관리자"""
    
    SERVICE_NAME = "MarkItDownGUI"
    
    @classmethod
    def save_api_key(cls, provider: str, api_key: str) -> bool:
        """
        API 키 저장 (keyring 사용)
        
        Args:
            provider: 공급업체 명
            api_key: API 키
        
        Returns:
            저장 성공 여부
        """
        try:
            keyring.set_password(cls.SERVICE_NAME, f"{provider}_api_key", api_key)
            logger.info(f"API key saved for provider: {provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to save API key for {provider}: {e}")
            return False
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """
        API 키 조회
        
        Args:
            provider: 공급업체 명
        
        Returns:
            API 키 (없으면 None)
        """
        try:
            api_key = keyring.get_password(cls.SERVICE_NAME, f"{provider}_api_key")
            if api_key:
                logger.debug(f"API key retrieved for provider: {provider}")
            return api_key
        except Exception as e:
            logger.error(f"Failed to retrieve API key for {provider}: {e}")
            return None
    
    @classmethod
    def delete_api_key(cls, provider: str) -> bool:
        """
        API 키 삭제
        
        Args:
            provider: 공급업체 명
        
        Returns:
            삭제 성공 여부
        """
        try:
            keyring.delete_password(cls.SERVICE_NAME, f"{provider}_api_key")
            logger.info(f"API key deleted for provider: {provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete API key for {provider}: {e}")
            return False
    
    @classmethod
    def list_stored_providers(cls) -> List[str]:
        """저장된 공급업체 목록 반환"""
        try:
            # keyring에서 직접 목록을 가져오는 것은 제한적이므로
            # 알려진 공급업체들을 확인
            providers = []
            for provider in ["openai", "azure_openai", "anthropic", "google"]:
                if cls.get_api_key(provider):
                    providers.append(provider)
            return providers
        except Exception as e:
            logger.error(f"Failed to list stored providers: {e}")
            return []


class TokenUsageTracker:
    """토큰 사용량 추적기"""
    
    def __init__(self, storage_path: Path):
        """
        초기화
        
        Args:
            storage_path: 사용량 저장 파일 경로
        """
        self.storage_path = storage_path
        self.usage_history: List[Dict[str, Any]] = []
        self.monthly_usage: Dict[str, int] = {}  # YYYY-MM -> token_count
        self._load_usage_history()
    
    def _load_usage_history(self):
        """사용량 히스토리 로드"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.usage_history = data.get('usage_history', [])
                    self.monthly_usage = data.get('monthly_usage', {})
                logger.info(f"Token usage history loaded: {len(self.usage_history)} entries")
            except Exception as e:
                logger.error(f"Failed to load usage history: {e}")
                self.usage_history = []
                self.monthly_usage = {}
    
    def _save_usage_history(self):
        """사용량 히스토리 저장"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'usage_history': self.usage_history,
                'monthly_usage': self.monthly_usage,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.debug("Token usage history saved")
        except Exception as e:
            logger.error(f"Failed to save usage history: {e}")
    
    def record_usage(self, response: LLMResponse):
        """
        사용량 기록
        
        Args:
            response: LLM 응답
        """
        usage_record = {
            'timestamp': response.usage.timestamp.isoformat(),
            'provider': response.provider.value,
            'model': response.model,
            'usage_type': response.usage.usage_type.value,
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens,
            'cost_estimate': response.usage.cost_estimate,
            'success': response.success
        }
        
        self.usage_history.append(usage_record)
        
        # 월별 사용량 업데이트
        month_key = response.usage.timestamp.strftime('%Y-%m')
        self.monthly_usage[month_key] = (
            self.monthly_usage.get(month_key, 0) + response.usage.total_tokens
        )
        
        # 히스토리가 너무 길면 정리 (최근 10,000개만 유지)
        if len(self.usage_history) > 10000:
            self.usage_history = self.usage_history[-10000:]
        
        self._save_usage_history()
        logger.debug(f"Token usage recorded: {response.usage.total_tokens} tokens")
    
    def get_monthly_usage(self, year: int, month: int) -> int:
        """
        월별 토큰 사용량 조회
        
        Args:
            year: 년도
            month: 월
        
        Returns:
            토큰 사용량
        """
        month_key = f"{year:04d}-{month:02d}"
        return self.monthly_usage.get(month_key, 0)
    
    def get_current_month_usage(self) -> int:
        """현재 월 토큰 사용량"""
        now = datetime.now()
        return self.get_monthly_usage(now.year, now.month)
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        사용량 통계 조회
        
        Args:
            days: 조회 기간 (일)
        
        Returns:
            사용량 통계
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_usage = [
            record for record in self.usage_history
            if datetime.fromisoformat(record['timestamp']) > cutoff_date
        ]
        
        if not recent_usage:
            return {
                'total_requests': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'success_rate': 0.0,
                'avg_tokens_per_request': 0.0
            }
        
        total_requests = len(recent_usage)
        successful_requests = sum(1 for r in recent_usage if r['success'])
        total_tokens = sum(r['total_tokens'] for r in recent_usage)
        total_cost = sum(r['cost_estimate'] for r in recent_usage)
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'success_rate': (successful_requests / total_requests) * 100,
            'avg_tokens_per_request': total_tokens / total_requests if total_requests > 0 else 0.0
        }


class LLMManager:
    """LLM 통합 관리자"""
    
    def __init__(self, config_dir: Path = None):
        """
        초기화
        
        Args:
            config_dir: 설정 디렉토리
        """
        if config_dir is None:
            config_dir = Path("config")
        
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        
        # 구성 요소 초기화
        self.key_manager = SecureKeyManager()
        self.usage_tracker = TokenUsageTracker(
            config_dir / "token_usage.json"
        )
        self._memory_optimizer = MemoryOptimizer()
        
        self.current_config: Optional[LLMConfig] = None
        self.stats = LLMStats()
        
        logger.info("LLM Manager initialized")
    
    def configure(self, config: LLMConfig) -> bool:
        """
        LLM 설정
        
        Args:
            config: LLM 설정
        
        Returns:
            설정 성공 여부
        """
        try:
            # API 키를 keyring에서 가져오기
            if not config.api_key:
                config.api_key = self.key_manager.get_api_key(config.provider.value)
            
            if not config.api_key:
                raise ValueError(f"No API key found for provider: {config.provider.value}")
            
            self.current_config = config
            logger.info(f"LLM configured: {config.provider.value} - {config.model}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure LLM: {e}")
            return False
    
    def save_api_key(self, provider: str, api_key: str) -> bool:
        """
        API 키 저장
        
        Args:
            provider: 공급업체
            api_key: API 키
        
        Returns:
            저장 성공 여부
        """
        return self.key_manager.save_api_key(provider, api_key)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        API 키 조회
        
        Args:
            provider: 공급업체
        
        Returns:
            API 키
        """
        return self.key_manager.get_api_key(provider)
    
    def delete_api_key(self, provider: str) -> bool:
        """
        API 키 삭제
        
        Args:
            provider: 공급업체
        
        Returns:
            삭제 성공 여부
        """
        return self.key_manager.delete_api_key(provider)
    
    async def test_connection(self, config: LLMConfig) -> Dict[str, Any]:
        """
        연결 테스트
        
        Args:
            config: 테스트할 설정
        
        Returns:
            테스트 결과
        """
        try:
            # 임시로 API 키 설정
            test_config = config
            if not test_config.api_key:
                test_config.api_key = self.key_manager.get_api_key(config.provider.value)
            
            if not test_config.api_key:
                return {
                    'success': False,
                    'error': f"No API key found for {config.provider.value}"
                }
            
            # 테스트 요청
            async with APIClientFactory.create_client(test_config) as client:
                response = await client.text_completion(
                    prompt="Hello! This is a connection test.",
                    usage_type=TokenUsageType.TEXT_GENERATION
                )
                
                if response.is_success:
                    return {
                        'success': True,
                        'model': response.model,
                        'provider': response.provider.value,
                        'response_time': response.response_time,
                        'tokens_used': response.usage.total_tokens
                    }
                else:
                    return {
                        'success': False,
                        'error': response.error_message
                    }
                    
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        usage_type: TokenUsageType = TokenUsageType.TEXT_GENERATION
    ) -> LLMResponse:
        """
        텍스트 생성
        
        Args:
            prompt: 프롬프트
            system_prompt: 시스템 프롬프트
            usage_type: 사용 유형
        
        Returns:
            LLM 응답
        """
        if not self.current_config:
            raise ValueError("LLM not configured")
        
        # 메모리 체크
        if self._memory_optimizer.should_trigger_gc():
            self._memory_optimizer.force_gc()
        
        # 응답 캐싱 확인
        cache_key = f"llm_{hash(prompt)}_{system_prompt or ''}_{usage_type.value}"
        cached_response = self._memory_optimizer.get_cached_result(cache_key)
        
        if cached_response:
            logger.debug(f"LLM response from cache")
            return cached_response
        
        async with APIClientFactory.create_client(self.current_config) as client:
            response = await client.text_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                usage_type=usage_type
            )
            
            # 응답 캐싱 (성공한 경우만)
            if response.is_success and len(response.content) < 100 * 1024:  # 100KB 미만
                self._memory_optimizer.cache_result(cache_key, response)
            
            # 통계 및 사용량 추적
            self.stats.add_request(response)
            self.usage_tracker.record_usage(response)
            
            return response
    
    async def ocr_image(self, request: OCRRequest) -> OCRResult:
        """
        이미지 OCR 처리
        
        Args:
            request: OCR 요청
        
        Returns:
            OCR 결과
        """
        if not self.current_config:
            raise ValueError("LLM not configured")
        
        if not self.current_config.enable_ocr:
            return OCRResult(
                text="",
                error_message="LLM OCR is not enabled"
            )
        
        if not request.image_exists:
            return OCRResult(
                text="",
                error_message=f"Image file not found: {request.image_path}"
            )
        
        # OCR 사용을 위한 메모리 체크
        if self._memory_optimizer.should_trigger_gc():
            self._memory_optimizer.force_gc()
        
        # OCR 결과 캐싱 확인
        image_stat = request.image_path.stat()
        cache_key = f"ocr_{request.image_path}_{image_stat.st_mtime}_{request.language}_{hash(request.prompt or '')}"
        cached_result = self._memory_optimizer.get_cached_result(cache_key)
        
        if cached_result:
            logger.debug(f"OCR result from cache: {request.image_path}")
            return cached_result
        
        try:
            # OCR 프롬프트 생성
            language_instruction = ""
            if request.language != "auto":
                language_instruction = f" The text is primarily in {request.language}."
            
            ocr_prompt = (
                f"Please extract all text from this image and return it in markdown format. "
                f"Maintain the original structure and formatting as much as possible.{language_instruction} "
                f"If there are tables, format them as markdown tables. "
                f"If there are no readable text elements, respond with 'No text found'."
            )
            
            if request.prompt:
                ocr_prompt = request.prompt
            
            # 이미지 크기 조정 (필요시)
            image_path = request.image_path
            if self._get_image_size(image_path) > request.max_size:
                image_path = self._resize_image(image_path, request.max_size)
            
            async with APIClientFactory.create_client(self.current_config) as client:
                response = await client.vision_completion(
                    text_prompt=ocr_prompt,
                    images=[image_path]
                )
                
                # 통계 및 사용량 추적
                self.stats.add_request(response)
                self.usage_tracker.record_usage(response)
                
                if response.is_success:
                    # 언어 감지 (간단한 휴리스틱)
                    detected_language = self._detect_language(response.content)
                    
                    ocr_result = OCRResult(
                        text=response.content,
                        confidence=0.95 if response.content != "No text found" else 0.0,
                        language_detected=detected_language,
                        processing_time=response.response_time,
                        token_usage=response.usage
                    )
                    
                    # OCR 결과 캐싱 (성공한 경우만)
                    if len(response.content) < 50 * 1024:  # 50KB 미만
                        self._memory_optimizer.cache_result(cache_key, ocr_result)
                    
                    return ocr_result
                else:
                    return OCRResult(
                        text="",
                        error_message=response.error_message,
                        processing_time=response.response_time,
                        token_usage=response.usage
                    )
                    
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return OCRResult(
                text="",
                error_message=str(e)
            )
    
    def _get_image_size(self, image_path: Path) -> int:
        """이미지 크기 조회 (가장 긴 변의 픽셀 수)"""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                return max(img.width, img.height)
        except ImportError:
            logger.warning("PIL not available, assuming image size is within limits")
            return 800  # 기본값
        except Exception as e:
            logger.error(f"Failed to get image size: {e}")
            return 800  # 기본값
    
    def _resize_image(self, image_path: Path, max_size: int) -> Path:
        """이미지 크기 조정"""
        try:
            from PIL import Image
            
            with Image.open(image_path) as img:
                # 비율 유지하며 리사이징
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # 임시 파일로 저장
                temp_path = image_path.parent / f"temp_resized_{image_path.name}"
                img.save(temp_path, optimize=True, quality=85)
                
                logger.debug(f"Image resized: {image_path} -> {temp_path}")
                return temp_path
                
        except ImportError:
            logger.warning("PIL not available, using original image")
            return image_path
        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            return image_path
    
    def _detect_language(self, text: str) -> Optional[str]:
        """간단한 언어 감지"""
        if not text or text == "No text found":
            return None
        
        # 한글 감지
        korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7a3')
        if korean_chars > len(text) * 0.1:
            return "ko"
        
        # 중국어 감지
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_chars > len(text) * 0.1:
            return "zh"
        
        # 일본어 감지
        japanese_chars = sum(1 for c in text if '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff')
        if japanese_chars > len(text) * 0.05:
            return "ja"
        
        # 기본적으로 영어로 가정
        return "en"
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        사용량 통계 조회
        
        Args:
            days: 조회 기간
        
        Returns:
            사용량 통계
        """
        usage_stats = self.usage_tracker.get_usage_stats(days)
        usage_stats.update({
            'current_session_stats': asdict(self.stats),
            'current_month_tokens': self.usage_tracker.get_current_month_usage(),
            'memory_stats': self._memory_optimizer.get_memory_statistics()
        })
        return usage_stats
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 사용 통계 반환"""
        return self._memory_optimizer.get_memory_statistics()
    
    def cleanup_memory(self):
        """메모리 정리"""
        self._memory_optimizer.cleanup()
        logger.info("LLMManager 메모리 정리 완료")
    
    def check_usage_limit(self, monthly_limit: int) -> Dict[str, Any]:
        """
        사용량 한도 확인
        
        Args:
            monthly_limit: 월별 토큰 한도
        
        Returns:
            한도 확인 결과
        """
        current_usage = self.usage_tracker.get_current_month_usage()
        usage_percentage = (current_usage / monthly_limit) * 100 if monthly_limit > 0 else 0
        
        return {
            'current_usage': current_usage,
            'monthly_limit': monthly_limit,
            'usage_percentage': usage_percentage,
            'limit_exceeded': current_usage >= monthly_limit,
            'remaining_tokens': max(0, monthly_limit - current_usage)
        }
    
    def reset_stats(self):
        """세션 통계 리셋"""
        self.stats = LLMStats()
        logger.info("LLM statistics reset")
    
    def get_stored_providers(self) -> List[str]:
        """저장된 API 키가 있는 공급업체 목록"""
        return self.key_manager.list_stored_providers()
    
    def __del__(self):
        """소멸자 - 메모리 정리"""
        try:
            if hasattr(self, '_memory_optimizer'):
                self._memory_optimizer.cleanup()
        except:
            pass  # 소멸 시 오류 무시