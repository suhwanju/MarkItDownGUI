"""
OCR Enhancement Module Data Models
OCR 개선 기능을 위한 데이터 모델들
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models import FileInfo, ConversionResult, OCRResult


class OCREnhancementType(Enum):
    """OCR 개선 유형"""
    ACCURACY_BOOST = "accuracy_boost"      # 정확도 향상
    PREPROCESSING = "preprocessing"        # 이미지 전처리
    POST_PROCESSING = "post_processing"    # 후처리
    LANGUAGE_DETECTION = "language_detection"  # 언어 감지
    CONFIDENCE_ANALYSIS = "confidence_analysis"  # 신뢰도 분석
    LAYOUT_ANALYSIS = "layout_analysis"    # 레이아웃 분석
    QUALITY_ASSESSMENT = "quality_assessment"  # 품질 평가


class OCRStatusType(Enum):
    """OCR 상태 유형"""
    IDLE = "idle"                      # 대기 중
    INITIALIZING = "initializing"      # 초기화 중
    PREPROCESSING = "preprocessing"    # 전처리 중
    PROCESSING = "processing"          # 처리 중
    POST_PROCESSING = "post_processing"  # 후처리 중
    ANALYZING = "analyzing"            # 분석 중
    COMPLETED = "completed"            # 완료
    FAILED = "failed"                  # 실패
    CANCELLED = "cancelled"            # 취소됨


class QualityLevel(Enum):
    """품질 수준"""
    EXCELLENT = "excellent"    # 95-100%
    GOOD = "good"             # 80-94%
    FAIR = "fair"             # 60-79%
    POOR = "poor"             # 40-59%
    VERY_POOR = "very_poor"   # 0-39%


@dataclass
class OCREnhancementConfig:
    """OCR Enhancement 설정"""
    # 기본 활성화 설정
    enabled: bool = False

    # 개선 기능 활성화 설정
    accuracy_boost_enabled: bool = False
    preprocessing_enabled: bool = True
    post_processing_enabled: bool = True
    language_detection_enabled: bool = True
    confidence_analysis_enabled: bool = True
    layout_analysis_enabled: bool = False
    quality_assessment_enabled: bool = True

    # 성능 설정
    max_concurrent_enhancements: int = 2
    enhancement_timeout: int = 60  # 초
    cache_results: bool = True
    cache_ttl: int = 3600  # 초

    # 품질 임계값
    min_confidence_threshold: float = 0.7
    retry_on_low_confidence: bool = True
    max_retry_attempts: int = 2

    # 전처리 설정
    image_enhancement_enabled: bool = True
    noise_reduction_enabled: bool = True
    contrast_adjustment_enabled: bool = True

    # 후처리 설정
    spell_check_enabled: bool = False
    grammar_check_enabled: bool = False
    formatting_cleanup_enabled: bool = True

    def is_any_enhancement_enabled(self) -> bool:
        """어떤 개선 기능이라도 활성화되어 있는지 확인"""
        return any([
            self.accuracy_boost_enabled,
            self.preprocessing_enabled,
            self.post_processing_enabled,
            self.language_detection_enabled,
            self.confidence_analysis_enabled,
            self.layout_analysis_enabled,
            self.quality_assessment_enabled
        ])

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OCREnhancementConfig':
        """딕셔너리로부터 설정 객체 생성"""
        config = cls()

        # 기본 설정 매핑
        field_mapping = {
            'enabled': 'enabled',
            'accuracy_boost_enabled': 'accuracy_boost_enabled',
            'preprocessing_enabled': 'preprocessing_enabled',
            'post_processing_enabled': 'post_processing_enabled',
            'language_detection_enabled': 'language_detection_enabled',
            'confidence_analysis_enabled': 'confidence_analysis_enabled',
            'layout_analysis_enabled': 'layout_analysis_enabled',
            'quality_assessment_enabled': 'quality_assessment_enabled',
            'max_concurrent_enhancements': 'max_concurrent_enhancements',
            'enhancement_timeout': 'enhancement_timeout',
            'cache_results': 'cache_results',
            'cache_ttl': 'cache_ttl',
            'min_confidence_threshold': 'min_confidence_threshold',
            'retry_on_low_confidence': 'retry_on_low_confidence',
            'max_retry_attempts': 'max_retry_attempts',
            'image_enhancement_enabled': 'image_enhancement_enabled',
            'noise_reduction_enabled': 'noise_reduction_enabled',
            'contrast_adjustment_enabled': 'contrast_adjustment_enabled',
            'spell_check_enabled': 'spell_check_enabled',
            'grammar_check_enabled': 'grammar_check_enabled',
            'formatting_cleanup_enabled': 'formatting_cleanup_enabled'
        }

        # 데이터에서 설정값 추출하여 적용
        for data_key, config_attr in field_mapping.items():
            if data_key in data:
                setattr(config, config_attr, data[data_key])

        return config


@dataclass
class OCRStatusInfo:
    """OCR 상태 정보"""
    status: OCRStatusType
    current_step: str = ""
    progress_percent: float = 0.0
    estimated_time_remaining: Optional[float] = None  # 초
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.started_at is None and self.status != OCRStatusType.IDLE:
            self.started_at = datetime.now()

    @property
    def elapsed_time(self) -> float:
        """경과 시간 (초)"""
        if self.started_at is None:
            return 0.0
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()

    @property
    def is_active(self) -> bool:
        """활성 상태 여부"""
        return self.status in [
            OCRStatusType.INITIALIZING,
            OCRStatusType.PREPROCESSING,
            OCRStatusType.PROCESSING,
            OCRStatusType.POST_PROCESSING,
            OCRStatusType.ANALYZING
        ]

    @property
    def is_completed(self) -> bool:
        """완료 상태 여부"""
        return self.status in [
            OCRStatusType.COMPLETED,
            OCRStatusType.FAILED,
            OCRStatusType.CANCELLED
        ]


@dataclass
class OCRProgressInfo:
    """OCR 진행률 정보"""
    total_steps: int
    completed_steps: int
    current_step_name: str = ""
    current_step_progress: float = 0.0  # 현재 단계 내 진행률 (0.0-1.0)
    enhancement_types: List[OCREnhancementType] = field(default_factory=list)

    @property
    def overall_progress(self) -> float:
        """전체 진행률 (0.0-1.0)"""
        if self.total_steps == 0:
            return 0.0

        base_progress = self.completed_steps / self.total_steps
        current_contribution = self.current_step_progress / self.total_steps
        return min(1.0, base_progress + current_contribution)

    @property
    def progress_percent(self) -> float:
        """진행률 퍼센트"""
        return self.overall_progress * 100


@dataclass
class QualityMetrics:
    """품질 메트릭"""
    confidence_score: float = 0.0
    clarity_score: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    overall_quality: QualityLevel = QualityLevel.POOR

    # 세부 메트릭
    character_count: int = 0
    word_count: int = 0
    line_count: int = 0
    detected_issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def calculate_overall_quality(self) -> QualityLevel:
        """전체 품질 수준 계산"""
        avg_score = (
            self.confidence_score +
            self.clarity_score +
            self.completeness_score +
            self.consistency_score
        ) / 4

        if avg_score >= 0.95:
            return QualityLevel.EXCELLENT
        elif avg_score >= 0.80:
            return QualityLevel.GOOD
        elif avg_score >= 0.60:
            return QualityLevel.FAIR
        elif avg_score >= 0.40:
            return QualityLevel.POOR
        else:
            return QualityLevel.VERY_POOR


@dataclass
class LayoutInfo:
    """레이아웃 정보"""
    text_regions: List[Dict[str, Any]] = field(default_factory=list)
    table_regions: List[Dict[str, Any]] = field(default_factory=list)
    image_regions: List[Dict[str, Any]] = field(default_factory=list)
    reading_order: List[int] = field(default_factory=list)
    column_count: int = 1
    page_orientation: str = "portrait"
    text_alignment: str = "left"


@dataclass
class OCREnhancementResult:
    """OCR 개선 결과"""
    file_info: FileInfo
    original_result: OCRResult
    enhanced_text: str

    # 상태 정보
    status_info: OCRStatusInfo
    progress_info: OCRProgressInfo

    # 품질 분석
    quality_metrics: QualityMetrics
    improvement_ratio: float = 0.0  # 개선 비율

    # 적용된 개선 사항
    applied_enhancements: List[OCREnhancementType] = field(default_factory=list)
    enhancement_details: Dict[str, Any] = field(default_factory=dict)

    # 레이아웃 정보 (선택적)
    layout_info: Optional[LayoutInfo] = None

    # 성능 메트릭
    processing_time: float = 0.0
    enhancement_overhead: float = 0.0  # 개선 처리로 인한 추가 시간

    # 메타데이터
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    @property
    def is_improved(self) -> bool:
        """개선 여부"""
        return self.improvement_ratio > 0.0 and len(self.applied_enhancements) > 0

    @property
    def enhancement_summary(self) -> str:
        """개선 요약"""
        if not self.is_improved:
            return "No improvements applied"

        enhancement_names = [e.value for e in self.applied_enhancements]
        return f"Applied {len(enhancement_names)} enhancements: {', '.join(enhancement_names)}"

    def get_final_result(self) -> OCRResult:
        """최종 OCR 결과 생성"""
        # 원본 결과를 기반으로 개선된 결과 생성
        enhanced_result = OCRResult(
            text=self.enhanced_text,
            confidence=max(self.original_result.confidence, self.quality_metrics.confidence_score),
            language_detected=self.original_result.language_detected,
            processing_time=self.original_result.processing_time + self.enhancement_overhead,
            token_usage=self.original_result.token_usage,
            error_message=self.original_result.error_message
        )

        return enhanced_result


@dataclass
class EnhancementStats:
    """개선 통계"""
    total_files_processed: int = 0
    total_improvements_applied: int = 0
    average_improvement_ratio: float = 0.0
    most_effective_enhancement: Optional[OCREnhancementType] = None
    total_processing_time: float = 0.0
    cache_hit_rate: float = 0.0

    # 품질 분포
    quality_distribution: Dict[QualityLevel, int] = field(default_factory=dict)

    # 호환성을 위한 별칭 프로퍼티들
    @property
    def total_processed(self) -> int:
        """총 처리된 파일 수 (호환성)"""
        return self.total_files_processed

    @property
    def successful_enhancements(self) -> int:
        """성공한 개선 수 (호환성)"""
        return self.total_improvements_applied

    @property
    def failed_enhancements(self) -> int:
        """실패한 개선 수 (호환성)"""
        return max(0, self.total_files_processed - self.total_improvements_applied)

    @property
    def average_processing_time(self) -> float:
        """평균 처리 시간 (호환성)"""
        if self.total_files_processed == 0:
            return 0.0
        return self.total_processing_time / self.total_files_processed

    @property
    def total_improvement_ratio(self) -> float:
        """총 개선 비율 (호환성)"""
        return self.average_improvement_ratio

    def add_result(self, result: OCREnhancementResult):
        """결과 추가"""
        self.total_files_processed += 1

        if result.is_improved:
            self.total_improvements_applied += 1

            # 평균 개선 비율 업데이트
            self.average_improvement_ratio = (
                (self.average_improvement_ratio * (self.total_improvements_applied - 1) +
                 result.improvement_ratio) / self.total_improvements_applied
            )

        self.total_processing_time += result.processing_time

        # 품질 분포 업데이트
        quality = result.quality_metrics.overall_quality
        self.quality_distribution[quality] = self.quality_distribution.get(quality, 0) + 1

    @property
    def improvement_rate(self) -> float:
        """개선률"""
        if self.total_files_processed == 0:
            return 0.0
        return (self.total_improvements_applied / self.total_files_processed) * 100