"""
UI Performance Optimizer
UI 반응성 개선을 위한 성능 최적화 도구
"""

import time
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import logging

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread, QMutex, QMutexLocker, Qt
from PyQt6.QtWidgets import QApplication

from ..core.logger import get_logger


logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


class AsyncTaskManager(QObject):
    """비동기 작업 관리자"""
    
    # 시그널
    task_started = pyqtSignal(str, str)  # task_id, description
    task_progress = pyqtSignal(str, int)  # task_id, progress_percent
    task_completed = pyqtSignal(str, object)  # task_id, result
    task_failed = pyqtSignal(str, str)  # task_id, error_message
    
    def __init__(self, max_workers: int = 4):
        super().__init__()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks: Dict[str, Any] = {}
        self._task_counter = 0
        self._mutex = QMutex()
    
    def submit_task(self, 
                   task_func: Callable,
                   description: str,
                   *args, 
                   **kwargs) -> str:
        """
        비동기 작업 제출
        
        Args:
            task_func: 실행할 함수
            description: 작업 설명
            *args, **kwargs: 함수 인자
            
        Returns:
            작업 ID
        """
        with QMutexLocker(self._mutex):
            self._task_counter += 1
            task_id = f"task_{self._task_counter}"
        
        # 작업 래퍼 함수
        def task_wrapper():
            try:
                logger.debug(f"Starting async task: {task_id} - {description}")
                self.task_started.emit(task_id, description)
                
                # 진행률 콜백 설정
                def progress_callback(percent):
                    self.task_progress.emit(task_id, percent)
                
                # kwargs에 진행률 콜백 추가 (함수가 지원하는 경우)
                if 'progress_callback' in task_func.__code__.co_varnames:
                    kwargs['progress_callback'] = progress_callback
                
                result = task_func(*args, **kwargs)
                
                logger.debug(f"Completed async task: {task_id}")
                self.task_completed.emit(task_id, result)
                
                return result
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed async task: {task_id} - {error_msg}")
                self.task_failed.emit(task_id, error_msg)
                raise
            finally:
                # 완료된 작업 정리
                with QMutexLocker(self._mutex):
                    self.active_tasks.pop(task_id, None)
        
        # 작업 제출
        future = self.executor.submit(task_wrapper)
        self.active_tasks[task_id] = {
            'future': future,
            'description': description,
            'start_time': time.time()
        }
        
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        if task_id not in self.active_tasks:
            return False
        
        future = self.active_tasks[task_id]['future']
        return future.cancel()
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """활성 작업 목록 조회"""
        with QMutexLocker(self._mutex):
            tasks = []
            for task_id, task_info in self.active_tasks.items():
                tasks.append({
                    'task_id': task_id,
                    'description': task_info['description'],
                    'running_time': time.time() - task_info['start_time']
                })
            return tasks
    
    def shutdown(self):
        """작업 관리자 종료"""
        self.executor.shutdown(wait=True)


class UIUpdateThrottler(QObject):
    """UI 업데이트 제한기"""
    
    update_requested = pyqtSignal(object)  # 업데이트 데이터
    
    def __init__(self, update_interval_ms: int = 100, max_batch_size: int = 50):
        super().__init__()
        self.update_interval_ms = update_interval_ms
        self.max_batch_size = max_batch_size
        
        self._pending_updates = []
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._process_pending_updates)
        self._update_timer.setSingleShot(True)
        
        self._mutex = QMutex()
    
    def request_update(self, update_data: Any):
        """UI 업데이트 요청"""
        with QMutexLocker(self._mutex):
            self._pending_updates.append({
                'data': update_data,
                'timestamp': time.time()
            })
            
            # 배치 크기 제한
            if len(self._pending_updates) > self.max_batch_size:
                self._pending_updates = self._pending_updates[-self.max_batch_size:]
            
            # 타이머가 실행 중이 아니면 시작
            if not self._update_timer.isActive():
                self._update_timer.start(self.update_interval_ms)
    
    def _process_pending_updates(self):
        """대기 중인 업데이트 처리"""
        with QMutexLocker(self._mutex):
            if not self._pending_updates:
                return
            
            # 최신 업데이트들만 처리 (중복 제거)
            updates_to_process = self._pending_updates.copy()
            self._pending_updates.clear()
        
        # 업데이트 시그널 발생
        for update in updates_to_process:
            self.update_requested.emit(update['data'])
    
    def flush_updates(self):
        """즉시 모든 업데이트 처리"""
        if self._update_timer.isActive():
            self._update_timer.stop()
        self._process_pending_updates()


class RenderingOptimizer:
    """렌더링 최적화기"""
    
    def __init__(self):
        self.viewport_cache = {}
        self.render_metrics = []
    
    def optimize_widget_rendering(self, widget):
        """위젯 렌더링 최적화"""
        # 더블 버퍼링 활성화
        widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        
        # 불필요한 업데이트 방지
        widget.setUpdatesEnabled(True)
        
        # 최적화된 크기 정책 설정
        if hasattr(widget, 'setSizePolicy'):
            from PyQt6.QtWidgets import QSizePolicy
            widget.setSizePolicy(
                QSizePolicy.Policy.Preferred, 
                QSizePolicy.Policy.Preferred
            )
    
    def batch_widget_updates(self, widgets: List, update_func: Callable):
        """위젯 업데이트 배치 처리"""
        # 업데이트 중 리페인팅 중지
        for widget in widgets:
            widget.setUpdatesEnabled(False)
        
        try:
            # 배치 업데이트 실행
            update_func(widgets)
        finally:
            # 업데이트 재개
            for widget in widgets:
                widget.setUpdatesEnabled(True)
    
    def cache_viewport_data(self, widget, data_key: str, data: Any):
        """뷰포트 데이터 캐싱"""
        widget_id = id(widget)
        if widget_id not in self.viewport_cache:
            self.viewport_cache[widget_id] = {}
        
        self.viewport_cache[widget_id][data_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_cached_viewport_data(self, widget, data_key: str, max_age_seconds: int = 1):
        """캐시된 뷰포트 데이터 조회"""
        widget_id = id(widget)
        if widget_id not in self.viewport_cache:
            return None
        
        cache_entry = self.viewport_cache[widget_id].get(data_key)
        if not cache_entry:
            return None
        
        # 캐시 유효성 검사
        age = time.time() - cache_entry['timestamp']
        if age > max_age_seconds:
            del self.viewport_cache[widget_id][data_key]
            return None
        
        return cache_entry['data']
    
    def clear_widget_cache(self, widget):
        """위젯 캐시 정리"""
        widget_id = id(widget)
        self.viewport_cache.pop(widget_id, None)


class PerformanceMonitor:
    """성능 모니터"""
    
    def __init__(self, max_metrics: int = 1000):
        self.max_metrics = max_metrics
        self.metrics: List[PerformanceMetrics] = []
        self._current_operations: Dict[str, PerformanceMetrics] = {}
        self._mutex = QMutex()
    
    def start_operation(self, operation_name: str) -> str:
        """성능 측정 시작"""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        metric = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time()
        )
        
        with QMutexLocker(self._mutex):
            self._current_operations[operation_id] = metric
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, error_message: str = None):
        """성능 측정 종료"""
        with QMutexLocker(self._mutex):
            if operation_id not in self._current_operations:
                return
            
            metric = self._current_operations.pop(operation_id)
        
        # 측정 완료
        metric.end_time = time.time()
        metric.duration_ms = (metric.end_time - metric.start_time) * 1000
        metric.success = success
        metric.error_message = error_message
        
        # 메모리 사용량 측정 (선택적)
        try:
            import psutil
            process = psutil.Process()
            metric.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        except ImportError:
            pass
        
        # 메트릭 저장
        with QMutexLocker(self._mutex):
            self.metrics.append(metric)
            
            # 메트릭 개수 제한
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
        
        logger.debug(f"Operation completed: {metric.operation_name} - {metric.duration_ms:.1f}ms")
    
    def get_performance_stats(self, operation_name: str = None, 
                            hours: int = 24) -> Dict[str, Any]:
        """성능 통계 조회"""
        cutoff_time = time.time() - (hours * 3600)
        
        with QMutexLocker(self._mutex):
            # 필터링
            filtered_metrics = [
                m for m in self.metrics 
                if m.start_time > cutoff_time and 
                   (operation_name is None or m.operation_name == operation_name)
            ]
        
        if not filtered_metrics:
            return {
                'total_operations': 0,
                'success_rate': 0.0,
                'avg_duration_ms': 0.0,
                'max_duration_ms': 0.0,
                'min_duration_ms': 0.0
            }
        
        successful_ops = [m for m in filtered_metrics if m.success]
        durations = [m.duration_ms for m in filtered_metrics if m.duration_ms is not None]
        
        return {
            'total_operations': len(filtered_metrics),
            'successful_operations': len(successful_ops),
            'success_rate': (len(successful_ops) / len(filtered_metrics)) * 100,
            'avg_duration_ms': sum(durations) / len(durations) if durations else 0.0,
            'max_duration_ms': max(durations) if durations else 0.0,
            'min_duration_ms': min(durations) if durations else 0.0,
            'avg_memory_mb': sum(m.memory_usage_mb for m in filtered_metrics 
                               if m.memory_usage_mb is not None) / len(filtered_metrics)
        }
    
    def get_slow_operations(self, threshold_ms: float = 1000.0) -> List[PerformanceMetrics]:
        """느린 작업 조회"""
        with QMutexLocker(self._mutex):
            return [
                m for m in self.metrics 
                if m.duration_ms and m.duration_ms > threshold_ms
            ]


class ResponsivenessOptimizer(QObject):
    """반응성 최적화기 - 메인 클래스"""
    
    # 시그널
    performance_alert = pyqtSignal(str, float)  # operation_name, duration_ms
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 구성 요소 초기화
        self.async_manager = AsyncTaskManager()
        self.update_throttler = UIUpdateThrottler()
        self.rendering_optimizer = RenderingOptimizer()
        self.performance_monitor = PerformanceMonitor()
        
        # 성능 임계값 설정
        self.slow_operation_threshold_ms = 100.0
        self.very_slow_operation_threshold_ms = 1000.0
        
        # 최적화 설정
        self.enable_update_throttling = True
        self.enable_rendering_optimization = True
        self.enable_performance_monitoring = True
        
        logger.info("ResponsivenessOptimizer initialized")
    
    def optimize_application(self, app: QApplication):
        """애플리케이션 전체 최적화"""
        # Qt 애플리케이션 최적화
        app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_CompressHighFrequencyEvents, True)
        
        # 이벤트 루프 최적화
        app.processEvents()
        
        logger.info("Application optimizations applied")
    
    def optimize_widget(self, widget):
        """위젯 최적화"""
        if self.enable_rendering_optimization:
            self.rendering_optimizer.optimize_widget_rendering(widget)
    
    def execute_async(self, task_func: Callable, description: str, 
                     *args, **kwargs) -> str:
        """비동기 작업 실행"""
        return self.async_manager.submit_task(task_func, description, *args, **kwargs)
    
    def throttled_update(self, update_data: Any):
        """제한된 UI 업데이트"""
        if self.enable_update_throttling:
            self.update_throttler.request_update(update_data)
        else:
            # 직접 업데이트
            self.update_throttler.update_requested.emit(update_data)
    
    def measure_operation(self, operation_name: str):
        """성능 측정 컨텍스트 매니저"""
        class OperationContext:
            def __init__(self, optimizer, name):
                self.optimizer = optimizer
                self.name = name
                self.operation_id = None
            
            def __enter__(self):
                if self.optimizer.enable_performance_monitoring:
                    self.operation_id = self.optimizer.performance_monitor.start_operation(self.name)
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.operation_id:
                    success = exc_type is None
                    error_msg = str(exc_val) if exc_val else None
                    self.optimizer.performance_monitor.end_operation(
                        self.operation_id, success, error_msg
                    )
                    
                    # 느린 작업 경고
                    if success and self.operation_id in self.optimizer.performance_monitor._current_operations:
                        metric = self.optimizer.performance_monitor._current_operations[self.operation_id]
                        if hasattr(metric, 'duration_ms') and metric.duration_ms:
                            if metric.duration_ms > self.optimizer.very_slow_operation_threshold_ms:
                                self.optimizer.performance_alert.emit(self.name, metric.duration_ms)
        
        return OperationContext(self, operation_name)
    
    def get_responsiveness_report(self) -> Dict[str, Any]:
        """반응성 보고서 생성"""
        # 성능 통계 수집
        overall_stats = self.performance_monitor.get_performance_stats()
        slow_operations = self.performance_monitor.get_slow_operations(
            self.slow_operation_threshold_ms
        )
        
        # 활성 작업 정보
        active_tasks = self.async_manager.get_active_tasks()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'performance_stats': overall_stats,
            'slow_operations_count': len(slow_operations),
            'active_async_tasks': len(active_tasks),
            'update_throttling_enabled': self.enable_update_throttling,
            'rendering_optimization_enabled': self.enable_rendering_optimization,
            'performance_monitoring_enabled': self.enable_performance_monitoring,
            'thresholds': {
                'slow_operation_ms': self.slow_operation_threshold_ms,
                'very_slow_operation_ms': self.very_slow_operation_threshold_ms
            },
            'recommendations': self._generate_recommendations(overall_stats, slow_operations)
        }
    
    def _generate_recommendations(self, stats: Dict[str, Any], 
                                slow_ops: List[PerformanceMetrics]) -> List[str]:
        """성능 개선 권장사항 생성"""
        recommendations = []
        
        # 평균 응답 시간 기반 권장사항
        avg_duration = stats.get('avg_duration_ms', 0)
        if avg_duration > 500:
            recommendations.append("평균 작업 시간이 길어 비동기 처리를 고려해보세요")
        
        # 성공률 기반 권장사항  
        success_rate = stats.get('success_rate', 100)
        if success_rate < 95:
            recommendations.append("작업 성공률이 낮아 오류 처리를 개선해보세요")
        
        # 느린 작업 기반 권장사항
        if len(slow_ops) > 10:
            recommendations.append("느린 작업이 많아 성능 최적화가 필요합니다")
        
        # 메모리 사용량 기반 권장사항
        avg_memory = stats.get('avg_memory_mb', 0)
        if avg_memory > 500:
            recommendations.append("메모리 사용량이 높아 메모리 최적화를 고려해보세요")
        
        return recommendations
    
    def cleanup(self):
        """정리 작업"""
        self.async_manager.shutdown()
        self.rendering_optimizer.viewport_cache.clear()
        logger.info("ResponsivenessOptimizer cleaned up")