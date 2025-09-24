"""
전처리 파이프라인
OCR 향상을 위한 이미지 전처리 워크플로우 조정 시스템
"""

import asyncio
import logging
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Callable

from .image_enhancer import ImageEnhancer, EnhancementParameters, EnhancementResult, EnhancementType
from .quality_analyzer import QualityAnalyzer, OCRReadinessAssessment, EnhancementRecommendation

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """처리 모드"""
    AUTO = "auto"           # 자동 최적화
    CONSERVATIVE = "conservative"  # 보수적 처리
    AGGRESSIVE = "aggressive"      # 공격적 처리
    CUSTOM = "custom"       # 사용자 정의


class CacheStrategy(Enum):
    """캐시 전략"""
    NONE = "none"          # 캐시 없음
    MEMORY = "memory"      # 메모리 캐시
    DISK = "disk"          # 디스크 캐시
    HYBRID = "hybrid"      # 하이브리드 캐시


@dataclass
class PreprocessingConfig:
    """전처리 설정"""
    # 처리 모드
    mode: ProcessingMode = ProcessingMode.AUTO

    # 활성화할 향상 기능들
    enabled_enhancements: List[str] = field(default_factory=lambda: [
        "deskew", "contrast", "brightness", "sharpening", "noise_reduction"
    ])

    # 품질 임계값
    quality_threshold: float = 0.6  # 이 값 이하면 전처리 수행

    # 성능 설정
    max_processing_time: float = 10.0  # 최대 처리 시간 (초)
    enable_parallel_processing: bool = True  # 병렬 처리 활성화
    cache_strategy: CacheStrategy = CacheStrategy.MEMORY

    # 배치 처리 설정
    batch_size: int = 5  # 배치 크기
    enable_batch_optimization: bool = True

    # 디버그 설정
    save_intermediate_results: bool = False  # 중간 결과 저장
    enable_performance_monitoring: bool = True


@dataclass
class PreprocessingResult:
    """전처리 결과"""
    enhanced_image_path: Optional[Path] = None
    original_image_path: Optional[Path] = None
    quality_assessment: Optional[OCRReadinessAssessment] = None
    enhancement_results: List[EnhancementResult] = field(default_factory=list)
    processing_time: float = 0.0
    cache_hit: bool = False
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """성공 여부"""
        return self.enhanced_image_path is not None and self.error_message is None

    @property
    def total_improvement_score(self) -> float:
        """총 향상도 점수"""
        if not self.enhancement_results:
            return 0.0

        scores = [result.improvement_score for result in self.enhancement_results if result.is_success]
        return sum(scores) / len(scores) if scores else 0.0


@dataclass
class BatchProcessingResult:
    """배치 처리 결과"""
    results: List[PreprocessingResult] = field(default_factory=list)
    total_processing_time: float = 0.0
    successful_count: int = 0
    failed_count: int = 0
    cache_hit_rate: float = 0.0
    average_improvement: float = 0.0

    def __post_init__(self):
        if self.results:
            self.successful_count = sum(1 for r in self.results if r.is_success)
            self.failed_count = len(self.results) - self.successful_count

            cache_hits = sum(1 for r in self.results if r.cache_hit)
            self.cache_hit_rate = cache_hits / len(self.results) if self.results else 0.0

            improvements = [r.total_improvement_score for r in self.results if r.is_success]
            self.average_improvement = sum(improvements) / len(improvements) if improvements else 0.0


class PreprocessingPipeline:
    """전처리 파이프라인"""

    def __init__(self, config: Dict):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = PreprocessingConfig(**config) if isinstance(config, dict) else config
        self.enhancer = ImageEnhancer()
        self.quality_analyzer = QualityAnalyzer()

        # 캐시 시스템
        self._cache = {}
        self._cache_stats = {"hits": 0, "misses": 0}

        # 성능 모니터링
        self._performance_stats = {
            "total_processed": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "success_rate": 0.0
        }

        # 임시 디렉토리
        self.temp_dir = Path(tempfile.gettempdir()) / "markitdown_preprocessing"
        self.temp_dir.mkdir(exist_ok=True)

        logger.info(f"Preprocessing pipeline initialized with mode: {self.config.mode}")

    async def auto_enhance_for_ocr(
        self,
        image_path: Path,
        force_processing: bool = False
    ) -> PreprocessingResult:
        """
        OCR을 위한 자동 향상

        Args:
            image_path: 이미지 경로
            force_processing: 강제 처리 여부

        Returns:
            전처리 결과
        """
        start_time = time.time()

        try:
            # 캐시 확인
            cache_key = self._get_cache_key(image_path)
            if not force_processing and cache_key in self._cache:
                cached_result = self._cache[cache_key]
                cached_result.cache_hit = True
                self._cache_stats["hits"] += 1
                logger.debug(f"Cache hit for {image_path.name}")
                return cached_result

            self._cache_stats["misses"] += 1

            # 품질 분석
            logger.debug(f"Analyzing image quality: {image_path.name}")
            quality_assessment = await self.quality_analyzer.assess_ocr_readiness(image_path)

            # 처리 필요성 판단
            if not force_processing and quality_assessment.is_ready and quality_assessment.confidence >= self.config.quality_threshold:
                logger.info(f"Image {image_path.name} already OCR-ready (confidence: {quality_assessment.confidence:.2f})")
                result = PreprocessingResult(
                    enhanced_image_path=image_path,  # 원본 사용
                    original_image_path=image_path,
                    quality_assessment=quality_assessment,
                    processing_time=time.time() - start_time
                )
                self._cache_result(cache_key, result)
                return result

            # 향상 처리 수행
            enhancement_results = await self._apply_recommended_enhancements(
                image_path,
                quality_assessment.recommendations
            )

            # 최종 결과 결정
            if enhancement_results:
                final_image_path = enhancement_results[-1].enhanced_image_path
            else:
                final_image_path = image_path

            processing_time = time.time() - start_time

            result = PreprocessingResult(
                enhanced_image_path=final_image_path,
                original_image_path=image_path,
                quality_assessment=quality_assessment,
                enhancement_results=enhancement_results,
                processing_time=processing_time,
                metadata={
                    "mode": self.config.mode.value if hasattr(self.config.mode, 'value') else self.config.mode,
                    "enhancements_count": len(enhancement_results),
                    "recommendations_count": len(quality_assessment.recommendations)
                }
            )

            # 캐시 저장
            self._cache_result(cache_key, result)

            # 성능 통계 업데이트
            self._update_performance_stats(result)

            logger.info(f"Auto enhancement completed for {image_path.name} in {processing_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Auto enhancement failed for {image_path.name}: {e}")
            return PreprocessingResult(
                original_image_path=image_path,
                error_message=f"Auto enhancement failed: {str(e)}",
                processing_time=time.time() - start_time
            )

    async def apply_custom_enhancements(
        self,
        image_path: Path,
        enhancement_parameters: EnhancementParameters
    ) -> PreprocessingResult:
        """
        사용자 정의 향상 적용

        Args:
            image_path: 이미지 경로
            enhancement_parameters: 향상 매개변수

        Returns:
            전처리 결과
        """
        start_time = time.time()

        try:
            logger.debug(f"Applying custom enhancements to {image_path.name}")

            # 사용자 정의 향상 적용
            enhancement_result = await self.enhancer.apply_multiple_enhancements(
                image_path, enhancement_parameters
            )

            # 결과 후 품질 분석
            final_quality = None
            if enhancement_result.is_success:
                final_quality = await self.quality_analyzer.assess_ocr_readiness(
                    enhancement_result.enhanced_image_path
                )

            processing_time = time.time() - start_time

            result = PreprocessingResult(
                enhanced_image_path=enhancement_result.enhanced_image_path,
                original_image_path=image_path,
                quality_assessment=final_quality,
                enhancement_results=[enhancement_result] if enhancement_result.is_success else [],
                processing_time=processing_time,
                metadata={
                    "mode": "custom",
                    "parameters": enhancement_parameters.__dict__
                }
            )

            self._update_performance_stats(result)

            logger.info(f"Custom enhancement completed for {image_path.name} in {processing_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Custom enhancement failed for {image_path.name}: {e}")
            return PreprocessingResult(
                original_image_path=image_path,
                error_message=f"Custom enhancement failed: {str(e)}",
                processing_time=time.time() - start_time
            )

    async def process_image_batch(
        self,
        image_paths: List[Path],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> BatchProcessingResult:
        """
        이미지 배치 처리

        Args:
            image_paths: 이미지 경로 리스트
            progress_callback: 진행 상황 콜백

        Returns:
            배치 처리 결과
        """
        start_time = time.time()
        results = []

        try:
            logger.info(f"Starting batch processing of {len(image_paths)} images")

            if self.config.enable_parallel_processing and len(image_paths) > 1:
                # 병렬 처리
                results = await self._process_batch_parallel(image_paths, progress_callback)
            else:
                # 순차 처리
                results = await self._process_batch_sequential(image_paths, progress_callback)

            total_time = time.time() - start_time

            batch_result = BatchProcessingResult(
                results=results,
                total_processing_time=total_time
            )

            logger.info(f"Batch processing completed: {batch_result.successful_count}/{len(image_paths)} successful")
            return batch_result

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return BatchProcessingResult(
                results=results,
                total_processing_time=time.time() - start_time
            )

    async def _process_batch_parallel(
        self,
        image_paths: List[Path],
        progress_callback: Optional[Callable[[int, int], None]]
    ) -> List[PreprocessingResult]:
        """병렬 배치 처리"""
        results = []
        batch_size = min(self.config.batch_size, len(image_paths))

        for i in range(0, len(image_paths), batch_size):
            batch = image_paths[i:i + batch_size]

            # 현재 배치를 병렬로 처리
            tasks = [self.auto_enhance_for_ocr(path) for path in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # 예외 처리
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error for {batch[j].name}: {result}")
                    results.append(PreprocessingResult(
                        original_image_path=batch[j],
                        error_message=str(result)
                    ))
                else:
                    results.append(result)

            # 진행 상황 업데이트
            if progress_callback:
                progress_callback(min(i + batch_size, len(image_paths)), len(image_paths))

        return results

    async def _process_batch_sequential(
        self,
        image_paths: List[Path],
        progress_callback: Optional[Callable[[int, int], None]]
    ) -> List[PreprocessingResult]:
        """순차 배치 처리"""
        results = []

        for i, image_path in enumerate(image_paths):
            try:
                result = await self.auto_enhance_for_ocr(image_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Sequential processing error for {image_path.name}: {e}")
                results.append(PreprocessingResult(
                    original_image_path=image_path,
                    error_message=str(e)
                ))

            # 진행 상황 업데이트
            if progress_callback:
                progress_callback(i + 1, len(image_paths))

        return results

    async def _apply_recommended_enhancements(
        self,
        image_path: Path,
        recommendations: List[EnhancementRecommendation]
    ) -> List[EnhancementResult]:
        """추천 향상 기법 적용"""
        enhancement_results = []
        current_path = image_path

        # 우선순위 순으로 정렬된 추천사항 처리
        for recommendation in recommendations:
            if recommendation.enhancement_type not in self.config.enabled_enhancements:
                logger.debug(f"Skipping disabled enhancement: {recommendation.enhancement_type}")
                continue

            try:
                # 향상 기법 적용
                result = await self._apply_single_enhancement(
                    current_path,
                    recommendation
                )

                if result.is_success:
                    enhancement_results.append(result)
                    current_path = result.enhanced_image_path
                    logger.debug(f"Applied {recommendation.enhancement_type} enhancement")
                else:
                    logger.warning(f"Enhancement {recommendation.enhancement_type} failed: {result.error_message}")

            except Exception as e:
                logger.error(f"Enhancement {recommendation.enhancement_type} error: {e}")

        return enhancement_results

    async def _apply_single_enhancement(
        self,
        image_path: Path,
        recommendation: EnhancementRecommendation
    ) -> EnhancementResult:
        """단일 향상 기법 적용"""
        enhancement_type = recommendation.enhancement_type
        parameters = recommendation.parameters

        if enhancement_type == "contrast":
            return await self.enhancer.enhance_contrast(
                image_path,
                factor=parameters.get("factor", 1.2),
                adaptive=parameters.get("adaptive", True)
            )
        elif enhancement_type == "brightness":
            return await self.enhancer.correct_brightness(
                image_path,
                auto_adjust=parameters.get("auto_adjust", True)
            )
        elif enhancement_type == "sharpening":
            return await self.enhancer.sharpen_image(
                image_path,
                strength=parameters.get("strength", 1.0)
            )
        elif enhancement_type == "noise_reduction":
            return await self.enhancer.remove_noise(
                image_path,
                strength=parameters.get("strength", 1)
            )
        elif enhancement_type == "deskew":
            return await self.enhancer.deskew_image(
                image_path,
                max_angle=parameters.get("max_angle", 45.0)
            )
        else:
            # 알 수 없는 향상 유형
            return EnhancementResult(
                original_image_path=image_path,
                error_message=f"Unknown enhancement type: {enhancement_type}"
            )

    def track_enhancement_effectiveness(self) -> Dict:
        """향상 효과 추적"""
        return {
            "performance_stats": self._performance_stats.copy(),
            "cache_stats": self._cache_stats.copy(),
            "cache_size": len(self._cache),
            "config": {
                "mode": self.config.mode.value if hasattr(self.config.mode, 'value') else self.config.mode,
                "enabled_enhancements": self.config.enabled_enhancements,
                "quality_threshold": self.config.quality_threshold
            }
        }

    def _get_cache_key(self, image_path: Path) -> str:
        """캐시 키 생성"""
        # 파일 경로, 크기, 수정 시간을 기반으로 키 생성
        try:
            stat = image_path.stat()
            return f"{image_path.name}_{stat.st_size}_{int(stat.st_mtime)}_{self.config.mode.value if hasattr(self.config.mode, 'value') else self.config.mode}"
        except Exception:
            return f"{image_path.name}_{self.config.mode.value if hasattr(self.config.mode, 'value') else self.config.mode}"

    def _cache_result(self, cache_key: str, result: PreprocessingResult):
        """결과 캐시"""
        cache_strategy = self.config.cache_strategy
        if hasattr(cache_strategy, 'value'):
            cache_strategy = cache_strategy.value

        if cache_strategy in ['memory', 'hybrid']:
            # 메모리 캐시 크기 제한 (최대 100개)
            if len(self._cache) >= 100:
                # 가장 오래된 항목 제거
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

            self._cache[cache_key] = result

    def _update_performance_stats(self, result: PreprocessingResult):
        """성능 통계 업데이트"""
        self._performance_stats["total_processed"] += 1
        self._performance_stats["total_time"] += result.processing_time

        total = self._performance_stats["total_processed"]
        successful = sum(1 for _ in range(total) if result.is_success)

        self._performance_stats["average_time"] = self._performance_stats["total_time"] / total
        self._performance_stats["success_rate"] = successful / total

    def cleanup(self):
        """리소스 정리"""
        try:
            # 임시 파일 정리
            for temp_file in self.temp_dir.glob("*.png"):
                try:
                    temp_file.unlink()
                except Exception:
                    pass

            # 캐시 정리
            self._cache.clear()

            # 향상기 정리
            if hasattr(self.enhancer, 'cleanup'):
                self.enhancer.cleanup()

            logger.debug("Preprocessing pipeline cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def get_statistics(self) -> Dict:
        """통계 정보 반환"""
        return {
            "performance": self._performance_stats.copy(),
            "cache": {
                "hits": self._cache_stats["hits"],
                "misses": self._cache_stats["misses"],
                "hit_rate": (
                    self._cache_stats["hits"] /
                    (self._cache_stats["hits"] + self._cache_stats["misses"])
                    if (self._cache_stats["hits"] + self._cache_stats["misses"]) > 0 else 0.0
                ),
                "size": len(self._cache)
            },
            "config": {
                "mode": self.config.mode.value if hasattr(self.config.mode, 'value') else self.config.mode,
                "enabled_enhancements": self.config.enabled_enhancements,
                "quality_threshold": self.config.quality_threshold,
                "cache_strategy": self.config.cache_strategy.value if hasattr(self.config.cache_strategy, 'value') else self.config.cache_strategy
            }
        }