"""
이미지 향상 도구
OCR 정확도 향상을 위한 다양한 이미지 향상 알고리즘 구현
"""

import asyncio
import logging
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

logger = logging.getLogger(__name__)


class EnhancementType(Enum):
    """향상 유형"""
    CONTRAST = "contrast"
    BRIGHTNESS = "brightness"
    DESKEW = "deskew"
    NOISE_REDUCTION = "noise_reduction"
    SHARPENING = "sharpening"
    BINARIZATION = "binarization"
    RESIZE = "resize"


@dataclass
class EnhancementResult:
    """향상 결과"""
    enhanced_image_path: Optional[Path] = None
    original_image_path: Optional[Path] = None
    enhancements_applied: List[EnhancementType] = None
    processing_time: float = 0.0
    improvement_score: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.enhancements_applied is None:
            self.enhancements_applied = []
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_success(self) -> bool:
        """성공 여부"""
        return self.enhanced_image_path is not None and self.error_message is None


@dataclass
class EnhancementParameters:
    """향상 매개변수"""
    # 대비 조정
    contrast_factor: float = 1.0  # 1.0 = 원본, >1.0 = 증가, <1.0 = 감소

    # 밝기 조정
    brightness_factor: float = 1.0  # 1.0 = 원본, >1.0 = 밝게, <1.0 = 어둡게

    # 기울기 보정
    deskew_enabled: bool = True
    deskew_max_angle: float = 45.0  # 최대 보정 각도

    # 노이즈 제거
    noise_reduction_strength: int = 1  # 1-3 (약함-강함)

    # 선명도 향상
    sharpening_strength: float = 1.0  # 1.0 = 기본, >1.0 = 강함

    # 이진화
    binarization_threshold: Optional[int] = None  # None = 자동, 0-255 = 수동

    # 크기 조정
    target_dpi: Optional[int] = 300  # 목표 DPI
    min_width: int = 800  # 최소 너비
    max_width: int = 4000  # 최대 너비


class ImageEnhancer:
    """이미지 향상 클래스"""

    def __init__(self, config: Optional[Dict] = None):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}
        self.temp_dir = Path(tempfile.gettempdir()) / "markitdown_preprocessing"
        self.temp_dir.mkdir(exist_ok=True)

        # OpenCV 가용성 확인
        self._opencv_available = self._check_opencv()
        if self._opencv_available:
            import cv2
            self.cv2 = cv2
            logger.info("OpenCV available for advanced image processing")
        else:
            logger.info("Using PIL-only image processing")

    def _check_opencv(self) -> bool:
        """OpenCV 가용성 확인"""
        try:
            import cv2
            return True
        except ImportError:
            return False

    async def enhance_contrast(
        self,
        image_path: Path,
        factor: float = 1.2,
        adaptive: bool = True
    ) -> EnhancementResult:
        """
        대비 향상

        Args:
            image_path: 이미지 경로
            factor: 대비 조정 계수
            adaptive: 적응적 대비 향상 사용

        Returns:
            향상 결과
        """
        start_time = time.time()

        try:
            with Image.open(image_path) as image:
                # 적응적 대비 향상
                if adaptive and self._opencv_available:
                    enhanced_image = await self._adaptive_contrast_opencv(image)
                else:
                    # 기본 대비 향상
                    enhancer = ImageEnhance.Contrast(image)
                    enhanced_image = enhancer.enhance(factor)

                # 결과 저장
                output_path = self._get_temp_path(image_path, "contrast")
                enhanced_image.save(output_path, "PNG")

                processing_time = time.time() - start_time

                return EnhancementResult(
                    enhanced_image_path=output_path,
                    original_image_path=image_path,
                    enhancements_applied=[EnhancementType.CONTRAST],
                    processing_time=processing_time,
                    improvement_score=self._calculate_contrast_improvement(image, enhanced_image),
                    metadata={"factor": factor, "adaptive": adaptive}
                )

        except Exception as e:
            logger.error(f"Contrast enhancement failed: {e}")
            return EnhancementResult(
                original_image_path=image_path,
                error_message=f"Contrast enhancement failed: {str(e)}"
            )

    async def _adaptive_contrast_opencv(self, image: Image.Image) -> Image.Image:
        """OpenCV를 사용한 적응적 대비 향상"""
        # PIL을 OpenCV로 변환
        image_array = np.array(image)

        # 그레이스케일 변환
        if len(image_array.shape) == 3:
            gray = self.cv2.cvtColor(image_array, self.cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array

        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = self.cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_array = clahe.apply(gray)

        # PIL로 다시 변환
        return Image.fromarray(enhanced_array)

    async def correct_brightness(
        self,
        image_path: Path,
        factor: Optional[float] = None,
        auto_adjust: bool = True
    ) -> EnhancementResult:
        """
        밝기 보정

        Args:
            image_path: 이미지 경로
            factor: 밝기 조정 계수 (None이면 자동)
            auto_adjust: 자동 밝기 조정

        Returns:
            향상 결과
        """
        start_time = time.time()

        try:
            with Image.open(image_path) as image:
                if auto_adjust or factor is None:
                    # 자동 밝기 조정
                    optimal_factor = self._calculate_optimal_brightness(image)
                else:
                    optimal_factor = factor

                enhancer = ImageEnhance.Brightness(image)
                enhanced_image = enhancer.enhance(optimal_factor)

                # 결과 저장
                output_path = self._get_temp_path(image_path, "brightness")
                enhanced_image.save(output_path, "PNG")

                processing_time = time.time() - start_time

                return EnhancementResult(
                    enhanced_image_path=output_path,
                    original_image_path=image_path,
                    enhancements_applied=[EnhancementType.BRIGHTNESS],
                    processing_time=processing_time,
                    improvement_score=self._calculate_brightness_improvement(image, enhanced_image),
                    metadata={"factor": optimal_factor, "auto_adjust": auto_adjust}
                )

        except Exception as e:
            logger.error(f"Brightness correction failed: {e}")
            return EnhancementResult(
                original_image_path=image_path,
                error_message=f"Brightness correction failed: {str(e)}"
            )

    async def deskew_image(
        self,
        image_path: Path,
        max_angle: float = 45.0
    ) -> EnhancementResult:
        """
        이미지 기울기 보정

        Args:
            image_path: 이미지 경로
            max_angle: 최대 보정 각도

        Returns:
            향상 결과
        """
        start_time = time.time()

        try:
            with Image.open(image_path) as image:
                if self._opencv_available:
                    # OpenCV를 사용한 고급 기울기 감지
                    deskewed_image, angle = await self._deskew_opencv(image, max_angle)
                else:
                    # PIL을 사용한 간단한 기울기 보정
                    deskewed_image, angle = await self._deskew_pil(image, max_angle)

                # 결과 저장
                output_path = self._get_temp_path(image_path, "deskew")
                deskewed_image.save(output_path, "PNG")

                processing_time = time.time() - start_time

                return EnhancementResult(
                    enhanced_image_path=output_path,
                    original_image_path=image_path,
                    enhancements_applied=[EnhancementType.DESKEW],
                    processing_time=processing_time,
                    improvement_score=abs(angle) / max_angle,  # 보정된 각도 비율
                    metadata={"detected_angle": angle, "max_angle": max_angle}
                )

        except Exception as e:
            logger.error(f"Deskewing failed: {e}")
            return EnhancementResult(
                original_image_path=image_path,
                error_message=f"Deskewing failed: {str(e)}"
            )

    async def _deskew_opencv(
        self,
        image: Image.Image,
        max_angle: float
    ) -> Tuple[Image.Image, float]:
        """OpenCV를 사용한 기울기 보정"""
        # PIL을 OpenCV로 변환
        image_array = np.array(image)

        # 그레이스케일 변환
        if len(image_array.shape) == 3:
            gray = self.cv2.cvtColor(image_array, self.cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array

        # 이진화
        _, binary = self.cv2.threshold(gray, 0, 255, self.cv2.THRESH_BINARY + self.cv2.THRESH_OTSU)

        # 윤곽선 찾기
        contours, _ = self.cv2.findContours(binary, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)

        # 가장 큰 윤곽선에서 기울기 계산
        angle = 0.0
        if contours:
            largest_contour = max(contours, key=self.cv2.contourArea)
            rect = self.cv2.minAreaRect(largest_contour)
            angle = rect[2]

            # 각도 보정
            if angle < -45:
                angle = 90 + angle
            elif angle > 45:
                angle = angle - 90

            # 최대 각도 제한
            angle = max(-max_angle, min(max_angle, angle))

        # 회전 적용
        if abs(angle) > 0.1:  # 0.1도 이상일 때만 보정
            height, width = gray.shape
            center = (width // 2, height // 2)
            matrix = self.cv2.getRotationMatrix2D(center, angle, 1.0)

            rotated = self.cv2.warpAffine(
                image_array, matrix, (width, height),
                flags=self.cv2.INTER_CUBIC,
                borderMode=self.cv2.BORDER_REPLICATE
            )

            return Image.fromarray(rotated), angle
        else:
            return image, angle

    async def _deskew_pil(
        self,
        image: Image.Image,
        max_angle: float
    ) -> Tuple[Image.Image, float]:
        """PIL을 사용한 간단한 기울기 보정"""
        # 간단한 휴리스틱 기반 기울기 감지
        # 실제로는 더 복잡한 알고리즘이 필요하지만, 기본 구현

        # 작은 각도들로 테스트해서 최적 각도 찾기
        best_angle = 0.0
        best_score = float('-inf')

        test_angles = np.linspace(-max_angle, max_angle, 19)  # -45도 ~ 45도를 19개 구간으로

        for angle in test_angles:
            if abs(angle) < 0.1:
                continue

            rotated = image.rotate(-angle, expand=True, fillcolor='white')
            score = self._calculate_deskew_score(rotated)

            if score > best_score:
                best_score = score
                best_angle = angle

        # 최적 각도로 회전
        if abs(best_angle) > 0.1:
            deskewed = image.rotate(-best_angle, expand=True, fillcolor='white')
            return deskewed, best_angle
        else:
            return image, 0.0

    def _calculate_deskew_score(self, image: Image.Image) -> float:
        """기울기 보정 점수 계산 (간단한 휴리스틱)"""
        # 그레이스케일 변환
        gray = image.convert('L')

        # 이진화
        threshold = ImageOps.autocontrast(gray)
        binary = threshold.point(lambda x: 0 if x < 128 else 255, '1')

        # 가로선의 수를 계산해서 점수 반환
        # 제대로 정렬된 텍스트는 더 많은 수평선을 가질 것
        width, height = binary.size
        horizontal_score = 0

        for y in range(height // 4, 3 * height // 4, 4):
            row_pixels = [binary.getpixel((x, y)) for x in range(width)]
            # 연속된 검은 픽셀의 수
            consecutive_count = 0
            max_consecutive = 0

            for pixel in row_pixels:
                if pixel == 0:  # 검은 픽셀
                    consecutive_count += 1
                    max_consecutive = max(max_consecutive, consecutive_count)
                else:
                    consecutive_count = 0

            horizontal_score += max_consecutive

        return horizontal_score

    async def remove_noise(
        self,
        image_path: Path,
        strength: int = 1
    ) -> EnhancementResult:
        """
        노이즈 제거

        Args:
            image_path: 이미지 경로
            strength: 노이즈 제거 강도 (1-3)

        Returns:
            향상 결과
        """
        start_time = time.time()

        try:
            with Image.open(image_path) as image:
                if self._opencv_available:
                    # OpenCV를 사용한 고급 노이즈 제거
                    denoised_image = await self._denoise_opencv(image, strength)
                else:
                    # PIL을 사용한 기본 노이즈 제거
                    denoised_image = await self._denoise_pil(image, strength)

                # 결과 저장
                output_path = self._get_temp_path(image_path, "denoise")
                denoised_image.save(output_path, "PNG")

                processing_time = time.time() - start_time

                return EnhancementResult(
                    enhanced_image_path=output_path,
                    original_image_path=image_path,
                    enhancements_applied=[EnhancementType.NOISE_REDUCTION],
                    processing_time=processing_time,
                    improvement_score=0.7,  # 고정값 (실제로는 노이즈 감소량 측정)
                    metadata={"strength": strength}
                )

        except Exception as e:
            logger.error(f"Noise removal failed: {e}")
            return EnhancementResult(
                original_image_path=image_path,
                error_message=f"Noise removal failed: {str(e)}"
            )

    async def _denoise_opencv(self, image: Image.Image, strength: int) -> Image.Image:
        """OpenCV를 사용한 노이즈 제거"""
        image_array = np.array(image)

        if len(image_array.shape) == 3:
            # 컬러 이미지
            if strength == 1:
                denoised = self.cv2.fastNlMeansDenoisingColored(image_array, None, 10, 10, 7, 21)
            elif strength == 2:
                denoised = self.cv2.fastNlMeansDenoisingColored(image_array, None, 20, 20, 7, 21)
            else:  # strength == 3
                denoised = self.cv2.fastNlMeansDenoisingColored(image_array, None, 30, 30, 7, 21)
        else:
            # 그레이스케일 이미지
            if strength == 1:
                denoised = self.cv2.fastNlMeansDenoising(image_array, None, 10, 7, 21)
            elif strength == 2:
                denoised = self.cv2.fastNlMeansDenoising(image_array, None, 20, 7, 21)
            else:  # strength == 3
                denoised = self.cv2.fastNlMeansDenoising(image_array, None, 30, 7, 21)

        return Image.fromarray(denoised)

    async def _denoise_pil(self, image: Image.Image, strength: int) -> Image.Image:
        """PIL을 사용한 기본 노이즈 제거"""
        if strength == 1:
            # 약한 블러
            return image.filter(ImageFilter.BLUR)
        elif strength == 2:
            # 가우시안 블러
            return image.filter(ImageFilter.GaussianBlur(radius=1))
        else:  # strength == 3
            # 미디안 필터
            return image.filter(ImageFilter.MedianFilter(size=3))

    async def sharpen_image(
        self,
        image_path: Path,
        strength: float = 1.0
    ) -> EnhancementResult:
        """
        이미지 선명도 향상

        Args:
            image_path: 이미지 경로
            strength: 선명도 강도

        Returns:
            향상 결과
        """
        start_time = time.time()

        try:
            with Image.open(image_path) as image:
                if self._opencv_available and strength > 1.5:
                    # OpenCV를 사용한 고급 선명화
                    sharpened_image = await self._sharpen_opencv(image, strength)
                else:
                    # PIL을 사용한 기본 선명화
                    enhancer = ImageEnhance.Sharpness(image)
                    sharpened_image = enhancer.enhance(strength)

                # 결과 저장
                output_path = self._get_temp_path(image_path, "sharpen")
                sharpened_image.save(output_path, "PNG")

                processing_time = time.time() - start_time

                return EnhancementResult(
                    enhanced_image_path=output_path,
                    original_image_path=image_path,
                    enhancements_applied=[EnhancementType.SHARPENING],
                    processing_time=processing_time,
                    improvement_score=min(strength / 2.0, 1.0),  # 강도 기반 점수
                    metadata={"strength": strength}
                )

        except Exception as e:
            logger.error(f"Sharpening failed: {e}")
            return EnhancementResult(
                original_image_path=image_path,
                error_message=f"Sharpening failed: {str(e)}"
            )

    async def _sharpen_opencv(self, image: Image.Image, strength: float) -> Image.Image:
        """OpenCV를 사용한 고급 선명화"""
        image_array = np.array(image)

        # 언샵 마스크 필터
        kernel = np.array([[-1, -1, -1],
                          [-1, 9, -1],
                          [-1, -1, -1]]) * strength

        sharpened = self.cv2.filter2D(image_array, -1, kernel)

        return Image.fromarray(np.clip(sharpened, 0, 255).astype(np.uint8))

    async def apply_multiple_enhancements(
        self,
        image_path: Path,
        parameters: EnhancementParameters
    ) -> EnhancementResult:
        """
        여러 향상 기법을 순차적으로 적용

        Args:
            image_path: 이미지 경로
            parameters: 향상 매개변수

        Returns:
            종합 향상 결과
        """
        start_time = time.time()
        current_path = image_path
        applied_enhancements = []
        total_improvement = 0.0
        metadata = {}

        try:
            # 1. 기울기 보정 (가장 먼저)
            if parameters.deskew_enabled:
                result = await self.deskew_image(current_path, parameters.deskew_max_angle)
                if result.is_success:
                    current_path = result.enhanced_image_path
                    applied_enhancements.append(EnhancementType.DESKEW)
                    total_improvement += result.improvement_score * 0.2
                    metadata.update(result.metadata)

            # 2. 노이즈 제거
            if parameters.noise_reduction_strength > 0:
                result = await self.remove_noise(current_path, parameters.noise_reduction_strength)
                if result.is_success:
                    current_path = result.enhanced_image_path
                    applied_enhancements.append(EnhancementType.NOISE_REDUCTION)
                    total_improvement += result.improvement_score * 0.15
                    metadata.update(result.metadata)

            # 3. 대비 조정
            if parameters.contrast_factor != 1.0:
                result = await self.enhance_contrast(current_path, parameters.contrast_factor)
                if result.is_success:
                    current_path = result.enhanced_image_path
                    applied_enhancements.append(EnhancementType.CONTRAST)
                    total_improvement += result.improvement_score * 0.25
                    metadata.update(result.metadata)

            # 4. 밝기 조정
            if parameters.brightness_factor != 1.0:
                result = await self.correct_brightness(current_path, parameters.brightness_factor)
                if result.is_success:
                    current_path = result.enhanced_image_path
                    applied_enhancements.append(EnhancementType.BRIGHTNESS)
                    total_improvement += result.improvement_score * 0.2
                    metadata.update(result.metadata)

            # 5. 선명도 향상
            if parameters.sharpening_strength != 1.0:
                result = await self.sharpen_image(current_path, parameters.sharpening_strength)
                if result.is_success:
                    current_path = result.enhanced_image_path
                    applied_enhancements.append(EnhancementType.SHARPENING)
                    total_improvement += result.improvement_score * 0.2
                    metadata.update(result.metadata)

            processing_time = time.time() - start_time

            return EnhancementResult(
                enhanced_image_path=current_path,
                original_image_path=image_path,
                enhancements_applied=applied_enhancements,
                processing_time=processing_time,
                improvement_score=min(total_improvement, 1.0),
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Multiple enhancements failed: {e}")
            return EnhancementResult(
                original_image_path=image_path,
                error_message=f"Multiple enhancements failed: {str(e)}"
            )

    def _get_temp_path(self, original_path: Path, enhancement_type: str) -> Path:
        """임시 파일 경로 생성"""
        filename = f"{original_path.stem}_{enhancement_type}_{int(time.time())}.png"
        return self.temp_dir / filename

    def _calculate_contrast_improvement(self, original: Image.Image, enhanced: Image.Image) -> float:
        """대비 향상도 계산"""
        try:
            # 간단한 표준편차 기반 대비 측정
            orig_std = np.std(np.array(original.convert('L')))
            enh_std = np.std(np.array(enhanced.convert('L')))

            if orig_std == 0:
                return 0.0

            improvement = (enh_std - orig_std) / orig_std
            return max(0.0, min(1.0, improvement))
        except Exception:
            return 0.5  # 기본값

    def _calculate_brightness_improvement(self, original: Image.Image, enhanced: Image.Image) -> float:
        """밝기 향상도 계산"""
        try:
            # 평균 밝기 변화 측정
            orig_mean = np.mean(np.array(original.convert('L')))
            enh_mean = np.mean(np.array(enhanced.convert('L')))

            # 128에 가까워지는 정도로 향상도 측정
            orig_distance = abs(orig_mean - 128)
            enh_distance = abs(enh_mean - 128)

            if orig_distance == 0:
                return 1.0

            improvement = (orig_distance - enh_distance) / orig_distance
            return max(0.0, min(1.0, improvement))
        except Exception:
            return 0.5  # 기본값

    def _calculate_optimal_brightness(self, image: Image.Image) -> float:
        """최적 밝기 계수 계산"""
        try:
            # 그레이스케일로 변환하여 평균 밝기 계산
            gray = image.convert('L')
            mean_brightness = np.mean(np.array(gray))

            # 목표 밝기 (128)에 맞춰 조정 계수 계산
            if mean_brightness < 80:
                # 너무 어두움
                return 1.2 + (80 - mean_brightness) / 80 * 0.5
            elif mean_brightness > 180:
                # 너무 밝음
                return 0.8 - (mean_brightness - 180) / 75 * 0.3
            else:
                # 적당한 밝기
                return 1.0 + (128 - mean_brightness) / 128 * 0.2

        except Exception:
            return 1.0  # 기본값

    def cleanup(self):
        """임시 파일 정리"""
        try:
            for temp_file in self.temp_dir.glob("*.png"):
                try:
                    temp_file.unlink()
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Cleanup warning: {e}")