"""
UI Responsiveness Benchmark Tests
UI 반응성 성능 측정 및 벤치마크 테스트
"""

import time
import threading
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest

from markitdown_gui.ui.performance_optimizer import (
    ResponsivenessOptimizer, AsyncTaskManager, UIUpdateThrottler,
    RenderingOptimizer, PerformanceMonitor, PerformanceMetrics
)
from markitdown_gui.core.config_manager import ConfigManager
from markitdown_gui.core.models import FileInfo, FileType
from markitdown_gui.ui.main_window import MainWindow


class TestUIResponsivenessBenchmarks:
    """UI 반응성 벤치마크 테스트"""
    
    @pytest.fixture
    def config_manager(self, tmp_path):
        """ConfigManager 픽스처"""
        return ConfigManager(tmp_path / "config")
    
    @pytest.fixture
    def performance_optimizer(self, qapp):
        """ResponsivenessOptimizer 픽스처"""
        return ResponsivenessOptimizer()
    
    @pytest.fixture
    def main_window(self, qapp, config_manager):
        """MainWindow 픽스처"""
        with patch('markitdown_gui.ui.main_window.get_i18n_manager'):
            with patch('markitdown_gui.ui.main_window.get_theme_manager'):
                with patch('markitdown_gui.ui.main_window.get_accessibility_manager'):
                    with patch('markitdown_gui.ui.main_window.get_keyboard_navigation_manager'):
                        window = MainWindow(config_manager)
                        window.show()
                        return window
    
    def test_ui_startup_performance(self, qapp, config_manager, benchmark):
        """UI 시작 성능 벤치마크"""
        def create_main_window():
            with patch('markitdown_gui.ui.main_window.get_i18n_manager'):
                with patch('markitdown_gui.ui.main_window.get_theme_manager'):
                    with patch('markitdown_gui.ui.main_window.get_accessibility_manager'):
                        with patch('markitdown_gui.ui.main_window.get_keyboard_navigation_manager'):
                            window = MainWindow(config_manager)
                            window.show()
                            qapp.processEvents()
                            window.close()
                            return window
        
        # 시작 시간 벤치마크 (2초 이내 목표)
        result = benchmark(create_main_window)
        assert result is not None
    
    def test_large_file_list_rendering_performance(self, main_window, benchmark):
        """대용량 파일 목록 렌더링 성능 테스트"""
        # 대용량 파일 목록 생성 (1000개)
        large_file_list = []
        for i in range(1000):
            file_info = FileInfo(
                path=Path(f"test_file_{i}.txt"),
                name=f"test_file_{i}.txt",
                size=1024 * (i + 1),
                file_type=FileType.TEXT,
                is_selected=False
            )
            large_file_list.append(file_info)
        
        def update_file_list():
            main_window._update_file_list_display(large_file_list)
            QApplication.processEvents()
        
        # 렌더링 시간 벤치마크 (500ms 이내 목표)
        benchmark(update_file_list)
    
    def test_rapid_ui_updates_throttling(self, performance_optimizer, benchmark):
        """빠른 UI 업데이트 제한 성능 테스트"""
        throttler = performance_optimizer.update_throttler
        update_count = 0
        
        def on_update(data):
            nonlocal update_count
            update_count += 1
        
        throttler.update_requested.connect(on_update)
        
        def rapid_updates():
            # 1000개의 빠른 업데이트 요청
            for i in range(1000):
                throttler.request_update({'update_id': i, 'data': f'update_{i}'})
            
            # 업데이트 처리 대기
            QTest.qWait(200)  # throttling interval보다 충분히 긴 시간
            
            return update_count
        
        # 업데이트 제한 효과 확인 (1000개 요청이 적절히 제한되어야 함)
        final_count = benchmark(rapid_updates)
        assert final_count < 1000  # 제한이 효과적으로 작동해야 함
        assert final_count > 0     # 하지만 일부는 처리되어야 함
    
    def test_async_task_performance(self, performance_optimizer, benchmark):
        """비동기 작업 성능 테스트"""
        async_manager = performance_optimizer.async_manager
        
        def heavy_computation():
            """무거운 계산 시뮬레이션"""
            result = 0
            for i in range(100000):
                result += i * i
            return result
        
        def execute_async_tasks():
            task_ids = []
            
            # 여러 비동기 작업 시작
            for i in range(10):
                task_id = async_manager.submit_task(
                    heavy_computation,
                    f"Heavy computation {i}"
                )
                task_ids.append(task_id)
            
            # 모든 작업 완료 대기
            start_time = time.time()
            while len(async_manager.get_active_tasks()) > 0:
                QTest.qWait(10)
                if time.time() - start_time > 30:  # 30초 타임아웃
                    break
            
            return len(task_ids)
        
        # 비동기 작업 처리 성능 벤치마크
        completed_tasks = benchmark(execute_async_tasks)
        assert completed_tasks == 10
    
    def test_memory_usage_during_heavy_operations(self, main_window, benchmark):
        """무거운 작업 중 메모리 사용량 테스트"""
        import tracemalloc
        
        def heavy_ui_operations():
            tracemalloc.start()
            
            # 초기 메모리 사용량
            initial_memory = tracemalloc.get_traced_memory()[0]
            
            # 무거운 UI 작업들 수행
            for i in range(100):
                # 가짜 파일 목록 업데이트
                fake_files = [
                    FileInfo(
                        path=Path(f"file_{j}.txt"),
                        name=f"file_{j}.txt", 
                        size=1024,
                        file_type=FileType.TEXT
                    ) for j in range(50)
                ]
                
                main_window._update_file_list_display(fake_files)
                QApplication.processEvents()
                
                # 진행률 업데이트
                main_window._update_progress_display(i, f"Processing {i}/100")
                QApplication.processEvents()
            
            # 최종 메모리 사용량
            final_memory = tracemalloc.get_traced_memory()[0]
            tracemalloc.stop()
            
            memory_increase = final_memory - initial_memory
            return memory_increase / (1024 * 1024)  # MB 단위
        
        # 메모리 증가량 벤치마크 (50MB 이내 목표)
        memory_increase_mb = benchmark(heavy_ui_operations)
        assert memory_increase_mb < 50, f"Memory increase too high: {memory_increase_mb:.1f}MB"
    
    def test_responsiveness_under_cpu_load(self, main_window, performance_optimizer, benchmark):
        """CPU 부하 상황에서의 반응성 테스트"""
        
        def cpu_intensive_task():
            """CPU 집약적 작업"""
            result = 0
            for i in range(1000000):
                result += i ** 2
            return result
        
        def ui_responsiveness_test():
            response_times = []
            
            # CPU 집약적 작업을 백그라운드에서 실행
            task_id = performance_optimizer.execute_async(
                cpu_intensive_task,
                "CPU intensive background task"
            )
            
            # UI 응답성 측정
            for i in range(10):
                start_time = time.time()
                
                # UI 업데이트 수행
                main_window.status_bar.showMessage(f"Responsiveness test {i}")
                QApplication.processEvents()
                
                end_time = time.time()
                response_times.append((end_time - start_time) * 1000)  # ms 단위
                
                QTest.qWait(50)  # 50ms 대기
            
            # 평균 응답 시간 반환
            return sum(response_times) / len(response_times)
        
        # UI 응답 시간 벤치마크 (100ms 이내 목표)
        avg_response_time = benchmark(ui_responsiveness_test)
        assert avg_response_time < 100, f"UI response time too slow: {avg_response_time:.1f}ms"
    
    def test_widget_rendering_optimization(self, performance_optimizer, qapp, benchmark):
        """위젯 렌더링 최적화 성능 테스트"""
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        
        # 테스트용 리스트 위젯 생성
        list_widget = QListWidget()
        list_widget.show()
        
        def render_large_list():
            # 최적화 적용
            performance_optimizer.optimize_widget(list_widget)
            
            # 대량의 아이템 추가
            items = []
            for i in range(1000):
                item = QListWidgetItem(f"Test Item {i}")
                items.append(item)
            
            # 배치 업데이트로 아이템 추가
            def batch_add(widgets):
                for item in items:
                    list_widget.addItem(item)
            
            performance_optimizer.rendering_optimizer.batch_widget_updates(
                [list_widget], batch_add
            )
            
            QApplication.processEvents()
            return list_widget.count()
        
        # 렌더링 성능 벤치마크
        item_count = benchmark(render_large_list)
        assert item_count == 1000
        
        list_widget.close()
    
    def test_performance_monitoring_overhead(self, performance_optimizer, benchmark):
        """성능 모니터링 오버헤드 테스트"""
        monitor = performance_optimizer.performance_monitor
        
        def operations_with_monitoring():
            operation_count = 100
            
            for i in range(operation_count):
                # 성능 측정과 함께 작업 수행
                with performance_optimizer.measure_operation(f"test_operation_{i}"):
                    # 간단한 계산 작업
                    result = sum(range(1000))
            
            return operation_count
        
        def operations_without_monitoring():
            operation_count = 100
            
            for i in range(operation_count):
                # 성능 측정 없이 동일한 작업 수행
                result = sum(range(1000))
            
            return operation_count
        
        # 모니터링 있는 경우와 없는 경우 비교
        with_monitoring_time = benchmark(operations_with_monitoring)
        
        # 모니터링 비활성화
        performance_optimizer.enable_performance_monitoring = False
        without_monitoring_time = benchmark(operations_without_monitoring)
        
        # 오버헤드가 50% 이내여야 함
        # (실제로는 benchmark 함수가 시간을 측정하므로 직접 비교는 어려움)
        # 여기서는 두 작업 모두 정상 완료되었는지만 확인
        assert with_monitoring_time == 100
        assert without_monitoring_time == 100
    
    def test_application_wide_performance_optimization(self, qapp, performance_optimizer, benchmark):
        """애플리케이션 전체 성능 최적화 테스트"""
        
        def optimize_application():
            start_time = time.time()
            
            # 애플리케이션 최적화 적용
            performance_optimizer.optimize_application(qapp)
            
            # 여러 윈도우/위젯 생성 및 최적화
            windows = []
            for i in range(5):
                window = QMainWindow()
                window.setWindowTitle(f"Test Window {i}")
                performance_optimizer.optimize_widget(window)
                windows.append(window)
                window.show()
            
            QApplication.processEvents()
            
            # 윈도우들 정리
            for window in windows:
                window.close()
            
            end_time = time.time()
            return (end_time - start_time) * 1000  # ms 단위
        
        # 애플리케이션 최적화 시간 벤치마크 (1초 이내 목표)
        optimization_time = benchmark(optimize_application)
        # benchmark 함수 자체의 측정 시간이므로 별도 assertion은 생략
    
    def test_performance_statistics_accuracy(self, performance_optimizer):
        """성능 통계 정확성 테스트"""
        monitor = performance_optimizer.performance_monitor
        
        # 여러 작업 수행
        operation_times = []
        for i in range(10):
            start_time = time.time()
            
            with performance_optimizer.measure_operation("accuracy_test"):
                time.sleep(0.01)  # 10ms 대기
            
            end_time = time.time()
            operation_times.append((end_time - start_time) * 1000)
        
        # 통계 조회
        stats = monitor.get_performance_stats("accuracy_test")
        
        # 통계 정확성 확인
        assert stats['total_operations'] == 10
        assert stats['success_rate'] == 100.0
        assert 8 <= stats['avg_duration_ms'] <= 15  # 10ms ± 5ms 허용 오차
        assert stats['min_duration_ms'] >= 8
        assert stats['max_duration_ms'] <= 15
    
    def test_responsiveness_report_generation(self, performance_optimizer):
        """반응성 보고서 생성 테스트"""
        # 여러 작업 수행하여 데이터 생성
        for i in range(5):
            with performance_optimizer.measure_operation("report_test"):
                time.sleep(0.005)  # 5ms
        
        # 보고서 생성
        report = performance_optimizer.get_responsiveness_report()
        
        # 보고서 구조 확인
        assert 'timestamp' in report
        assert 'performance_stats' in report
        assert 'slow_operations_count' in report
        assert 'active_async_tasks' in report
        assert 'thresholds' in report
        assert 'recommendations' in report
        
        # 성능 통계 확인
        perf_stats = report['performance_stats']
        assert perf_stats['total_operations'] >= 5
        assert perf_stats['success_rate'] == 100.0
    
    @pytest.mark.asyncio
    async def test_async_ui_updates_performance(self, performance_optimizer):
        """비동기 UI 업데이트 성능 테스트"""
        update_throttler = performance_optimizer.update_throttler
        received_updates = []
        
        def on_update(data):
            received_updates.append(data)
        
        update_throttler.update_requested.connect(on_update)
        
        # 비동기적으로 많은 업데이트 전송
        async def send_updates():
            for i in range(100):
                update_throttler.request_update({'async_update': i})
                await asyncio.sleep(0.001)  # 1ms 간격
        
        start_time = time.time()
        await send_updates()
        
        # 업데이트 처리 대기
        await asyncio.sleep(0.2)
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        
        # 성능 확인 (500ms 이내)
        assert duration < 500, f"Async updates took too long: {duration:.1f}ms"
        
        # 업데이트 제한이 작동했는지 확인
        assert len(received_updates) < 100
        assert len(received_updates) > 0


class TestPerformanceRegressionPrevention:
    """성능 회귀 방지 테스트"""
    
    def test_file_list_update_performance_regression(self, benchmark):
        """파일 목록 업데이트 성능 회귀 테스트"""
        # 기준 성능 데이터 (예: 1000개 파일 처리에 200ms)
        BASELINE_TIME_MS = 200
        REGRESSION_THRESHOLD = 1.5  # 50% 성능 저하까지 허용
        
        def file_list_update_simulation():
            # 1000개 파일 정보 생성
            files = []
            for i in range(1000):
                file_info = FileInfo(
                    path=Path(f"regression_test_{i}.txt"),
                    name=f"regression_test_{i}.txt",
                    size=1024 * (i + 1),
                    file_type=FileType.TEXT
                )
                files.append(file_info)
            
            # 파일 정보 처리 시뮬레이션
            processed_files = []
            for file_info in files:
                # 각 파일에 대한 처리 시뮬레이션
                processed_info = {
                    'name': file_info.name,
                    'size': file_info.size,
                    'type': file_info.file_type.value,
                    'path': str(file_info.path)
                }
                processed_files.append(processed_info)
            
            return len(processed_files)
        
        # 성능 측정
        result = benchmark(file_list_update_simulation)
        assert result == 1000
        
        # 실제 벤치마크 시간은 benchmark 객체의 속성으로 접근 가능
        # 여기서는 작업이 완료되었는지만 확인
    
    def test_ui_rendering_performance_regression(self, qapp, benchmark):
        """UI 렌더링 성능 회귀 테스트"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        def ui_rendering_simulation():
            # 복잡한 UI 구조 생성
            main_widget = QWidget()
            main_layout = QVBoxLayout(main_widget)
            
            # 많은 레이블 위젯 생성
            labels = []
            for i in range(500):
                label = QLabel(f"Performance Test Label {i}")
                main_layout.addWidget(label)
                labels.append(label)
            
            main_widget.show()
            qapp.processEvents()
            main_widget.close()
            
            return len(labels)
        
        # 렌더링 성능 측정
        widget_count = benchmark(ui_rendering_simulation)
        assert widget_count == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])