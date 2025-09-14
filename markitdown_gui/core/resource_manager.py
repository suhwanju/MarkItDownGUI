"""
리소스 관리 모듈
임시 파일, 스레드, 메모리 등의 리소스 관리를 담당
"""

import os
import shutil
import threading
import tempfile
import weakref
from pathlib import Path
from typing import List, Set, Optional, Dict, Any
from contextlib import contextmanager
import logging

from .logger import get_logger
from .constants import DEFAULT_MAX_FILE_SIZE_BYTES
from .exceptions import ResourceError, ResourceNotFoundError, InsufficientResourceError

logger = get_logger(__name__)


class TempFileManager:
    """임시 파일 관리자"""
    
    def __init__(self):
        self._temp_files: Set[Path] = set()
        self._temp_dirs: Set[Path] = set()
        self._lock = threading.Lock()
    
    def create_temp_file(self, suffix: str = "", prefix: str = "markitdown_", 
                        dir: Optional[Path] = None) -> Path:
        """
        임시 파일 생성
        
        Args:
            suffix: 파일 확장자
            prefix: 파일 이름 접두사
            dir: 임시 파일을 생성할 디렉토리
        
        Returns:
            생성된 임시 파일 경로
        """
        with self._lock:
            try:
                fd, temp_path = tempfile.mkstemp(
                    suffix=suffix,
                    prefix=prefix,
                    dir=str(dir) if dir else None
                )
                os.close(fd)  # 파일 디스크립터 즉시 닫기
                
                temp_path = Path(temp_path)
                self._temp_files.add(temp_path)
                logger.debug(f"Created temp file: {temp_path}")
                return temp_path
                
            except OSError as e:
                raise ResourceError(f"Failed to create temp file: {e}")
    
    def create_temp_dir(self, prefix: str = "markitdown_",
                       dir: Optional[Path] = None) -> Path:
        """
        임시 디렉토리 생성
        
        Args:
            prefix: 디렉토리 이름 접두사
            dir: 임시 디렉토리를 생성할 부모 디렉토리
        
        Returns:
            생성된 임시 디렉토리 경로
        """
        with self._lock:
            try:
                temp_dir = tempfile.mkdtemp(
                    prefix=prefix,
                    dir=str(dir) if dir else None
                )
                
                temp_dir = Path(temp_dir)
                self._temp_dirs.add(temp_dir)
                logger.debug(f"Created temp dir: {temp_dir}")
                return temp_dir
                
            except OSError as e:
                raise ResourceError(f"Failed to create temp directory: {e}")
    
    def cleanup_file(self, file_path: Path) -> bool:
        """
        임시 파일 정리
        
        Args:
            file_path: 정리할 파일 경로
        
        Returns:
            정리 성공 여부
        """
        with self._lock:
            try:
                if file_path in self._temp_files:
                    if file_path.exists():
                        file_path.unlink()
                    self._temp_files.remove(file_path)
                    logger.debug(f"Cleaned up temp file: {file_path}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to cleanup temp file {file_path}: {e}")
                return False
    
    def cleanup_dir(self, dir_path: Path) -> bool:
        """
        임시 디렉토리 정리
        
        Args:
            dir_path: 정리할 디렉토리 경로
        
        Returns:
            정리 성공 여부
        """
        with self._lock:
            try:
                if dir_path in self._temp_dirs:
                    if dir_path.exists():
                        shutil.rmtree(dir_path)
                    self._temp_dirs.remove(dir_path)
                    logger.debug(f"Cleaned up temp dir: {dir_path}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to cleanup temp directory {dir_path}: {e}")
                return False
    
    def cleanup_all(self):
        """모든 임시 파일/디렉토리 정리"""
        with self._lock:
            # 임시 파일 정리
            for temp_file in list(self._temp_files):
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                    logger.debug(f"Cleaned up temp file: {temp_file}")
                except Exception as e:
                    logger.error(f"Failed to cleanup temp file {temp_file}: {e}")
            
            # 임시 디렉토리 정리
            for temp_dir in list(self._temp_dirs):
                try:
                    if temp_dir.exists():
                        shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temp dir: {temp_dir}")
                except Exception as e:
                    logger.error(f"Failed to cleanup temp directory {temp_dir}: {e}")
            
            self._temp_files.clear()
            self._temp_dirs.clear()
            
            logger.info("All temporary resources cleaned up")
    
    def get_temp_stats(self) -> Dict[str, int]:
        """임시 리소스 통계 반환"""
        with self._lock:
            return {
                "temp_files": len(self._temp_files),
                "temp_dirs": len(self._temp_dirs)
            }


class ThreadManager:
    """스레드 관리자"""
    
    def __init__(self):
        self._active_threads: Dict[str, threading.Thread] = {}
        self._thread_results: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def register_thread(self, thread_id: str, thread: threading.Thread):
        """스레드 등록"""
        with self._lock:
            self._active_threads[thread_id] = thread
            logger.debug(f"Registered thread: {thread_id}")
    
    def unregister_thread(self, thread_id: str) -> bool:
        """스레드 등록 해제"""
        with self._lock:
            if thread_id in self._active_threads:
                del self._active_threads[thread_id]
                logger.debug(f"Unregistered thread: {thread_id}")
                return True
            return False
    
    def is_thread_alive(self, thread_id: str) -> bool:
        """스레드 실행 상태 확인"""
        with self._lock:
            thread = self._active_threads.get(thread_id)
            return thread is not None and thread.is_alive()
    
    def terminate_thread(self, thread_id: str) -> bool:
        """스레드 종료 (graceful)"""
        with self._lock:
            thread = self._active_threads.get(thread_id)
            if thread and thread.is_alive():
                # Note: Python에서는 스레드를 강제로 종료할 수 없으므로
                # 스레드가 자체적으로 종료 신호를 확인하도록 구현해야 함
                logger.warning(f"Cannot force terminate thread: {thread_id}")
                return False
            return True
    
    def cleanup_finished_threads(self):
        """완료된 스레드 정리"""
        with self._lock:
            finished_threads = []
            for thread_id, thread in self._active_threads.items():
                if not thread.is_alive():
                    finished_threads.append(thread_id)
            
            for thread_id in finished_threads:
                del self._active_threads[thread_id]
                logger.debug(f"Cleaned up finished thread: {thread_id}")
    
    def get_active_thread_count(self) -> int:
        """활성 스레드 수 반환"""
        with self._lock:
            return len([t for t in self._active_threads.values() if t.is_alive()])
    
    def cleanup_all(self):
        """모든 스레드 정리"""
        with self._lock:
            # 모든 스레드가 완료될 때까지 대기 (최대 5초)
            for thread_id, thread in self._active_threads.items():
                if thread.is_alive():
                    logger.info(f"Waiting for thread to finish: {thread_id}")
                    thread.join(timeout=5.0)
                    if thread.is_alive():
                        logger.warning(f"Thread did not finish gracefully: {thread_id}")
            
            self._active_threads.clear()
            self._thread_results.clear()
            logger.info("All threads cleaned up")


class MemoryMonitor:
    """메모리 사용량 모니터링"""
    
    def __init__(self, warning_threshold: float = 0.8, critical_threshold: float = 0.9):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
    
    def get_memory_usage(self) -> Dict[str, float]:
        """메모리 사용량 정보 반환"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / (1024 * 1024),
                "vms_mb": memory_info.vms / (1024 * 1024),
                "percent": process.memory_percent()
            }
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
            return {"rss_mb": 0, "vms_mb": 0, "percent": 0}
    
    def check_memory_pressure(self) -> Optional[str]:
        """메모리 압박 상황 확인"""
        usage = self.get_memory_usage()
        percent = usage.get("percent", 0) / 100.0
        
        if percent >= self.critical_threshold:
            return "critical"
        elif percent >= self.warning_threshold:
            return "warning"
        return None


class ResourceManager:
    """통합 리소스 관리자"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.temp_file_manager = TempFileManager()
            self.thread_manager = ThreadManager()
            self.memory_monitor = MemoryMonitor()
            self._cleanup_callbacks: List[callable] = []
            self._initialized = True
            logger.info("Resource manager initialized")
    
    def register_cleanup_callback(self, callback: callable):
        """정리 콜백 등록"""
        self._cleanup_callbacks.append(callback)
        logger.debug(f"Registered cleanup callback: {callback.__name__}")
    
    def cleanup_all(self):
        """모든 리소스 정리"""
        logger.info("Starting global resource cleanup")
        
        # 사용자 정의 콜백 실행
        for callback in self._cleanup_callbacks:
            try:
                callback()
                logger.debug(f"Executed cleanup callback: {callback.__name__}")
            except Exception as e:
                logger.error(f"Error in cleanup callback {callback.__name__}: {e}")
        
        # 각 관리자의 정리 메서드 호출
        self.thread_manager.cleanup_all()
        self.temp_file_manager.cleanup_all()
        
        logger.info("Global resource cleanup completed")
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """리소스 사용 통계"""
        return {
            "temp_files": self.temp_file_manager.get_temp_stats(),
            "active_threads": self.thread_manager.get_active_thread_count(),
            "memory": self.memory_monitor.get_memory_usage(),
            "memory_pressure": self.memory_monitor.check_memory_pressure()
        }
    
    def perform_maintenance(self):
        """정기 유지보수 작업"""
        self.thread_manager.cleanup_finished_threads()
        
        # 메모리 압박 상황 체크
        pressure = self.memory_monitor.check_memory_pressure()
        if pressure == "critical":
            logger.warning("Critical memory pressure detected, forcing cleanup")
            self.temp_file_manager.cleanup_all()
        elif pressure == "warning":
            logger.info("Memory pressure detected, performing maintenance")
            # 선택적 정리 작업 수행


@contextmanager
def temp_file(suffix: str = "", prefix: str = "markitdown_"):
    """임시 파일 컨텍스트 매니저"""
    resource_manager = ResourceManager()
    temp_path = resource_manager.temp_file_manager.create_temp_file(suffix, prefix)
    
    try:
        yield temp_path
    finally:
        resource_manager.temp_file_manager.cleanup_file(temp_path)


@contextmanager
def temp_directory(prefix: str = "markitdown_"):
    """임시 디렉토리 컨텍스트 매니저"""
    resource_manager = ResourceManager()
    temp_dir = resource_manager.temp_file_manager.create_temp_dir(prefix)
    
    try:
        yield temp_dir
    finally:
        resource_manager.temp_file_manager.cleanup_dir(temp_dir)


def register_cleanup_handler():
    """애플리케이션 종료시 정리 핸들러 등록"""
    import atexit
    import signal
    
    resource_manager = ResourceManager()
    
    # 정상 종료시 정리
    atexit.register(resource_manager.cleanup_all)
    
    # 시그널 핸들러 등록 (Unix 시스템)
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, performing cleanup")
        resource_manager.cleanup_all()
    
    try:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    except (AttributeError, ValueError):
        # Windows에서는 일부 시그널이 지원되지 않음
        pass


# 전역 리소스 매니저 인스턴스
resource_manager = ResourceManager()