"""
이미지 품질 분석기
OCR 적합성 평가 및 전처리 추천 시스템
"""

import asyncio
import logging
import math
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageStat

logger = logging.getLogger(__name__)


class ImageQuality(Enum):
    """이미지 품질 등급"""
    EXCELLENT = "excellent"  # 0.8-1.0
    GOOD = "good"           # 0.6-0.8
    FAIR = "fair"           # 0.4-0.6
    POOR = "poor"           # 0.2-0.4
    VERY_POOR = "very_poor" # 0.0-0.2


@dataclass
class QualityMetrics:
    """품질 측정 지표"""
    # 전체 품질 점수 (0.0-1.0)
    overall_score: float = 0.0

    # 개별 지표 점수들 (0.0-1.0)
    contrast_score: float = 0.0
    brightness_score: float = 0.0
    sharpness_score: float = 0.0
    noise_score: float = 0.0
    resolution_score: float = 0.0
    text_density_score: float = 0.0
    skew_score: float = 0.0

    # 메타데이터
    image_size: Tuple[int, int] = (0, 0)
    file_size_mb: float = 0.0
    color_mode: str = ""
    dpi: Optional[Tuple[int, int]] = None

    # 품질 등급
    quality_grade: ImageQuality = ImageQuality.POOR

    def __post_init__(self):
        # 전체 점수 계산
        self.overall_score = self._calculate_overall_score()
        # 품질 등급 결정
        self.quality_grade = self._determine_quality_grade()

    def _calculate_overall_score(self) -> float:
        """전체 품질 점수 계산 (가중평균)"""
        weights = {
            'contrast': 0.20,
            'brightness': 0.15,
            'sharpness': 0.25,
            'noise': 0.15,
            'resolution': 0.10,
            'text_density': 0.10,
            'skew': 0.05
        }

        score = (
            self.contrast_score * weights['contrast'] +
            self.brightness_score * weights['brightness'] +
            self.sharpness_score * weights['sharpness'] +
            self.noise_score * weights['noise'] +
            self.resolution_score * weights['resolution'] +
            self.text_density_score * weights['text_density'] +
            self.skew_score * weights['skew']
        )

        return max(0.0, min(1.0, score))

    def _determine_quality_grade(self) -> ImageQuality:
        """품질 등급 결정"""
        if self.overall_score >= 0.8:
            return ImageQuality.EXCELLENT
        elif self.overall_score >= 0.6:
            return ImageQuality.GOOD
        elif self.overall_score >= 0.4:
            return ImageQuality.FAIR
        elif self.overall_score >= 0.2:
            return ImageQuality.POOR
        else:
            return ImageQuality.VERY_POOR


@dataclass
class EnhancementRecommendation:
    """향상 추천"""
    enhancement_type: str
    priority: int  # 1-5 (높을수록 중요)
    reason: str
    expected_improvement: float  # 예상 향상도 (0.0-1.0)
    parameters: Dict


@dataclass
class OCRReadinessAssessment:
    """OCR 준비도 평가"""
    is_ready: bool
    confidence: float  # OCR 성공 예상 확률 (0.0-1.0)
    quality_metrics: QualityMetrics
    recommendations: List[EnhancementRecommendation]
    estimated_processing_time: float  # 예상 처리 시간 (초)
    analysis_time: float  # 분석 시간 (초)


class QualityAnalyzer:
    """이미지 품질 분석기"""

    def __init__(self, config: Optional[Dict] = None):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}

        # OpenCV 가용성 확인
        self._opencv_available = self._check_opencv()
        if self._opencv_available:
            import cv2
            self.cv2 = cv2
            logger.info("OpenCV available for advanced quality analysis")
        else:
            logger.info("Using PIL-only quality analysis")

        # 품질 임계값 설정
        self.thresholds = {
            'min_contrast': self.config.get('min_contrast', 0.3),
            'min_brightness': self.config.get('min_brightness', 0.4),
            'min_sharpness': self.config.get('min_sharpness', 0.5),
            'max_noise': self.config.get('max_noise', 0.3),
            'min_resolution': self.config.get('min_resolution', 0.6),
            'min_text_density': self.config.get('min_text_density', 0.2),
            'max_skew': self.config.get('max_skew', 5.0)  # 도 단위
        }

    def _check_opencv(self) -> bool:
        """OpenCV 가용성 확인"""
        try:
            import cv2
            return True
        except ImportError:
            return False

    async def assess_ocr_readiness(self, image_path: Path) -> OCRReadinessAssessment:
        """
        OCR 준비도 종합 평가

        Args:
            image_path: 이미지 경로

        Returns:
            OCR 준비도 평가 결과
        """
        start_time = time.time()

        try:
            # 품질 측정
            quality_metrics = await self.analyze_image_quality(image_path)

            # 추천사항 생성
            recommendations = await self.recommend_enhancements(quality_metrics)

            # OCR 성공률 예측
            success_rate = self.predict_ocr_success_rate(quality_metrics)

            # 처리 시간 추정
            processing_time = self._estimate_processing_time(image_path, recommendations)

            analysis_time = time.time() - start_time

            # OCR 준비도 결정
            is_ready = (
                quality_metrics.overall_score >= 0.5 and
                success_rate >= 0.6
            )

            return OCRReadinessAssessment(
                is_ready=is_ready,
                confidence=success_rate,
                quality_metrics=quality_metrics,
                recommendations=recommendations,
                estimated_processing_time=processing_time,
                analysis_time=analysis_time
            )

        except Exception as e:
            logger.error(f"OCR readiness assessment failed: {e}")
            # 기본값 반환
            return OCRReadinessAssessment(
                is_ready=False,
                confidence=0.0,
                quality_metrics=QualityMetrics(),
                recommendations=[],
                estimated_processing_time=0.0,
                analysis_time=time.time() - start_time
            )

    async def analyze_image_quality(self, image_path: Path) -> QualityMetrics:
        """
        이미지 품질 상세 분석

        Args:
            image_path: 이미지 경로

        Returns:
            품질 측정 지표
        """
        try:
            with Image.open(image_path) as image:
                # 기본 정보 수집
                size = image.size
                file_size_mb = image_path.stat().st_size / (1024 * 1024)
                color_mode = image.mode
                dpi = image.info.get('dpi')

                # 개별 품질 지표 측정
                contrast_score = await self._measure_contrast(image)
                brightness_score = await self._measure_brightness(image)
                sharpness_score = await self._measure_sharpness(image)
                noise_score = await self._measure_noise_level(image)
                resolution_score = await self._measure_resolution_quality(image)
                text_density_score = await self._measure_text_density(image)
                skew_score = await self._measure_skew_level(image)

                return QualityMetrics(
                    contrast_score=contrast_score,
                    brightness_score=brightness_score,
                    sharpness_score=sharpness_score,
                    noise_score=noise_score,
                    resolution_score=resolution_score,
                    text_density_score=text_density_score,
                    skew_score=skew_score,
                    image_size=size,
                    file_size_mb=file_size_mb,
                    color_mode=color_mode,
                    dpi=dpi
                )

        except Exception as e:
            logger.error(f"Image quality analysis failed: {e}")
            return QualityMetrics()

    async def _measure_contrast(self, image: Image.Image) -> float:
        """대비 측정"""
        try:
            # 그레이스케일로 변환
            gray = image.convert('L')

            if self._opencv_available:
                # OpenCV를 사용한 고급 대비 측정
                image_array = np.array(gray)

                # 표준편차 기반 대비 측정
                std_dev = np.std(image_array)
                contrast_score = min(std_dev / 128.0, 1.0)  # 정규화

                # 히스토그램 기반 대비 검증
                hist = self.cv2.calcHist([image_array], [0], None, [256], [0, 256])
                hist_spread = np.sum(hist > np.max(hist) * 0.01) / 256.0

                # 두 방법의 평균
                return (contrast_score + hist_spread) / 2.0
            else:
                # PIL을 사용한 기본 대비 측정
                stat = ImageStat.Stat(gray)
                # 표준편차를 대비 지표로 사용
                std_dev = stat.stddev[0]
                return min(std_dev / 64.0, 1.0)  # 정규화

        except Exception as e:
            logger.debug(f"Contrast measurement failed: {e}")
            return 0.5

    async def _measure_brightness(self, image: Image.Image) -> float:
        """밝기 측정"""
        try:
            gray = image.convert('L')
            stat = ImageStat.Stat(gray)
            mean_brightness = stat.mean[0]

            # 최적 밝기(128) 대비 점수 계산
            # 128에 가까울수록 높은 점수
            distance_from_optimal = abs(mean_brightness - 128)
            brightness_score = 1.0 - (distance_from_optimal / 128.0)

            return max(0.0, brightness_score)

        except Exception as e:
            logger.debug(f"Brightness measurement failed: {e}")
            return 0.5

    async def _measure_sharpness(self, image: Image.Image) -> float:
        """선명도 측정"""
        try:
            gray = image.convert('L')

            if self._opencv_available:
                # OpenCV를 사용한 라플라시안 변화도 기반 선명도 측정
                image_array = np.array(gray)
                laplacian_var = self.cv2.Laplacian(image_array, self.cv2.CV_64F).var()

                # 정규화 (일반적인 선명한 이미지의 라플라시안 분산은 100-2000 범위)
                sharpness_score = min(laplacian_var / 1000.0, 1.0)

                return max(0.0, sharpness_score)
            else:
                # PIL을 사용한 기본 선명도 측정
                # 가장자리 검출 필터 적용
                from PIL import ImageFilter
                edges = gray.filter(ImageFilter.FIND_EDGES)
                stat = ImageStat.Stat(edges)
                edge_intensity = stat.mean[0]

                # 정규화
                return min(edge_intensity / 50.0, 1.0)

        except Exception as e:
            logger.debug(f"Sharpness measurement failed: {e}")
            return 0.5

    async def _measure_noise_level(self, image: Image.Image) -> float:
        """노이즈 수준 측정 (높을수록 노이즈가 적음)"""
        try:
            gray = image.convert('L')

            if self._opencv_available:
                # OpenCV를 사용한 노이즈 측정
                image_array = np.array(gray)

                # 가우시안 블러 적용 후 차이 계산
                blurred = self.cv2.GaussianBlur(image_array, (5, 5), 0)
                noise = np.abs(image_array.astype(np.float32) - blurred.astype(np.float32))
                noise_level = np.mean(noise)

                # 노이즈가 적을수록 높은 점수 (역수 관계)
                noise_score = 1.0 - min(noise_level / 50.0, 1.0)

                return max(0.0, noise_score)
            else:
                # PIL을 사용한 간단한 노이즈 추정
                # 지역 분산을 이용한 노이즈 추정
                image_array = np.array(gray)

                # 3x3 커널로 지역 분산 계산
                kernel_size = 3
                height, width = image_array.shape
                variances = []

                for y in range(kernel_size, height - kernel_size, 10):
                    for x in range(kernel_size, width - kernel_size, 10):
                        patch = image_array[y-1:y+2, x-1:x+2]
                        variances.append(np.var(patch))

                if variances:
                    avg_variance = np.mean(variances)
                    # 분산이 클수록 노이즈가 많다고 가정
                    noise_score = 1.0 - min(avg_variance / 1000.0, 1.0)
                    return max(0.0, noise_score)
                else:
                    return 0.5

        except Exception as e:
            logger.debug(f"Noise measurement failed: {e}")
            return 0.5

    async def _measure_resolution_quality(self, image: Image.Image) -> float:
        """해상도 품질 측정"""
        try:
            width, height = image.size
            total_pixels = width * height

            # DPI 정보가 있으면 활용
            dpi = image.info.get('dpi')
            if dpi:
                # 최소 150 DPI, 최적 300 DPI
                avg_dpi = (dpi[0] + dpi[1]) / 2
                dpi_score = min(avg_dpi / 300.0, 1.0)
            else:
                dpi_score = 0.5  # DPI 정보 없음

            # 픽셀 수 기반 품질
            # 최소 800x600, 최적 2000x1500
            min_pixels = 800 * 600
            optimal_pixels = 2000 * 1500

            if total_pixels < min_pixels:
                pixel_score = total_pixels / min_pixels * 0.5
            elif total_pixels >= optimal_pixels:
                pixel_score = 1.0
            else:
                pixel_score = 0.5 + (total_pixels - min_pixels) / (optimal_pixels - min_pixels) * 0.5

            # 종횡비 확인 (너무 극단적이면 감점)
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 5.0:  # 너무 긴 이미지
                aspect_penalty = 0.8
            elif aspect_ratio > 3.0:
                aspect_penalty = 0.9
            else:
                aspect_penalty = 1.0

            # 최종 해상도 점수
            resolution_score = (dpi_score + pixel_score) / 2.0 * aspect_penalty

            return max(0.0, min(1.0, resolution_score))

        except Exception as e:
            logger.debug(f"Resolution measurement failed: {e}")
            return 0.5

    async def _measure_text_density(self, image: Image.Image) -> float:
        """텍스트 밀도 측정"""
        try:
            # 이진화 후 텍스트 영역 추정
            gray = image.convert('L')

            # 간단한 이진화
            threshold = 128
            binary = gray.point(lambda x: 0 if x < threshold else 255, '1')

            # 검은 픽셀 (텍스트) 비율 계산
            image_array = np.array(binary)
            total_pixels = image_array.size
            text_pixels = np.sum(image_array == 0)  # 검은 픽셀

            text_ratio = text_pixels / total_pixels

            # 적절한 텍스트 밀도는 0.1-0.4 정도
            if 0.05 <= text_ratio <= 0.5:
                # 적절한 범위 내에서는 높은 점수
                if 0.1 <= text_ratio <= 0.3:
                    density_score = 1.0
                elif text_ratio < 0.1:
                    density_score = text_ratio / 0.1
                else:  # text_ratio > 0.3
                    density_score = 1.0 - (text_ratio - 0.3) / 0.2
            else:
                # 범위를 벗어나면 낮은 점수
                if text_ratio < 0.05:
                    density_score = text_ratio / 0.05 * 0.3
                else:  # text_ratio > 0.5
                    density_score = 0.1

            return max(0.0, min(1.0, density_score))

        except Exception as e:
            logger.debug(f"Text density measurement failed: {e}")
            return 0.5

    async def _measure_skew_level(self, image: Image.Image) -> float:
        """기울기 수준 측정 (높을수록 기울기가 적음)"""
        try:
            if self._opencv_available:
                # OpenCV를 사용한 정확한 기울기 측정
                image_array = np.array(image.convert('L'))

                # 이진화
                _, binary = self.cv2.threshold(image_array, 0, 255, self.cv2.THRESH_BINARY + self.cv2.THRESH_OTSU)

                # 윤곽선 찾기
                contours, _ = self.cv2.findContours(binary, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    # 가장 큰 윤곽선에서 기울기 계산
                    largest_contour = max(contours, key=self.cv2.contourArea)
                    rect = self.cv2.minAreaRect(largest_contour)
                    angle = rect[2]

                    # 각도 정규화
                    if angle < -45:
                        angle = 90 + angle
                    elif angle > 45:
                        angle = angle - 90

                    # 기울기가 적을수록 높은 점수
                    skew_score = 1.0 - min(abs(angle) / 45.0, 1.0)
                    return max(0.0, skew_score)
                else:
                    return 0.5
            else:
                # PIL만 사용하는 간단한 기울기 추정
                # 수평선의 연속성을 기반으로 기울기 추정
                gray = image.convert('L')
                width, height = gray.size

                # 중간 영역의 수평선 연속성 확인
                horizontal_scores = []
                for y in range(height // 4, 3 * height // 4, height // 20):
                    row_pixels = [gray.getpixel((x, y)) for x in range(width)]

                    # 이진화
                    binary_row = [1 if p < 128 else 0 for p in row_pixels]

                    # 연속성 점수 계산
                    max_run = 0
                    current_run = 0
                    for pixel in binary_row:
                        if pixel == 1:
                            current_run += 1
                            max_run = max(max_run, current_run)
                        else:
                            current_run = 0

                    if width > 0:
                        horizontal_scores.append(max_run / width)

                if horizontal_scores:
                    avg_score = sum(horizontal_scores) / len(horizontal_scores)
                    return min(avg_score * 2, 1.0)  # 점수 증폭
                else:
                    return 0.5

        except Exception as e:
            logger.debug(f"Skew measurement failed: {e}")
            return 0.5

    async def recommend_enhancements(self, quality_metrics: QualityMetrics) -> List[EnhancementRecommendation]:
        """
        품질 지표를 바탕으로 향상 추천

        Args:
            quality_metrics: 품질 측정 지표

        Returns:
            추천사항 리스트 (우선순위 순)
        """
        recommendations = []

        # 대비 향상 추천
        if quality_metrics.contrast_score < self.thresholds['min_contrast']:
            recommendations.append(EnhancementRecommendation(
                enhancement_type="contrast",
                priority=4,
                reason=f"낮은 대비 ({quality_metrics.contrast_score:.2f})",
                expected_improvement=0.7,
                parameters={
                    "factor": 1.2 + (self.thresholds['min_contrast'] - quality_metrics.contrast_score),
                    "adaptive": True
                }
            ))

        # 밝기 보정 추천
        if quality_metrics.brightness_score < self.thresholds['min_brightness']:
            recommendations.append(EnhancementRecommendation(
                enhancement_type="brightness",
                priority=3,
                reason=f"부적절한 밝기 ({quality_metrics.brightness_score:.2f})",
                expected_improvement=0.6,
                parameters={
                    "auto_adjust": True
                }
            ))

        # 선명도 향상 추천
        if quality_metrics.sharpness_score < self.thresholds['min_sharpness']:
            recommendations.append(EnhancementRecommendation(
                enhancement_type="sharpening",
                priority=4,
                reason=f"낮은 선명도 ({quality_metrics.sharpness_score:.2f})",
                expected_improvement=0.8,
                parameters={
                    "strength": 1.5 + (self.thresholds['min_sharpness'] - quality_metrics.sharpness_score)
                }
            ))

        # 노이즈 제거 추천
        if quality_metrics.noise_score < (1.0 - self.thresholds['max_noise']):
            noise_strength = 1 if quality_metrics.noise_score > 0.6 else 2 if quality_metrics.noise_score > 0.3 else 3
            recommendations.append(EnhancementRecommendation(
                enhancement_type="noise_reduction",
                priority=2,
                reason=f"높은 노이즈 수준 ({1.0 - quality_metrics.noise_score:.2f})",
                expected_improvement=0.5,
                parameters={
                    "strength": noise_strength
                }
            ))

        # 기울기 보정 추천
        if quality_metrics.skew_score < 0.8:  # 기울기가 있음
            recommendations.append(EnhancementRecommendation(
                enhancement_type="deskew",
                priority=5,
                reason=f"이미지 기울기 감지 ({quality_metrics.skew_score:.2f})",
                expected_improvement=0.9,
                parameters={
                    "max_angle": self.thresholds['max_skew']
                }
            ))

        # 해상도 향상 추천 (크기가 너무 작은 경우)
        if quality_metrics.resolution_score < self.thresholds['min_resolution']:
            width, height = quality_metrics.image_size
            if width < 1000 or height < 800:
                recommendations.append(EnhancementRecommendation(
                    enhancement_type="resize",
                    priority=1,
                    reason=f"낮은 해상도 ({width}x{height})",
                    expected_improvement=0.4,
                    parameters={
                        "target_dpi": 300,
                        "min_width": 1200
                    }
                ))

        # 우선순위로 정렬 (높은 우선순위부터)
        recommendations.sort(key=lambda x: x.priority, reverse=True)

        return recommendations

    def predict_ocr_success_rate(self, quality_metrics: QualityMetrics) -> float:
        """
        OCR 성공률 예측

        Args:
            quality_metrics: 품질 측정 지표

        Returns:
            성공률 예측 (0.0-1.0)
        """
        # 각 지표의 가중치
        weights = {
            'sharpness': 0.25,
            'contrast': 0.20,
            'skew': 0.20,
            'brightness': 0.15,
            'text_density': 0.10,
            'noise': 0.05,
            'resolution': 0.05
        }

        # 가중 평균 계산
        success_rate = (
            quality_metrics.sharpness_score * weights['sharpness'] +
            quality_metrics.contrast_score * weights['contrast'] +
            quality_metrics.skew_score * weights['skew'] +
            quality_metrics.brightness_score * weights['brightness'] +
            quality_metrics.text_density_score * weights['text_density'] +
            quality_metrics.noise_score * weights['noise'] +
            quality_metrics.resolution_score * weights['resolution']
        )

        # 추가 보정
        # 매우 낮은 해상도는 큰 패널티
        if quality_metrics.resolution_score < 0.3:
            success_rate *= 0.7

        # 매우 낮은 텍스트 밀도는 패널티
        if quality_metrics.text_density_score < 0.2:
            success_rate *= 0.8

        # 전체 품질이 너무 낮으면 패널티
        if quality_metrics.overall_score < 0.3:
            success_rate *= 0.6

        return max(0.0, min(1.0, success_rate))

    def _estimate_processing_time(
        self,
        image_path: Path,
        recommendations: List[EnhancementRecommendation]
    ) -> float:
        """
        처리 시간 추정

        Args:
            image_path: 이미지 경로
            recommendations: 추천사항 리스트

        Returns:
            예상 처리 시간 (초)
        """
        try:
            # 이미지 크기 기반 기본 시간
            file_size_mb = image_path.stat().st_size / (1024 * 1024)
            base_time = max(0.5, file_size_mb * 0.3)  # 기본 0.5초 + 파일 크기

            # 추천사항별 추가 시간
            enhancement_times = {
                'contrast': 0.2,
                'brightness': 0.1,
                'sharpening': 0.3,
                'noise_reduction': 0.8,
                'deskew': 0.5,
                'resize': 0.4
            }

            additional_time = sum(
                enhancement_times.get(rec.enhancement_type, 0.2)
                for rec in recommendations
            )

            total_time = base_time + additional_time

            # OpenCV가 없으면 시간 증가
            if not self._opencv_available:
                total_time *= 1.5

            return total_time

        except Exception:
            return 2.0  # 기본값