"""
Screen Reader Support System
ARIA-equivalent announcements and live regions for PyQt6 applications
"""

import json
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Union
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time

from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QDialog, QLabel, QTextEdit,
    QPushButton, QCheckBox, QComboBox, QLineEdit, QProgressBar,
    QSlider, QTabWidget, QGroupBox, QListWidget, QTreeWidget, QTableWidget
)
from PyQt6.QtCore import (
    QObject, pyqtSignal, QSettings, QTimer, Qt, QThread, QMutex,
    QWaitCondition, QMutexLocker
)
# Import accessibility classes from compatibility layer
from .qt_compatibility import QAccessible, QAccessibleInterface, QAccessibleEvent, is_accessibility_available

from .logger import get_logger


logger = get_logger(__name__)


class AnnouncementPriority(Enum):
    """알림 우선순위"""
    POLITE = "polite"        # 현재 읽기 완료 후 알림
    ASSERTIVE = "assertive"  # 현재 읽기 중단하고 즉시 알림
    OFF = "off"              # 알림 안함


class LiveRegionType(Enum):
    """라이브 리전 타입"""
    LOG = "log"              # 로그 메시지
    STATUS = "status"        # 상태 정보
    ALERT = "alert"          # 경고 메시지
    MARQUEE = "marquee"      # 스크롤 텍스트
    TIMER = "timer"          # 시간 정보


@dataclass
class Announcement:
    """알림 메시지"""
    message: str
    priority: AnnouncementPriority
    timestamp: float = field(default_factory=time.time)
    widget: Optional[QWidget] = None
    context: str = ""
    language: str = "ko"
    
    def __post_init__(self):
        # 메시지 정리 및 유효성 검사
        self.message = self.message.strip()
        if not self.message:
            raise ValueError("Empty announcement message")


@dataclass
class LiveRegion:
    """라이브 리전"""
    widget: QWidget
    region_type: LiveRegionType
    priority: AnnouncementPriority
    atomic: bool = False  # 전체 내용 읽기 여부
    relevant: Set[str] = field(default_factory=lambda: {"text", "additions"})
    busy: bool = False
    label: str = ""


class ScreenReaderAPI(ABC):
    """스크린 리더 API 추상 클래스"""
    
    @abstractmethod
    def announce(self, message: str, priority: AnnouncementPriority) -> bool:
        """메시지 알림"""
        pass
    
    @abstractmethod
    def stop_speech(self) -> bool:
        """음성 중지"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """스크린 리더 사용 가능 여부"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """스크린 리더 이름"""
        pass


class WindowsScreenReader(ScreenReaderAPI):
    """Windows 스크린 리더 (NVDA, JAWS, Narrator 지원)"""
    
    def __init__(self):
        self.system = platform.system()
        self.available_readers = self._detect_screen_readers()
    
    def _detect_screen_readers(self) -> List[str]:
        """설치된 스크린 리더 감지"""
        readers = []
        
        if self.system != "Windows":
            return readers
        
        try:
            # NVDA 감지 (여러 경로 확인)
            nvda_paths = [
                "C:/Program Files (x86)/NVDA/nvda.exe",
                "C:/Program Files/NVDA/nvda.exe",
                "C:/NVDA/nvda.exe"
            ]
            for nvda_path in nvda_paths:
                try:
                    if Path(nvda_path).exists():
                        readers.append("NVDA")
                        break
                except (OSError, PermissionError):
                    continue
            
            # JAWS 감지 (여러 버전 확인)
            jaws_paths = [
                "C:/Program Files/Freedom Scientific/JAWS",
                "C:/Program Files (x86)/Freedom Scientific/JAWS"
            ]
            for jaws_path in jaws_paths:
                try:
                    if Path(jaws_path).exists():
                        readers.append("JAWS")
                        break
                except (OSError, PermissionError):
                    continue
            
            # Narrator는 Windows 10+ 기본 탑재
            try:
                release = platform.release()
                if release in ["10", "11"] or (release.isdigit() and int(release) >= 10):
                    readers.append("Narrator")
            except (ValueError, AttributeError):
                # Fallback: assume modern Windows has Narrator
                readers.append("Narrator")
            
        except Exception as e:
            logger.warning(f"Error detecting screen readers: {e}")
        
        return readers
    
    def announce(self, message: str, priority: AnnouncementPriority) -> bool:
        """Windows 스크린 리더에 메시지 알림"""
        try:
            if not self.available_readers:
                return False
            
            # SAPI (Speech API) 사용
            if self._announce_via_sapi(message, priority):
                return True
            
            # UI Automation 사용
            if self._announce_via_uiautomation(message, priority):
                return True
            
            # 접근성 이벤트 발생
            return self._announce_via_accessibility_event(message, priority)
            
        except Exception as e:
            logger.error(f"Error announcing to Windows screen reader: {e}")
            return False
    
    def _announce_via_sapi(self, message: str, priority: AnnouncementPriority) -> bool:
        """SAPI를 통한 알림"""
        try:
            # 메시지 정리 및 이스케이프 처리
            escaped_message = message.replace('"', '""').replace('\n', ' ').replace('\r', '').strip()[:500]  # 길이 제한
            if not escaped_message:
                return False
                
            cmd = f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{escaped_message}")'
            
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                timeout=5,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.debug(f"SAPI announcement failed: {e}")
            return False
    
    def _announce_via_uiautomation(self, message: str, priority: AnnouncementPriority) -> bool:
        """UI Automation을 통한 알림"""
        try:
            # Windows UI Automation을 통한 접근성 이벤트 발생
            # 실제 구현에서는 win32com 또는 ctypes 사용
            return False
            
        except Exception as e:
            logger.debug(f"UI Automation announcement failed: {e}")
            return False
    
    def _announce_via_accessibility_event(self, message: str, priority: AnnouncementPriority) -> bool:
        """접근성 이벤트를 통한 알림"""
        if not is_accessibility_available():
            logger.debug("Accessibility not available, skipping event announcement")
            return False
            
        try:
            # Qt 접근성 이벤트 발생
            event = QAccessibleEvent(QAccessible.Event.NameChanged, None, -1)
            event.setValue(message)
            QAccessible.updateAccessibility(event)
            return True
            
        except Exception as e:
            logger.debug(f"Accessibility event announcement failed: {e}")
            return False
    
    def stop_speech(self) -> bool:
        """음성 중지"""
        try:
            # SAPI 음성 중지
            cmd = 'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.SpeakAsyncCancelAll()'
            
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                timeout=2,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
            return False
    
    def is_available(self) -> bool:
        """스크린 리더 사용 가능 여부"""
        return len(self.available_readers) > 0
    
    def get_name(self) -> str:
        """사용 가능한 스크린 리더 이름"""
        if self.available_readers:
            return ", ".join(self.available_readers)
        return "None"


class LinuxScreenReader(ScreenReaderAPI):
    """Linux 스크린 리더 (Orca, espeak 지원)"""
    
    def __init__(self):
        self.system = platform.system()
        self.available_readers = self._detect_screen_readers()
    
    def _detect_screen_readers(self) -> List[str]:
        """설치된 스크린 리더 감지"""
        readers = []
        
        if self.system != "Linux":
            return readers
        
        try:
            # Orca 감지
            if subprocess.run(["which", "orca"], capture_output=True).returncode == 0:
                readers.append("Orca")
            
            # espeak 감지
            if subprocess.run(["which", "espeak"], capture_output=True).returncode == 0:
                readers.append("espeak")
            
            # speech-dispatcher 감지
            if subprocess.run(["which", "spd-say"], capture_output=True).returncode == 0:
                readers.append("speech-dispatcher")
            
        except Exception as e:
            logger.warning(f"Error detecting Linux screen readers: {e}")
        
        return readers
    
    def announce(self, message: str, priority: AnnouncementPriority) -> bool:
        """Linux 스크린 리더에 메시지 알림"""
        try:
            # speech-dispatcher 시도
            if "speech-dispatcher" in self.available_readers:
                if self._announce_via_spd(message, priority):
                    return True
            
            # espeak 시도
            if "espeak" in self.available_readers:
                if self._announce_via_espeak(message, priority):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error announcing to Linux screen reader: {e}")
            return False
    
    def _announce_via_spd(self, message: str, priority: AnnouncementPriority) -> bool:
        """speech-dispatcher를 통한 알림"""
        try:
            priority_map = {
                AnnouncementPriority.POLITE: "text",
                AnnouncementPriority.ASSERTIVE: "message",
                AnnouncementPriority.OFF: "text"
            }
            
            spd_priority = priority_map.get(priority, "text")
            
            result = subprocess.run(
                ["spd-say", "-t", spd_priority, message],
                capture_output=True,
                timeout=5
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.debug(f"speech-dispatcher announcement failed: {e}")
            return False
    
    def _announce_via_espeak(self, message: str, priority: AnnouncementPriority) -> bool:
        """espeak을 통한 알림"""
        try:
            # 우선순위에 따라 기존 음성 중지 여부 결정
            args = ["espeak"]
            if priority == AnnouncementPriority.ASSERTIVE:
                # 기존 음성 중지하고 즉시 재생
                subprocess.run(["killall", "espeak"], capture_output=True)
            
            args.extend(["-s", "150", message])  # 속도 150wpm
            
            result = subprocess.run(args, capture_output=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            logger.debug(f"espeak announcement failed: {e}")
            return False
    
    def stop_speech(self) -> bool:
        """음성 중지"""
        try:
            # speech-dispatcher 중지
            subprocess.run(["spd-say", "-S"], capture_output=True, timeout=2)
            
            # espeak 프로세스 중지
            subprocess.run(["killall", "espeak"], capture_output=True, timeout=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Linux speech: {e}")
            return False
    
    def is_available(self) -> bool:
        """스크린 리더 사용 가능 여부"""
        return len(self.available_readers) > 0
    
    def get_name(self) -> str:
        """사용 가능한 스크린 리더 이름"""
        if self.available_readers:
            return ", ".join(self.available_readers)
        return "None"


class MacOSScreenReader(ScreenReaderAPI):
    """macOS 스크린 리더 (VoiceOver 지원)"""
    
    def __init__(self):
        self.system = platform.system()
        self.voiceover_available = self._detect_voiceover()
    
    def _detect_voiceover(self) -> bool:
        """VoiceOver 감지"""
        if self.system != "Darwin":
            return False
        
        try:
            # VoiceOver 실행 상태 확인
            result = subprocess.run([
                "osascript", "-e",
                "tell application \"System Events\" to get (value of attribute \"AXVoiceOverEnabled\" of application process \"System Events\")"
            ], capture_output=True, text=True)
            
            return result.returncode == 0 and "true" in result.stdout.lower()
            
        except Exception as e:
            logger.warning(f"Error detecting VoiceOver: {e}")
            return False
    
    def announce(self, message: str, priority: AnnouncementPriority) -> bool:
        """VoiceOver에 메시지 알림"""
        try:
            if not self.voiceover_available:
                return self._announce_via_say(message, priority)
            
            # VoiceOver API 사용 (AppleScript)
            script = f'''
            tell application "System Events"
                set voiceOverEnabled to (value of attribute "AXVoiceOverEnabled" of application process "System Events")
                if voiceOverEnabled then
                    set announcement to "{message}"
                    do shell script "osascript -e 'tell application \\"System Events\\" to set the contents of the clipboard to \\"" & announcement & "\\"'"
                    key code 9 using {{command down}}
                end if
            end tell
            '''
            
            result = subprocess.run([
                "osascript", "-e", script
            ], capture_output=True, timeout=5)
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error announcing to VoiceOver: {e}")
            return False
    
    def _announce_via_say(self, message: str, priority: AnnouncementPriority) -> bool:
        """say 명령어를 통한 TTS"""
        try:
            args = ["say"]
            
            # 우선순위에 따른 옵션
            if priority == AnnouncementPriority.ASSERTIVE:
                # 기존 음성 중지
                subprocess.run(["killall", "say"], capture_output=True)
            
            args.extend(["-r", "200", message])  # 속도 200wpm
            
            result = subprocess.run(args, capture_output=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            logger.debug(f"say command failed: {e}")
            return False
    
    def stop_speech(self) -> bool:
        """음성 중지"""
        try:
            subprocess.run(["killall", "say"], capture_output=True, timeout=2)
            return True
        except Exception as e:
            logger.error(f"Error stopping macOS speech: {e}")
            return False
    
    def is_available(self) -> bool:
        """스크린 리더 사용 가능 여부"""
        return self.voiceover_available or self.system == "Darwin"
    
    def get_name(self) -> str:
        """스크린 리더 이름"""
        if self.voiceover_available:
            return "VoiceOver"
        elif self.system == "Darwin":
            return "macOS TTS"
        return "None"


class AnnouncementQueue:
    """알림 메시지 큐"""
    
    def __init__(self, max_size: int = 100):
        self.queue = []
        self.max_size = max(1, max_size)  # 최소 1개 보장
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.processing = False
        self._shutdown = False
    
    def enqueue(self, announcement: Announcement):
        """알림 메시지 큐에 추가"""
        with QMutexLocker(self.mutex):
            if self._shutdown:
                return False
                
            # 입력 검증
            if not announcement or not announcement.message.strip():
                return False
                
            # 우선순위가 높은 메시지는 기존 큐 비우기
            if announcement.priority == AnnouncementPriority.ASSERTIVE:
                self.queue.clear()
            
            # 큐 크기 제한
            while len(self.queue) >= self.max_size:
                self.queue.pop(0)
            
            self.queue.append(announcement)
            self.condition.wakeOne()
            return True
    
    def dequeue(self) -> Optional[Announcement]:
        """알림 메시지 큐에서 제거"""
        with QMutexLocker(self.mutex):
            if self._shutdown:
                return None
            if self.queue:
                return self.queue.pop(0)
            return None
    
    def wait_for_announcement(self, timeout: int = 1000) -> bool:
        """새로운 알림 메시지 대기"""
        with QMutexLocker(self.mutex):
            if self._shutdown:
                return False
            if not self.queue:
                return self.condition.wait(self.mutex, timeout)
            return True
    
    def clear(self):
        """큐 비우기"""
        with QMutexLocker(self.mutex):
            self.queue.clear()
    
    def shutdown(self):
        """큐 종료 준비"""
        with QMutexLocker(self.mutex):
            self._shutdown = True
            self.queue.clear()
            self.condition.wakeAll()  # 대기 중인 모든 스레드 깨우기
    
    def size(self) -> int:
        """큐 크기 반환"""
        with QMutexLocker(self.mutex):
            return len(self.queue)


class AnnouncementWorker(QThread):
    """알림 메시지 처리 워커 스레드"""
    
    def __init__(self, screen_reader_api: ScreenReaderAPI, announcement_queue: AnnouncementQueue):
        super().__init__()
        self.screen_reader_api = screen_reader_api
        self.announcement_queue = announcement_queue
        self.running = True
        self.paused = False
    
    def run(self):
        """워커 스레드 실행"""
        consecutive_failures = 0
        max_failures = 10
        
        while self.running:
            try:
                if self.paused:
                    self.msleep(100)
                    continue
                
                # 연속 실패가 너무 많으면 잠시 대기
                if consecutive_failures >= max_failures:
                    logger.warning(f"Too many consecutive failures ({consecutive_failures}), pausing for 5 seconds")
                    self.msleep(5000)
                    consecutive_failures = 0
                    continue
                
                if self.announcement_queue.wait_for_announcement(1000):
                    announcement = self.announcement_queue.dequeue()
                    if announcement and announcement.priority != AnnouncementPriority.OFF:
                        try:
                            # 메시지 유효성 검사
                            if not announcement.message or not announcement.message.strip():
                                consecutive_failures = 0  # 유효하지 않은 메시지는 실패로 카운트하지 않음
                                continue
                            
                            success = self.screen_reader_api.announce(
                                announcement.message.strip(), 
                                announcement.priority
                            )
                            
                            if success:
                                consecutive_failures = 0
                            else:
                                consecutive_failures += 1
                                logger.debug(f"Failed to announce: {announcement.message[:50]}...")
                                
                        except Exception as e:
                            consecutive_failures += 1
                            logger.error(f"Error announcing message: {e}")
                            
                        # 메시지 간격 조절 (너무 빠른 연속 알림 방지)
                        self.msleep(50)
                        
            except Exception as e:
                logger.error(f"Critical error in announcement worker: {e}")
                consecutive_failures += 1
                self.msleep(1000)  # 1초 대기 후 계속
    
    def stop(self):
        """워커 중지"""
        self.running = False
        
        # 큐 종료 시그널 보내기
        if hasattr(self.announcement_queue, 'shutdown'):
            self.announcement_queue.shutdown()
            
        # 스레드 정리
        if self.isRunning():
            self.quit()
            if not self.wait(5000):  # 5초 대기
                logger.warning("Announcement worker did not stop gracefully, terminating")
                self.terminate()
                self.wait(2000)  # 추가 2초 대기
    
    def pause(self):
        """워커 일시정지"""
        self.paused = True
    
    def resume(self):
        """워커 재개"""
        self.paused = False


class LiveRegionManager:
    """라이브 리전 관리자"""
    
    def __init__(self, screen_reader_bridge):
        self.screen_reader_bridge = screen_reader_bridge
        self.live_regions: Dict[QWidget, LiveRegion] = {}
        self.content_cache: Dict[QWidget, str] = {}
        
        # 라이브 리전 모니터링 타이머
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_live_regions)
        self.monitor_timer.setInterval(1000)  # 1초마다 체크 (성능 개선)
        
        # 변경 감지 최적화
        self.last_check_time = 0
        self.min_check_interval = 250  # 최소 250ms 간격
    
    def initialize(self) -> bool:
        """라이브 리전 매니저 초기화"""
        try:
            self.monitor_timer.start()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize live region manager: {e}")
            return False
    
    def register_live_region(self, widget: QWidget, 
                           region_type: LiveRegionType = LiveRegionType.LOG,
                           priority: AnnouncementPriority = AnnouncementPriority.POLITE,
                           atomic: bool = False,
                           label: str = "") -> bool:
        """라이브 리전 등록"""
        try:
            live_region = LiveRegion(
                widget=widget,
                region_type=region_type,
                priority=priority,
                atomic=atomic,
                label=label
            )
            
            self.live_regions[widget] = live_region
            
            # 초기 콘텐츠 캐시
            self.content_cache[widget] = self._get_widget_content(widget)
            
            logger.debug(f"Live region registered: {widget.__class__.__name__} ({region_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register live region: {e}")
            return False
    
    def unregister_live_region(self, widget: QWidget):
        """라이브 리전 등록 해제"""
        try:
            if widget in self.live_regions:
                del self.live_regions[widget]
            if widget in self.content_cache:
                del self.content_cache[widget]
            
            logger.debug("Live region unregistered")
            
        except Exception as e:
            logger.error(f"Failed to unregister live region: {e}")
    
    def _monitor_live_regions(self):
        """라이브 리전 모니터링"""
        try:
            current_time = time.time() * 1000
            
            # 최소 간격 체크
            if current_time - self.last_check_time < self.min_check_interval:
                return
                
            self.last_check_time = current_time
            
            # 활성화된 리전만 체크 (성능 최적화)
            active_regions = [
                (widget, live_region) for widget, live_region in self.live_regions.items()
                if not live_region.busy and widget.isVisible() and widget.isEnabled()
            ]
            
            for widget, live_region in active_regions:
                try:
                    current_content = self._get_widget_content(widget)
                    cached_content = self.content_cache.get(widget, "")
                    
                    if current_content != cached_content:
                        self._handle_content_change(widget, live_region, current_content, cached_content)
                        self.content_cache[widget] = current_content
                        
                except Exception as e:
                    logger.debug(f"Error checking widget {widget.__class__.__name__}: {e}")
        
        except Exception as e:
            logger.error(f"Error monitoring live regions: {e}")
    
    def _get_widget_content(self, widget: QWidget) -> str:
        """위젯의 텍스트 콘텐츠 추출"""
        try:
            if isinstance(widget, QLabel):
                return widget.text()
            elif isinstance(widget, QTextEdit):
                return widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                return widget.text()
            elif isinstance(widget, QProgressBar):
                return f"진행률 {widget.value()}%"
            elif hasattr(widget, 'text'):
                return widget.text()
            else:
                return widget.accessibleName() or widget.objectName() or ""
                
        except Exception as e:
            logger.debug(f"Error getting widget content: {e}")
            return ""
    
    def _handle_content_change(self, widget: QWidget, live_region: LiveRegion, 
                             new_content: str, old_content: str):
        """콘텐츠 변경 처리"""
        try:
            # 변경 내용 분석
            if "additions" in live_region.relevant:
                # 추가된 내용만 알림
                if len(new_content) > len(old_content):
                    added_content = new_content[len(old_content):]
                    message = self._format_live_region_message(live_region, added_content)
                    self.screen_reader_bridge._enqueue_announcement(message, live_region.priority, widget)
            
            elif "text" in live_region.relevant:
                # 전체 내용 알림
                if live_region.atomic:
                    message = self._format_live_region_message(live_region, new_content)
                else:
                    message = self._format_live_region_message(live_region, new_content)
                
                self.screen_reader_bridge._enqueue_announcement(message, live_region.priority, widget)
        
        except Exception as e:
            logger.error(f"Error handling content change: {e}")
    
    def _format_live_region_message(self, live_region: LiveRegion, content: str) -> str:
        """라이브 리전 메시지 포맷팅"""
        try:
            if live_region.label:
                return f"{live_region.label}: {content}"
            
            region_labels = {
                LiveRegionType.LOG: "로그",
                LiveRegionType.STATUS: "상태",
                LiveRegionType.ALERT: "알림",
                LiveRegionType.MARQUEE: "",
                LiveRegionType.TIMER: "시간"
            }
            
            label = region_labels.get(live_region.region_type, "")
            if label:
                return f"{label}: {content}"
            else:
                return content
                
        except Exception as e:
            logger.error(f"Error formatting live region message: {e}")
            return content
    
    def cleanup(self):
        """정리"""
        try:
            self.monitor_timer.stop()
            self.live_regions.clear()
            self.content_cache.clear()
        except Exception as e:
            logger.error(f"Error cleaning up live region manager: {e}")


class ScreenReaderBridge(QObject):
    """스크린 리더 브리지 - 메인 인터페이스"""
    
    # 시그널
    announcement_sent = pyqtSignal(str, str)  # message, priority
    screen_reader_detected = pyqtSignal(str)   # reader_name
    
    def __init__(self, accessibility_manager=None):
        super().__init__()
        
        self.accessibility_manager = accessibility_manager
        self.settings = QSettings()
        
        # 플랫폼별 스크린 리더 API
        self.screen_reader_apis: List[ScreenReaderAPI] = []
        self.current_api: Optional[ScreenReaderAPI] = None
        
        # 알림 시스템
        self.announcement_queue = AnnouncementQueue()
        self.announcement_worker: Optional[AnnouncementWorker] = None
        
        # 라이브 리전 매니저
        self.live_region_manager = LiveRegionManager(self)
        
        # 설정
        self.enabled = True
        self.announcement_delay = 0  # 알림 지연 시간 (ms)
        self.max_message_length = 500  # 최대 메시지 길이
        
        # 상태
        self.last_announcement_time = 0
        self.speech_rate = 200  # WPM
    
    def initialize(self) -> bool:
        """스크린 리더 브리지 초기화"""
        try:
            # 플랫폼별 API 초기화
            self._initialize_screen_reader_apis()
            
            # 사용 가능한 API 선택
            self._select_best_api()
            
            if not self.current_api:
                logger.warning("No screen reader API available")
                return False
            
            # 알림 워커 시작
            self._start_announcement_worker()
            
            # 라이브 리전 매니저 초기화
            self.live_region_manager.initialize()
            
            # 설정 로드
            self._load_settings()
            
            logger.info(f"Screen reader bridge initialized with {self.current_api.get_name()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize screen reader bridge: {e}")
            return False
    
    def _initialize_screen_reader_apis(self):
        """플랫폼별 스크린 리더 API 초기화"""
        try:
            system = platform.system()
            
            if system == "Windows":
                self.screen_reader_apis.append(WindowsScreenReader())
            elif system == "Linux":
                self.screen_reader_apis.append(LinuxScreenReader())
            elif system == "Darwin":  # macOS
                self.screen_reader_apis.append(MacOSScreenReader())
            
        except Exception as e:
            logger.error(f"Error initializing screen reader APIs: {e}")
    
    def _select_best_api(self):
        """최적의 스크린 리더 API 선택"""
        try:
            for api in self.screen_reader_apis:
                if api.is_available():
                    self.current_api = api
                    self.screen_reader_detected.emit(api.get_name())
                    return
            
            logger.warning("No available screen reader API found")
            
        except Exception as e:
            logger.error(f"Error selecting screen reader API: {e}")
    
    def _start_announcement_worker(self):
        """알림 워커 시작"""
        try:
            if self.current_api and not self.announcement_worker:
                self.announcement_worker = AnnouncementWorker(
                    self.current_api, 
                    self.announcement_queue
                )
                self.announcement_worker.start()
                
        except Exception as e:
            logger.error(f"Error starting announcement worker: {e}")
    
    def announce(self, message: str, priority: str = "polite", 
                widget: QWidget = None, context: str = "") -> bool:
        """
        스크린 리더에 메시지 알림
        
        Args:
            message: 알림 메시지
            priority: 우선순위 ("polite", "assertive", "off")
            widget: 관련 위젯
            context: 컨텍스트 정보
            
        Returns:
            성공 여부
        """
        try:
            if not self.enabled or not message.strip():
                return False
            
            # 우선순위 변환
            try:
                priority_enum = AnnouncementPriority(priority.lower())
            except ValueError:
                priority_enum = AnnouncementPriority.POLITE
            
            # 메시지 길이 제한
            if len(message) > self.max_message_length:
                message = message[:self.max_message_length] + "..."
            
            # 알림 객체 생성
            announcement = Announcement(
                message=message,
                priority=priority_enum,
                widget=widget,
                context=context
            )
            
            # 지연 시간 적용
            if self.announcement_delay > 0:
                current_time = time.time() * 1000
                if current_time - self.last_announcement_time < self.announcement_delay:
                    return False
            
            # 큐에 추가
            self._enqueue_announcement(message, priority_enum, widget)
            
            self.last_announcement_time = time.time() * 1000
            return True
            
        except Exception as e:
            logger.error(f"Error announcing message: {e}")
            return False
    
    def _enqueue_announcement(self, message: str, priority: AnnouncementPriority, widget: QWidget = None):
        """알림을 큐에 추가"""
        try:
            announcement = Announcement(
                message=message,
                priority=priority,
                widget=widget
            )
            
            self.announcement_queue.enqueue(announcement)
            self.announcement_sent.emit(message, priority.value)
            
        except Exception as e:
            logger.error(f"Error enqueueing announcement: {e}")
    
    def stop_speech(self) -> bool:
        """음성 출력 중지"""
        try:
            if self.current_api:
                return self.current_api.stop_speech()
            return False
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
            return False
    
    def set_speech_rate(self, rate: int):
        """음성 속도 설정 (WPM)"""
        try:
            if 50 <= rate <= 400:
                self.speech_rate = rate
                self.settings.setValue("screen_reader/speech_rate", rate)
        except Exception as e:
            logger.error(f"Error setting speech rate: {e}")
    
    def set_enabled(self, enabled: bool):
        """스크린 리더 지원 활성화/비활성화"""
        try:
            self.enabled = enabled
            if self.announcement_worker:
                if enabled:
                    self.announcement_worker.resume()
                else:
                    self.announcement_worker.pause()
            
            self.settings.setValue("screen_reader/enabled", enabled)
            logger.info(f"Screen reader support {'enabled' if enabled else 'disabled'}")
            
        except Exception as e:
            logger.error(f"Error setting screen reader enabled state: {e}")
    
    def set_announcement_delay(self, delay_ms: int):
        """알림 지연 시간 설정"""
        try:
            if 0 <= delay_ms <= 5000:
                self.announcement_delay = delay_ms
                self.settings.setValue("screen_reader/announcement_delay", delay_ms)
        except Exception as e:
            logger.error(f"Error setting announcement delay: {e}")
    
    def get_screen_reader_info(self) -> Dict[str, Any]:
        """스크린 리더 정보 반환"""
        try:
            return {
                "available": self.current_api is not None,
                "name": self.current_api.get_name() if self.current_api else "None",
                "platform": platform.system(),
                "enabled": self.enabled,
                "speech_rate": self.speech_rate,
                "announcement_delay": self.announcement_delay,
                "queue_size": self.announcement_queue.size(),
                "apis_count": len(self.screen_reader_apis)
            }
        except Exception as e:
            logger.error(f"Error getting screen reader info: {e}")
            return {}
    
    def register_live_region(self, widget: QWidget, **kwargs) -> bool:
        """라이브 리전 등록 (편의 메서드)"""
        return self.live_region_manager.register_live_region(widget, **kwargs)
    
    def unregister_live_region(self, widget: QWidget):
        """라이브 리전 등록 해제 (편의 메서드)"""
        self.live_region_manager.unregister_live_region(widget)
    
    def _load_settings(self):
        """설정 로드"""
        try:
            self.enabled = self.settings.value("screen_reader/enabled", True, type=bool)
            self.speech_rate = self.settings.value("screen_reader/speech_rate", 200, type=int)
            self.announcement_delay = self.settings.value("screen_reader/announcement_delay", 0, type=int)
            
        except Exception as e:
            logger.error(f"Error loading screen reader settings: {e}")
    
    def save_settings(self):
        """설정 저장"""
        try:
            self.settings.setValue("screen_reader/enabled", self.enabled)
            self.settings.setValue("screen_reader/speech_rate", self.speech_rate)
            self.settings.setValue("screen_reader/announcement_delay", self.announcement_delay)
            self.settings.sync()
            
        except Exception as e:
            logger.error(f"Error saving screen reader settings: {e}")
    
    def cleanup(self):
        """정리"""
        try:
            # 알림 워커 중지
            if self.announcement_worker:
                try:
                    self.announcement_worker.stop()
                    if self.announcement_worker.isRunning():
                        self.announcement_worker.wait(3000)  # 3초 대기
                    if self.announcement_worker.isRunning():
                        self.announcement_worker.terminate()  # 강제 종료
                        self.announcement_worker.wait(1000)
                except Exception as e:
                    logger.debug(f"Error stopping announcement worker: {e}")
                finally:
                    self.announcement_worker = None
            
            # 라이브 리전 매니저 정리
            if hasattr(self, 'live_region_manager') and self.live_region_manager:
                try:
                    self.live_region_manager.cleanup()
                except Exception as e:
                    logger.debug(f"Error cleaning up live region manager: {e}")
                self.live_region_manager = None
            
            # 알림 큐 비우기
            try:
                if hasattr(self, 'announcement_queue'):
                    self.announcement_queue.clear()
            except Exception as e:
                logger.debug(f"Error clearing announcement queue: {e}")
            
            # API 정리
            self.screen_reader_apis.clear()
            self.current_api = None
            
            # 설정 저장
            try:
                self.save_settings()
            except Exception as e:
                logger.debug(f"Error saving settings during cleanup: {e}")
            
            logger.info("Screen reader bridge cleaned up")
            
        except Exception as e:
            logger.error(f"Error during screen reader bridge cleanup: {e}")


def create_screen_reader_bridge(accessibility_manager=None) -> ScreenReaderBridge:
    """스크린 리더 브리지 생성"""
    return ScreenReaderBridge(accessibility_manager)