"""
OCR Progress Tracker
OCR 진행률 추적기

Enhanced progress tracking for OCR operations with ProgressWidget integration.
Provides OCR-specific progress stages and real-time progress updates.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QProgressBar, QLabel
from PyQt6.QtGui import QColor
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta

from ..models import (
    OCREnhancementConfig, OCRStatusType, OCRProgressInfo,
    OCREnhancementType, OCRStatusInfo, OCREnhancementResult
)
from ...models import FileInfo, ConversionProgress, ConversionProgressStatus
from ...logger import get_logger

logger = get_logger(__name__)


class OCRStageProgressBar(QProgressBar):
    """OCR 단계별 진행률 바"""

    def __init__(self):
        super().__init__()
        self.setMinimum(0)
        self.setMaximum(100)
        self.setTextVisible(True)
        self._current_stage = OCRStatusType.IDLE
        self._setup_styles()

    def _setup_styles(self):
        """스타일 설정"""
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                text-align: center;
                font-size: 10px;
                height: 18px;
            }
            QProgressBar::chunk {
                border-radius: 2px;
            }
        """)

    def update_stage(self, stage: OCRStatusType, progress: float = 0.0):
        """현재 단계와 진행률 업데이트"""
        self._current_stage = stage
        self.setValue(int(progress * 100))

        # 단계별 색상 및 텍스트 설정
        stage_config = self._get_stage_config(stage)

        self.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                text-align: center;
                font-size: 10px;
                height: 18px;
            }}
            QProgressBar::chunk {{
                background-color: {stage_config['color']};
                border-radius: 2px;
            }}
        """)

        # 진행률 텍스트 업데이트
        self.setFormat(f"{stage_config['label']} - %p%")

    def _get_stage_config(self, stage: OCRStatusType) -> Dict:
        """단계별 설정"""
        configs = {
            OCRStatusType.IDLE: {
                'label': '대기',
                'color': '#E0E0E0'
            },
            OCRStatusType.INITIALIZING: {
                'label': 'OCR 초기화',
                'color': '#FFC107'
            },
            OCRStatusType.PREPROCESSING: {
                'label': '이미지 전처리',
                'color': '#FF9800'
            },
            OCRStatusType.PROCESSING: {
                'label': 'OCR 처리',
                'color': '#2196F3'
            },
            OCRStatusType.POST_PROCESSING: {
                'label': '텍스트 후처리',
                'color': '#673AB7'
            },
            OCRStatusType.ANALYZING: {
                'label': '품질 분석',
                'color': '#9C27B0'
            },
            OCRStatusType.COMPLETED: {
                'label': 'OCR 완료',
                'color': '#4CAF50'
            },
            OCRStatusType.FAILED: {
                'label': 'OCR 실패',
                'color': '#F44336'
            },
            OCRStatusType.CANCELLED: {
                'label': 'OCR 취소',
                'color': '#795548'
            }
        }

        return configs.get(stage, configs[OCRStatusType.IDLE])


class OCREnhancementTracker:
    """OCR 개선 추적기"""

    def __init__(self):
        self.active_enhancements: List[OCREnhancementType] = []
        self.completed_enhancements: List[OCREnhancementType] = []
        self.start_time: Optional[datetime] = None
        self.estimated_completion: Optional[datetime] = None

    def start_tracking(self, enhancements: List[OCREnhancementType]):
        """추적 시작"""
        self.active_enhancements = enhancements.copy()
        self.completed_enhancements = []
        self.start_time = datetime.now()
        self._estimate_completion_time()

    def complete_enhancement(self, enhancement: OCREnhancementType):
        """개선 완료"""
        if enhancement in self.active_enhancements:
            self.active_enhancements.remove(enhancement)
            self.completed_enhancements.append(enhancement)
            self._update_estimation()

    def get_progress(self) -> float:
        """전체 진행률 반환"""
        total = len(self.active_enhancements) + len(self.completed_enhancements)
        if total == 0:
            return 1.0
        return len(self.completed_enhancements) / total

    def get_remaining_time(self) -> Optional[timedelta]:
        """남은 시간 추정"""
        if not self.estimated_completion:
            return None

        now = datetime.now()
        if now >= self.estimated_completion:
            return timedelta(0)

        return self.estimated_completion - now

    def _estimate_completion_time(self):
        """완료 시간 추정"""
        if not self.start_time:
            return

        # 개선 유형별 예상 처리 시간 (초)
        enhancement_times = {
            OCREnhancementType.ACCURACY_BOOST: 15,
            OCREnhancementType.PREPROCESSING: 5,
            OCREnhancementType.POST_PROCESSING: 8,
            OCREnhancementType.LANGUAGE_DETECTION: 3,
            OCREnhancementType.CONFIDENCE_ANALYSIS: 2,
            OCREnhancementType.LAYOUT_ANALYSIS: 10,
            OCREnhancementType.QUALITY_ASSESSMENT: 5
        }

        total_time = sum(
            enhancement_times.get(enhancement, 10)
            for enhancement in self.active_enhancements
        )

        self.estimated_completion = self.start_time + timedelta(seconds=total_time)

    def _update_estimation(self):
        """추정 시간 업데이트"""
        if not self.start_time or not self.estimated_completion:
            return

        # 완료된 개선의 실제 시간을 기반으로 추정 조정
        elapsed = datetime.now() - self.start_time
        completed_count = len(self.completed_enhancements)
        total_count = completed_count + len(self.active_enhancements)

        if completed_count > 0:
            avg_time_per_enhancement = elapsed.total_seconds() / completed_count
            remaining_time = avg_time_per_enhancement * len(self.active_enhancements)
            self.estimated_completion = datetime.now() + timedelta(seconds=remaining_time)


class OCRProgressTracker(QObject):
    """OCR 진행률 추적기 - ProgressWidget 통합용"""

    # 시그널
    progress_updated = pyqtSignal(str, OCRStatusType, float)  # file_path, stage, progress
    stage_changed = pyqtSignal(str, OCRStatusType, str)      # file_path, stage, description
    enhancement_completed = pyqtSignal(str, OCREnhancementType)  # file_path, enhancement_type
    ocr_completed = pyqtSignal(str, bool, str)               # file_path, success, message

    def __init__(self, config: OCREnhancementConfig):
        super().__init__()
        self.config = config
        self._active_files: Dict[str, OCREnhancementTracker] = {}
        self._progress_cache: Dict[str, OCRProgressInfo] = {}
        self._status_cache: Dict[str, OCRStatusInfo] = {}

        # 업데이트 타이머
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._periodic_update)
        self._update_timer.start(500)  # 0.5초마다 업데이트

        logger.debug("OCRProgressTracker 초기화됨")

    def start_ocr_tracking(self, file_info: FileInfo,
                          enhancements: List[OCREnhancementType]):
        """OCR 추적 시작"""
        file_path = str(file_info.path)

        # 추적기 생성
        tracker = OCREnhancementTracker()
        tracker.start_tracking(enhancements)
        self._active_files[file_path] = tracker

        # 초기 상태 설정
        progress_info = OCRProgressInfo(
            total_steps=len(enhancements) + 1,  # +1 for base OCR
            completed_steps=0,
            current_step_name="OCR 시작",
            enhancement_types=enhancements
        )
        self._progress_cache[file_path] = progress_info

        status_info = OCRStatusInfo(
            status=OCRStatusType.INITIALIZING,
            current_step="OCR 초기화 중"
        )
        self._status_cache[file_path] = status_info

        # 시그널 발송
        self.stage_changed.emit(file_path, OCRStatusType.INITIALIZING, "OCR 초기화 중")
        self.progress_updated.emit(file_path, OCRStatusType.INITIALIZING, 0.0)

        logger.info(f"OCR 추적 시작: {file_info.name} ({len(enhancements)} 개선 적용)")

    def update_ocr_stage(self, file_info: FileInfo, stage: OCRStatusType,
                        progress: float = 0.0, description: str = ""):
        """OCR 단계 업데이트"""
        file_path = str(file_info.path)

        # 상태 정보 업데이트
        if file_path in self._status_cache:
            status_info = self._status_cache[file_path]
            status_info.status = stage
            status_info.current_step = description or self._get_stage_description(stage)
            status_info.progress_percent = progress * 100

            if stage == OCRStatusType.COMPLETED:
                status_info.completed_at = datetime.now()
            elif stage == OCRStatusType.FAILED or stage == OCRStatusType.CANCELLED:
                status_info.completed_at = datetime.now()

        # 진행률 정보 업데이트
        if file_path in self._progress_cache:
            progress_info = self._progress_cache[file_path]
            progress_info.current_step_name = description or self._get_stage_description(stage)
            progress_info.current_step_progress = progress

            # 단계 완료 처리
            if progress >= 1.0 and stage != OCRStatusType.FAILED:
                if progress_info.completed_steps < progress_info.total_steps:
                    progress_info.completed_steps += 1

        # 시그널 발송
        self.stage_changed.emit(file_path, stage, description or self._get_stage_description(stage))
        self.progress_updated.emit(file_path, stage, progress)

        logger.debug(f"OCR 단계 업데이트: {file_info.name} -> {stage.value} ({progress:.1%})")

    def update_enhancement_progress(self, file_info: FileInfo,
                                  enhancement: OCREnhancementType,
                                  completed: bool = False):
        """개선 진행률 업데이트"""
        file_path = str(file_info.path)

        if file_path not in self._active_files:
            return

        tracker = self._active_files[file_path]

        if completed:
            tracker.complete_enhancement(enhancement)
            self.enhancement_completed.emit(file_path, enhancement)
            logger.debug(f"OCR 개선 완료: {file_info.name} -> {enhancement.value}")

        # 전체 진행률 업데이트
        overall_progress = tracker.get_progress()
        self.progress_updated.emit(file_path, OCRStatusType.PROCESSING, overall_progress)

    def complete_ocr_tracking(self, file_info: FileInfo, success: bool = True,
                            message: str = ""):
        """OCR 추적 완료"""
        file_path = str(file_info.path)

        # 최종 상태 설정
        final_stage = OCRStatusType.COMPLETED if success else OCRStatusType.FAILED
        self.update_ocr_stage(file_info, final_stage, 1.0, message)

        # 완료 시그널 발송
        self.ocr_completed.emit(file_path, success, message)

        # 정리
        if file_path in self._active_files:
            del self._active_files[file_path]

        logger.info(f"OCR 추적 완료: {file_info.name} (성공: {success})")

    def cancel_ocr_tracking(self, file_info: FileInfo):
        """OCR 추적 취소"""
        file_path = str(file_info.path)

        self.update_ocr_stage(file_info, OCRStatusType.CANCELLED, 0.0, "사용자가 취소")
        self.complete_ocr_tracking(file_info, False, "사용자가 취소")

    def get_ocr_progress_info(self, file_info: FileInfo) -> Optional[OCRProgressInfo]:
        """OCR 진행률 정보 반환"""
        file_path = str(file_info.path)
        return self._progress_cache.get(file_path)

    def get_ocr_status_info(self, file_info: FileInfo) -> Optional[OCRStatusInfo]:
        """OCR 상태 정보 반환"""
        file_path = str(file_info.path)
        return self._status_cache.get(file_path)

    def get_enhancement_progress(self, file_info: FileInfo) -> float:
        """개선 진행률 반환"""
        file_path = str(file_info.path)
        if file_path not in self._active_files:
            return 0.0

        return self._active_files[file_path].get_progress()

    def get_estimated_remaining_time(self, file_info: FileInfo) -> Optional[str]:
        """예상 남은 시간 반환"""
        file_path = str(file_info.path)
        if file_path not in self._active_files:
            return None

        remaining = self._active_files[file_path].get_remaining_time()
        if not remaining:
            return None

        total_seconds = int(remaining.total_seconds())
        if total_seconds <= 0:
            return "곧 완료"

        minutes, seconds = divmod(total_seconds, 60)
        if minutes > 0:
            return f"{minutes}분 {seconds}초"
        else:
            return f"{seconds}초"

    def create_ocr_progress_summary(self, file_info: FileInfo) -> Dict:
        """OCR 진행률 요약 생성"""
        progress_info = self.get_ocr_progress_info(file_info)
        status_info = self.get_ocr_status_info(file_info)

        if not progress_info or not status_info:
            return {}

        return {
            'stage': status_info.status.value,
            'current_step': status_info.current_step,
            'overall_progress': progress_info.progress_percent,
            'completed_steps': progress_info.completed_steps,
            'total_steps': progress_info.total_steps,
            'elapsed_time': status_info.elapsed_time,
            'estimated_remaining': self.get_estimated_remaining_time(file_info),
            'is_active': status_info.is_active,
            'enhancements': [e.value for e in progress_info.enhancement_types]
        }

    def integrate_with_conversion_progress(self, file_info: FileInfo,
                                         conversion_progress: ConversionProgress):
        """변환 진행률과 통합"""
        ocr_progress = self.get_ocr_progress_info(file_info)
        ocr_status = self.get_ocr_status_info(file_info)

        if not ocr_progress or not ocr_status:
            return conversion_progress

        # OCR 단계를 변환 진행률에 추가
        if ocr_status.is_active:
            # 현재 파일이 OCR 처리 중인 경우
            conversion_progress.current_progress_status = self._map_ocr_to_conversion_status(
                ocr_status.status
            )
            conversion_progress.current_file_progress = ocr_progress.overall_progress

        return conversion_progress

    def clear_tracking_data(self):
        """추적 데이터 정리"""
        self._active_files.clear()
        self._progress_cache.clear()
        self._status_cache.clear()
        logger.debug("OCR 추적 데이터 정리됨")

    def _periodic_update(self):
        """주기적 업데이트"""
        # 활성 파일들의 예상 시간 업데이트
        for file_path, tracker in self._active_files.items():
            if file_path in self._status_cache:
                status_info = self._status_cache[file_path]
                remaining = tracker.get_remaining_time()
                if remaining:
                    status_info.estimated_time_remaining = remaining.total_seconds()

    def _get_stage_description(self, stage: OCRStatusType) -> str:
        """단계별 설명"""
        descriptions = {
            OCRStatusType.IDLE: "대기 중",
            OCRStatusType.INITIALIZING: "OCR 엔진 초기화 중",
            OCRStatusType.PREPROCESSING: "이미지 품질 개선 중",
            OCRStatusType.PROCESSING: "텍스트 추출 중",
            OCRStatusType.POST_PROCESSING: "텍스트 정리 및 보정 중",
            OCRStatusType.ANALYZING: "결과 품질 분석 중",
            OCRStatusType.COMPLETED: "OCR 처리 완료",
            OCRStatusType.FAILED: "OCR 처리 실패",
            OCRStatusType.CANCELLED: "OCR 처리 취소됨"
        }
        return descriptions.get(stage, "알 수 없는 단계")

    def _map_ocr_to_conversion_status(self, ocr_status: OCRStatusType) -> ConversionProgressStatus:
        """OCR 상태를 변환 상태로 매핑"""
        mapping = {
            OCRStatusType.IDLE: ConversionProgressStatus.INITIALIZING,
            OCRStatusType.INITIALIZING: ConversionProgressStatus.VALIDATING_FILE,
            OCRStatusType.PREPROCESSING: ConversionProgressStatus.READING_FILE,
            OCRStatusType.PROCESSING: ConversionProgressStatus.PROCESSING,
            OCRStatusType.POST_PROCESSING: ConversionProgressStatus.PROCESSING,
            OCRStatusType.ANALYZING: ConversionProgressStatus.PROCESSING,
            OCRStatusType.COMPLETED: ConversionProgressStatus.FINALIZING,
            OCRStatusType.FAILED: ConversionProgressStatus.ERROR,
            OCRStatusType.CANCELLED: ConversionProgressStatus.ERROR
        }
        return mapping.get(ocr_status, ConversionProgressStatus.PROCESSING)

    def get_active_files_count(self) -> int:
        """활성 파일 수 반환"""
        return len(self._active_files)

    def get_tracking_stats(self) -> Dict:
        """추적 통계 반환"""
        return {
            'active_files': len(self._active_files),
            'cached_progress': len(self._progress_cache),
            'cached_status': len(self._status_cache),
            'total_enhancements_tracked': sum(
                len(tracker.active_enhancements) + len(tracker.completed_enhancements)
                for tracker in self._active_files.values()
            )
        }