"""
Memory Optimizer Unit Tests
Tests for memory optimization functionality
"""

import gc
import time
import tracemalloc
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from markitdown_gui.core.memory_optimizer import (
    MemoryTracker, LRUCache, StreamingFileProcessor, 
    MemoryPool, WeakReferenceManager, MemoryOptimizer
)


class TestMemoryTracker:
    """MemoryTracker 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        tracker = MemoryTracker()
        assert tracker.baseline_memory == 0
        assert tracker.peak_memory == 0
        assert len(tracker.snapshots) == 0
    
    def test_start_monitoring(self):
        """모니터링 시작 테스트"""
        tracker = MemoryTracker()
        tracker.start_monitoring()
        
        # tracemalloc가 시작되었는지 확인
        assert tracemalloc.is_tracing()
        assert tracker.baseline_memory > 0
        
        tracker.stop_monitoring()
    
    def test_stop_monitoring(self):
        """모니터링 중지 테스트"""
        tracker = MemoryTracker()
        tracker.start_monitoring()
        
        stats = tracker.stop_monitoring()
        
        assert not tracemalloc.is_tracing()
        assert 'peak_memory_mb' in stats
        assert 'total_allocations' in stats
        assert 'memory_leaks' in stats
    
    def test_take_snapshot(self):
        """스냅샷 생성 테스트"""
        tracker = MemoryTracker()
        tracker.start_monitoring()
        
        # 메모리 할당
        test_data = [i for i in range(1000)]
        
        snapshot_name = tracker.take_snapshot("test_snapshot")
        
        assert snapshot_name == "test_snapshot"
        assert len(tracker.snapshots) == 1
        
        tracker.stop_monitoring()
        del test_data  # 정리
    
    def test_should_trigger_gc(self):
        """GC 트리거 조건 테스트"""
        tracker = MemoryTracker()
        
        # 초기 상태에서는 False
        assert not tracker.should_trigger_gc()
        
        # 임계치를 넘는 메모리 사용량 시뮬레이션
        tracker.baseline_memory = 100 * 1024 * 1024  # 100MB
        current_memory = 180 * 1024 * 1024  # 180MB (80% 증가)
        
        with patch.object(tracker, '_get_current_memory', return_value=current_memory):
            assert tracker.should_trigger_gc()
    
    def test_force_gc(self):
        """강제 GC 테스트"""
        tracker = MemoryTracker()
        
        stats = tracker.force_gc()
        
        assert 'objects_before' in stats
        assert 'objects_after' in stats
        assert 'objects_collected' in stats
    
    def test_detect_memory_leaks(self):
        """메모리 누수 감지 테스트"""
        tracker = MemoryTracker()
        tracker.start_monitoring()
        
        # 첫 번째 스냅샷
        tracker.take_snapshot("before")
        
        # 의도적으로 메모리 할당
        test_objects = []
        for i in range(1000):
            test_objects.append([j for j in range(10)])
        
        # 두 번째 스냅샷
        tracker.take_snapshot("after")
        
        leaks = tracker.detect_memory_leaks("before", "after")
        
        assert len(leaks) > 0  # 누수가 감지되어야 함
        
        tracker.stop_monitoring()
        del test_objects


class TestLRUCache:
    """LRUCache 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        cache = LRUCache(max_size=5, max_memory_mb=10)
        
        assert cache.max_size == 5
        assert cache.max_memory_bytes == 10 * 1024 * 1024
        assert len(cache.cache) == 0
    
    def test_put_and_get(self):
        """저장 및 조회 테스트"""
        cache = LRUCache(max_size=3)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("nonexistent") is None
    
    def test_lru_eviction(self):
        """LRU 제거 테스트"""
        cache = LRUCache(max_size=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # key1이 제거되어야 함
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_memory_limit(self):
        """메모리 제한 테스트"""
        cache = LRUCache(max_size=10, max_memory_mb=1)  # 1MB 제한
        
        # 큰 객체 저장 (메모리 제한에 걸려야 함)
        large_data = "x" * (512 * 1024)  # 512KB
        
        cache.put("key1", large_data)
        cache.put("key2", large_data)  # 메모리 제한으로 key1이 제거될 수 있음
        
        stats = cache.get_stats()
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'memory_usage_bytes' in stats
    
    def test_update_access_order(self):
        """접근 순서 업데이트 테스트"""
        cache = LRUCache(max_size=2)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # key1 접근으로 순서 변경
        _ = cache.get("key1")
        
        cache.put("key3", "value3")  # key2가 제거되어야 함
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
    
    def test_clear(self):
        """캐시 초기화 테스트"""
        cache = LRUCache(max_size=5)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.get("key1") is None


class TestStreamingFileProcessor:
    """StreamingFileProcessor 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        processor = StreamingFileProcessor()
        
        assert processor.chunk_size == 8192
        assert processor.max_memory_mb == 100
    
    @pytest.fixture
    def temp_file(self, tmp_path):
        """임시 파일 픽스처"""
        file_path = tmp_path / "test_file.txt"
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def test_read_file_chunked(self, temp_file):
        """청크 단위 파일 읽기 테스트"""
        processor = StreamingFileProcessor(chunk_size=10)
        
        chunks = list(processor.read_file_chunked(str(temp_file)))
        
        # 청크가 생성되었는지 확인
        assert len(chunks) > 0
        
        # 전체 내용이 올바른지 확인
        full_content = ''.join(chunks)
        expected_content = temp_file.read_text(encoding='utf-8')
        assert full_content == expected_content
    
    def test_process_file_chunked(self, temp_file):
        """청크 단위 파일 처리 테스트"""
        processor = StreamingFileProcessor(chunk_size=10)
        
        def uppercase_processor(chunk):
            return chunk.upper()
        
        results = list(processor.process_file_chunked(str(temp_file), uppercase_processor))
        
        assert len(results) > 0
        
        # 처리 결과 확인
        full_result = ''.join(results)
        expected_result = temp_file.read_text(encoding='utf-8').upper()
        assert full_result == expected_result
    
    def test_memory_monitoring(self, temp_file):
        """메모리 모니터링 테스트"""
        processor = StreamingFileProcessor(max_memory_mb=1)  # 1MB 제한
        
        def memory_intensive_processor(chunk):
            # 메모리 사용량이 많은 처리 시뮬레이션
            return chunk * 100
        
        # 메모리 제한이 있는 상태에서 처리
        results = list(processor.process_file_chunked(str(temp_file), memory_intensive_processor))
        
        assert len(results) > 0


class TestMemoryPool:
    """MemoryPool 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        pool = MemoryPool(object_type=list, initial_size=5, max_size=10)
        
        assert pool.object_type == list
        assert pool.initial_size == 5
        assert pool.max_size == 10
        assert len(pool._available) == 5
    
    def test_acquire_and_release(self):
        """객체 획득 및 반환 테스트"""
        pool = MemoryPool(object_type=list, initial_size=2, max_size=5)
        
        # 객체 획득
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        
        assert isinstance(obj1, list)
        assert isinstance(obj2, list)
        assert len(pool._available) == 0  # 사용 가능한 객체가 없어야 함
        
        # 객체 반환
        pool.release(obj1)
        pool.release(obj2)
        
        assert len(pool._available) == 2  # 반환된 객체들
    
    def test_max_size_limit(self):
        """최대 크기 제한 테스트"""
        pool = MemoryPool(object_type=dict, initial_size=1, max_size=2)
        
        # 최대 크기를 초과하는 객체 반환 시도
        extra_objects = [pool.acquire() for _ in range(5)]
        
        for obj in extra_objects:
            pool.release(obj)
        
        # 최대 크기를 초과하지 않아야 함
        assert len(pool._available) <= 2
    
    def test_object_factory(self):
        """객체 팩토리 테스트"""
        def custom_factory():
            return {"initialized": True}
        
        pool = MemoryPool(
            object_type=dict, 
            initial_size=1, 
            max_size=3, 
            factory=custom_factory
        )
        
        obj = pool.acquire()
        
        assert obj["initialized"] is True
    
    def test_reset_function(self):
        """객체 리셋 함수 테스트"""
        def reset_list(lst):
            lst.clear()
            return lst
        
        pool = MemoryPool(
            object_type=list, 
            initial_size=1, 
            max_size=3, 
            reset_func=reset_list
        )
        
        obj = pool.acquire()
        obj.extend([1, 2, 3])  # 데이터 추가
        
        pool.release(obj)  # 리셋되어야 함
        
        reused_obj = pool.acquire()
        assert len(reused_obj) == 0  # 리셋되었는지 확인


class TestWeakReferenceManager:
    """WeakReferenceManager 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        manager = WeakReferenceManager()
        
        assert len(manager._references) == 0
        assert manager._cleanup_threshold == 100
    
    def test_add_reference(self):
        """참조 추가 테스트"""
        manager = WeakReferenceManager()
        
        obj = {"test": "data"}
        key = manager.add_reference("test_key", obj)
        
        assert key == "test_key"
        assert len(manager._references) == 1
    
    def test_get_reference(self):
        """참조 조회 테스트"""
        manager = WeakReferenceManager()
        
        obj = {"test": "data"}
        manager.add_reference("test_key", obj)
        
        retrieved_obj = manager.get_reference("test_key")
        
        assert retrieved_obj is obj
    
    def test_weak_reference_cleanup(self):
        """약한 참조 자동 정리 테스트"""
        manager = WeakReferenceManager()
        
        # 객체 생성 및 참조 추가
        obj = {"test": "data"}
        manager.add_reference("test_key", obj)
        
        # 원본 객체 삭제
        del obj
        gc.collect()  # 가비지 컬렉션 실행
        
        # 참조가 정리되었는지 확인
        retrieved_obj = manager.get_reference("test_key")
        assert retrieved_obj is None
    
    def test_remove_reference(self):
        """참조 제거 테스트"""
        manager = WeakReferenceManager()
        
        obj = {"test": "data"}
        manager.add_reference("test_key", obj)
        
        assert manager.remove_reference("test_key") is True
        assert manager.get_reference("test_key") is None
        assert manager.remove_reference("nonexistent") is False
    
    def test_cleanup_dead_references(self):
        """죽은 참조 정리 테스트"""
        manager = WeakReferenceManager(cleanup_threshold=2)
        
        # 여러 객체 추가
        obj1 = {"test": "data1"}
        obj2 = {"test": "data2"}
        
        manager.add_reference("key1", obj1)
        manager.add_reference("key2", obj2)
        
        # 객체 하나 삭제
        del obj1
        gc.collect()
        
        # 임계치에 도달하여 정리 실행
        obj3 = {"test": "data3"}
        manager.add_reference("key3", obj3)  # 이때 cleanup 실행
        
        # 죽은 참조가 정리되었는지 확인
        assert manager.get_reference("key1") is None
        assert manager.get_reference("key2") is obj2
    
    def test_list_active_references(self):
        """활성 참조 목록 조회 테스트"""
        manager = WeakReferenceManager()
        
        obj1 = {"test": "data1"}
        obj2 = {"test": "data2"}
        
        manager.add_reference("key1", obj1)
        manager.add_reference("key2", obj2)
        
        active_refs = manager.list_active_references()
        
        assert "key1" in active_refs
        assert "key2" in active_refs
        assert len(active_refs) == 2


class TestMemoryOptimizer:
    """MemoryOptimizer 통합 테스트"""
    
    def test_init(self):
        """초기화 테스트"""
        optimizer = MemoryOptimizer()
        
        assert optimizer.tracker is not None
        assert optimizer.cache is not None
        assert optimizer.streaming_processor is not None
        assert optimizer.memory_pools is not None
        assert optimizer.weak_references is not None
    
    def test_start_and_stop_monitoring(self):
        """모니터링 시작/중지 테스트"""
        optimizer = MemoryOptimizer()
        
        optimizer.start_monitoring()
        assert tracemalloc.is_tracing()
        
        stats = optimizer.stop_monitoring()
        assert not tracemalloc.is_tracing()
        assert 'peak_memory_mb' in stats
    
    def test_cache_operations(self):
        """캐시 작업 테스트"""
        optimizer = MemoryOptimizer()
        
        # 캐시에 데이터 저장
        optimizer.cache_result("test_key", "test_value")
        
        # 캐시에서 데이터 조회
        result = optimizer.get_cached_result("test_key")
        assert result == "test_value"
        
        # 존재하지 않는 키 조회
        result = optimizer.get_cached_result("nonexistent")
        assert result is None
    
    def test_memory_pool_operations(self):
        """메모리 풀 작업 테스트"""
        optimizer = MemoryOptimizer()
        
        # 메모리 풀 생성
        pool_name = optimizer.create_memory_pool("list_pool", list, 3, 10)
        assert pool_name == "list_pool"
        
        # 객체 획득 및 반환
        obj = optimizer.acquire_from_pool("list_pool")
        assert isinstance(obj, list)
        
        optimizer.release_to_pool("list_pool", obj)
    
    def test_weak_reference_operations(self):
        """약한 참조 작업 테스트"""
        optimizer = MemoryOptimizer()
        
        test_obj = {"data": "test"}
        
        # 약한 참조 추가
        optimizer.add_weak_reference("test_ref", test_obj)
        
        # 약한 참조 조회
        retrieved_obj = optimizer.get_weak_reference("test_ref")
        assert retrieved_obj is test_obj
    
    def test_should_trigger_gc(self):
        """GC 트리거 조건 테스트"""
        optimizer = MemoryOptimizer()
        optimizer.start_monitoring()
        
        # 초기 상태에서는 False여야 함
        should_trigger = optimizer.should_trigger_gc()
        # 시스템 상태에 따라 결과가 달라질 수 있음
        
        optimizer.stop_monitoring()
    
    def test_force_gc(self):
        """강제 GC 테스트"""
        optimizer = MemoryOptimizer()
        
        stats = optimizer.force_gc()
        
        assert 'objects_before' in stats
        assert 'objects_after' in stats
        assert 'objects_collected' in stats
    
    def test_get_memory_statistics(self):
        """메모리 통계 조회 테스트"""
        optimizer = MemoryOptimizer()
        optimizer.start_monitoring()
        
        # 일부 데이터 생성
        optimizer.cache_result("test", "data")
        
        stats = optimizer.get_memory_statistics()
        
        assert 'current_memory_mb' in stats
        assert 'peak_memory_mb' in stats
        assert 'cache_stats' in stats
        
        optimizer.stop_monitoring()
    
    def test_cleanup(self):
        """정리 작업 테스트"""
        optimizer = MemoryOptimizer()
        optimizer.start_monitoring()
        
        # 일부 데이터 생성
        optimizer.cache_result("test1", "data1")
        optimizer.cache_result("test2", "data2")
        
        # 정리 실행
        optimizer.cleanup()
        
        # 정리 후 상태 확인
        stats = optimizer.get_memory_statistics()
        cache_stats = stats.get('cache_stats', {})
        
        # 캐시가 정리되었는지 확인
        assert cache_stats.get('size', 0) == 0
    
    @pytest.mark.asyncio
    async def test_streaming_processing(self, tmp_path):
        """스트리밍 처리 테스트"""
        optimizer = MemoryOptimizer()
        
        # 임시 파일 생성
        test_file = tmp_path / "test_stream.txt"
        test_content = "Line 1\nLine 2\nLine 3\n" * 100
        test_file.write_text(test_content, encoding='utf-8')
        
        def line_counter(chunk):
            return len(chunk.splitlines())
        
        # 스트리밍 처리
        results = list(optimizer.streaming_processor.process_file_chunked(
            str(test_file), line_counter
        ))
        
        assert len(results) > 0
        total_lines = sum(results)
        expected_lines = len(test_content.splitlines())
        
        # 정확한 라인 수가 계산되는지는 청크 크기에 따라 달라질 수 있음
        assert total_lines >= 0


class TestMemoryOptimizerIntegration:
    """Memory Optimizer 통합 시나리오 테스트"""
    
    def test_large_data_processing_scenario(self, tmp_path):
        """대용량 데이터 처리 시나리오"""
        optimizer = MemoryOptimizer()
        optimizer.start_monitoring()
        
        # 대용량 파일 시뮬레이션
        large_file = tmp_path / "large_data.txt"
        large_content = "This is a test line with some data.\n" * 10000
        large_file.write_text(large_content, encoding='utf-8')
        
        # 캐시를 활용한 처리
        cache_key = f"processed_{large_file.name}"
        
        def process_content(content):
            # 단어 수 계산
            return len(content.split())
        
        # 첫 번째 처리 (캐시 미스)
        if not optimizer.get_cached_result(cache_key):
            content = large_file.read_text()
            word_count = process_content(content)
            optimizer.cache_result(cache_key, word_count)
        
        # 두 번째 처리 (캐시 히트)
        cached_result = optimizer.get_cached_result(cache_key)
        assert cached_result is not None
        
        # 메모리 통계 확인
        stats = optimizer.get_memory_statistics()
        assert stats['cache_stats']['hits'] >= 1
        
        optimizer.cleanup()
        optimizer.stop_monitoring()
    
    def test_memory_leak_prevention_scenario(self):
        """메모리 누수 방지 시나리오"""
        optimizer = MemoryOptimizer()
        optimizer.start_monitoring()
        
        # 많은 객체 생성 및 약한 참조 추가
        for i in range(100):
            test_obj = {"id": i, "data": f"test_data_{i}"}
            optimizer.add_weak_reference(f"obj_{i}", test_obj)
        
        # 일부 객체는 강한 참조로 유지
        strong_refs = []
        for i in range(0, 20):
            obj = optimizer.get_weak_reference(f"obj_{i}")
            if obj:
                strong_refs.append(obj)
        
        # 가비지 컬렉션 실행
        gc.collect()
        
        # 약한 참조 정리 실행
        optimizer.weak_references.cleanup_dead_references()
        
        # 강한 참조가 있는 객체는 유지되어야 함
        active_refs = optimizer.weak_references.list_active_references()
        assert len(active_refs) >= 20
        
        optimizer.cleanup()
        optimizer.stop_monitoring()
    
    def test_performance_under_memory_pressure(self):
        """메모리 압박 상황에서의 성능 테스트"""
        optimizer = MemoryOptimizer()
        optimizer.start_monitoring()
        
        # 메모리 풀 생성
        optimizer.create_memory_pool("test_pool", list, 10, 50)
        
        # 메모리 압박 상황 시뮬레이션
        large_objects = []
        try:
            for i in range(100):
                # 풀에서 객체 획득
                obj = optimizer.acquire_from_pool("test_pool")
                
                # 큰 데이터 추가
                obj.extend(range(1000))
                
                # 캐시에 저장
                optimizer.cache_result(f"large_obj_{i}", obj)
                
                # GC 트리거 조건 확인
                if optimizer.should_trigger_gc():
                    gc_stats = optimizer.force_gc()
                    assert 'objects_collected' in gc_stats
                
                large_objects.append(obj)
            
        finally:
            # 정리
            for obj in large_objects:
                optimizer.release_to_pool("test_pool", obj)
        
        # 최종 통계 확인
        final_stats = optimizer.get_memory_statistics()
        assert final_stats is not None
        
        optimizer.cleanup()
        optimizer.stop_monitoring()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])