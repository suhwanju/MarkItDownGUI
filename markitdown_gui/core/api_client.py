"""
API 클라이언트 래퍼
LLM API 통신을 위한 클라이언트 구현
"""

import asyncio
import time
import json
import base64
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import asdict
import aiohttp
import logging
from datetime import datetime, timedelta
from collections import deque

from .models import (
    LLMProvider, LLMConfig, LLMResponse, TokenUsage, 
    TokenUsageType, OCRRequest, OCRResult
)
from .logger import get_logger


logger = get_logger(__name__)


class RateLimiter:
    """API 속도 제한기"""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        초기화
        
        Args:
            max_requests: 시간 창 내 최대 요청 수
            time_window: 시간 창 (초)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """요청 허가 대기"""
        async with self._lock:
            now = time.time()
            
            # 오래된 요청 기록 제거
            while self.requests and self.requests[0] <= now - self.time_window:
                self.requests.popleft()
            
            # 요청 수 확인
            if len(self.requests) >= self.max_requests:
                # 대기 시간 계산
                oldest_request = self.requests[0]
                wait_time = self.time_window - (now - oldest_request)
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()
            
            # 요청 기록 추가
            self.requests.append(now)


class APIClient:
    """API 클라이언트 기본 클래스"""
    
    def __init__(self, config: LLMConfig):
        """
        초기화
        
        Args:
            config: LLM 설정
        """
        self.config = config
        self.rate_limiter = RateLimiter()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 재시도 설정
        self.max_retries = config.max_retries
        self.retry_delay = 1.0  # 초기 재시도 지연 (초)
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        HTTP 요청 실행
        
        Args:
            method: HTTP 메서드
            url: 요청 URL
            headers: 헤더
            data: 폼 데이터
            json_data: JSON 데이터
        
        Returns:
            응답 데이터
        
        Raises:
            Exception: 요청 실패시
        """
        if self.session is None:
            raise RuntimeError("API client session not initialized")
        
        await self.rate_limiter.acquire()
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    json=json_data
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 429:  # Rate limit
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        
                        if attempt < self.max_retries and response.status >= 500:
                            # 서버 오류시 재시도
                            delay = self.retry_delay * (2 ** attempt)  # 지수 백오프
                            logger.info(f"Retrying in {delay} seconds (attempt {attempt + 1})")
                            await asyncio.sleep(delay)
                            continue
                        
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                    
                    result = await response.json()
                    result['_response_time'] = response_time
                    return result
                    
            except asyncio.TimeoutError:
                logger.error(f"Request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                raise Exception("Request timeout after retries")
            
            except aiohttp.ClientError as e:
                logger.error(f"Client error: {e} (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                raise Exception(f"Client error: {e}")
        
        raise Exception("Max retries exceeded")


class OpenAIClient(APIClient):
    """OpenAI API 클라이언트"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        
        if config.provider == LLMProvider.AZURE_OPENAI:
            if not config.base_url or not config.api_version:
                raise ValueError("Azure OpenAI requires base_url and api_version")
            self.base_url = config.base_url.rstrip('/')
            self.api_version = config.api_version
        else:
            self.base_url = "https://api.openai.com/v1"
            self.api_version = None
    
    def _get_headers(self) -> Dict[str, str]:
        """요청 헤더 생성"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.config.provider == LLMProvider.AZURE_OPENAI:
            headers["api-key"] = self.config.api_key
        else:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        return headers
    
    def _get_url(self, endpoint: str) -> str:
        """API URL 생성"""
        if self.config.provider == LLMProvider.AZURE_OPENAI:
            return f"{self.base_url}/openai/deployments/{self.config.model}/{endpoint}?api-version={self.api_version}"
        else:
            return f"{self.base_url}/{endpoint}"
    
    async def text_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        usage_type: TokenUsageType = TokenUsageType.TEXT_GENERATION
    ) -> LLMResponse:
        """
        텍스트 완성 요청
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            usage_type: 토큰 사용 유형
        
        Returns:
            LLM 응답
        """
        try:
            messages = []
            
            if system_prompt or self.config.system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt or self.config.system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            url = self._get_url("chat/completions")
            headers = self._get_headers()
            
            start_time = time.time()
            response_data = await self._make_request("POST", url, headers, json_data=payload)
            response_time = time.time() - start_time
            
            # 응답 파싱
            choice = response_data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            
            # 토큰 사용량 파싱
            usage_data = response_data.get("usage", {})
            token_usage = TokenUsage(
                usage_type=usage_type,
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )
            
            return LLMResponse(
                content=content,
                usage=token_usage,
                model=self.config.model,
                provider=self.config.provider,
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Text completion failed: {e}")
            
            # 빈 토큰 사용량으로 오류 응답 생성
            empty_usage = TokenUsage(usage_type=usage_type)
            
            return LLMResponse(
                content="",
                usage=empty_usage,
                model=self.config.model,
                provider=self.config.provider,
                success=False,
                error_message=str(e),
                response_time=0.0
            )
    
    async def vision_completion(
        self,
        text_prompt: str,
        images: List[Union[Path, str, bytes]],
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        비전 완성 요청 (이미지 OCR)
        
        Args:
            text_prompt: 텍스트 프롬프트
            images: 이미지 파일 경로 또는 데이터 리스트
            system_prompt: 시스템 프롬프트
        
        Returns:
            LLM 응답
        """
        try:
            messages = []
            
            if system_prompt or self.config.system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt or self.config.system_prompt
                })
            
            # 메시지 내용 구성
            content = [{"type": "text", "text": text_prompt}]
            
            # 이미지 처리
            for image in images:
                if isinstance(image, (str, Path)):
                    # 파일 경로
                    image_path = Path(image)
                    if not image_path.exists():
                        raise FileNotFoundError(f"Image not found: {image_path}")
                    
                    image_data = image_path.read_bytes()
                    
                elif isinstance(image, bytes):
                    # 바이트 데이터
                    image_data = image
                else:
                    raise ValueError(f"Unsupported image type: {type(image)}")
                
                # Base64 인코딩
                encoded_image = base64.b64encode(image_data).decode()
                
                # MIME 타입 결정
                if isinstance(image, (str, Path)):
                    suffix = Path(image).suffix.lower()
                    mime_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg', 
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp'
                    }.get(suffix, 'image/jpeg')
                else:
                    mime_type = 'image/jpeg'
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded_image}"
                    }
                })
            
            messages.append({
                "role": "user", 
                "content": content
            })
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            url = self._get_url("chat/completions")
            headers = self._get_headers()
            
            start_time = time.time()
            response_data = await self._make_request("POST", url, headers, json_data=payload)
            response_time = time.time() - start_time
            
            # 응답 파싱
            choice = response_data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            
            # 토큰 사용량 파싱
            usage_data = response_data.get("usage", {})
            token_usage = TokenUsage(
                usage_type=TokenUsageType.OCR,
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )
            
            return LLMResponse(
                content=content,
                usage=token_usage,
                model=self.config.model,
                provider=self.config.provider,
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Vision completion failed: {e}")
            
            # 빈 토큰 사용량으로 오류 응답 생성
            empty_usage = TokenUsage(usage_type=TokenUsageType.OCR)
            
            return LLMResponse(
                content="",
                usage=empty_usage,
                model=self.config.model,
                provider=self.config.provider,
                success=False,
                error_message=str(e),
                response_time=0.0
            )


class APIClientFactory:
    """API 클라이언트 팩토리"""
    
    @staticmethod
    def create_client(config: LLMConfig) -> APIClient:
        """
        설정에 따른 API 클라이언트 생성
        
        Args:
            config: LLM 설정
        
        Returns:
            API 클라이언트
        
        Raises:
            ValueError: 지원하지 않는 공급업체
        """
        if config.provider in [LLMProvider.OPENAI, LLMProvider.AZURE_OPENAI]:
            return OpenAIClient(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")


# 사용량 추적을 위한 전역 통계
_global_usage_stats: Dict[str, int] = {
    "total_requests": 0,
    "total_tokens": 0,
    "total_cost": 0.0
}


def get_global_usage_stats() -> Dict[str, Any]:
    """전역 사용량 통계 반환"""
    return _global_usage_stats.copy()


def update_global_usage_stats(response: LLMResponse):
    """전역 사용량 통계 업데이트"""
    global _global_usage_stats
    _global_usage_stats["total_requests"] += 1
    _global_usage_stats["total_tokens"] += response.usage.total_tokens
    _global_usage_stats["total_cost"] += response.usage.cost_estimate