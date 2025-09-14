"""
Memory optimization utilities and management
"""

import gc
import weakref
import tracemalloc
import threading
from typing import Dict, List, Optional, Any, Callable, Generator
from functools import wraps
from collections import OrderedDict
import psutil
import time
from pathlib import Path

from .logger import get_logger

logger = get_logger(__name__)


class MemoryTracker:
    """Track memory usage and detect leaks"""
    
    def __init__(self):
        self.baseline_memory = 0
        self.peak_memory = 0
        self.allocations = []
        self.monitoring_enabled = False
        self._lock = threading.Lock()
    
    def start_monitoring(self):
        """Start memory monitoring"""
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        
        self.baseline_memory = self._get_current_memory()
        self.peak_memory = self.baseline_memory
        self.monitoring_enabled = True
        self.allocations.clear()
        
        logger.debug(f"Memory monitoring started. Baseline: {self._format_bytes(self.baseline_memory)}")
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return statistics"""
        if not self.monitoring_enabled:
            return {}
        
        current_memory = self._get_current_memory()
        
        # Get tracemalloc statistics if available
        traced_current = 0
        traced_peak = 0
        if tracemalloc.is_tracing():
            traced_current, traced_peak = tracemalloc.get_traced_memory()
        
        stats = {
            'baseline_memory': self.baseline_memory,
            'current_memory': current_memory,
            'peak_memory': self.peak_memory,
            'memory_increase': current_memory - self.baseline_memory,
            'traced_current': traced_current,
            'traced_peak': traced_peak,
            'allocations_tracked': len(self.allocations)
        }
        
        self.monitoring_enabled = False
        logger.debug(f"Memory monitoring stopped. Stats: {stats}")
        
        return stats
    
    def checkpoint(self, name: str) -> Dict[str, Any]:
        """Create a memory checkpoint"""
        if not self.monitoring_enabled:
            return {}
        
        current_memory = self._get_current_memory()
        self.peak_memory = max(self.peak_memory, current_memory)
        
        checkpoint_data = {
            'name': name,
            'timestamp': time.time(),
            'memory_usage': current_memory,
            'memory_increase': current_memory - self.baseline_memory
        }
        
        with self._lock:
            self.allocations.append(checkpoint_data)
        
        logger.debug(f"Memory checkpoint '{name}': {self._format_bytes(current_memory)}")
        
        return checkpoint_data
    
    def _get_current_memory(self) -> int:
        """Get current process memory usage"""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception:
            return 0
    
    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes as human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"
    
    def get_memory_report(self) -> str:
        """Generate a memory usage report"""
        if not self.monitoring_enabled and not self.allocations:
            return "Memory monitoring not active"
        
        current_memory = self._get_current_memory()
        
        report = [
            "Memory Usage Report",
            "=" * 50,
            f"Baseline Memory: {self._format_bytes(self.baseline_memory)}",
            f"Current Memory: {self._format_bytes(current_memory)}",
            f"Peak Memory: {self._format_bytes(self.peak_memory)}",
            f"Memory Increase: {self._format_bytes(current_memory - self.baseline_memory)}",
            ""
        ]
        
        if self.allocations:
            report.append("Checkpoints:")
            for allocation in self.allocations[-10:]:  # Show last 10
                report.append(
                    f"  {allocation['name']}: {self._format_bytes(allocation['memory_usage'])} "
                    f"(+{self._format_bytes(allocation['memory_increase'])})"
                )
        
        return "\n".join(report)


class LRUCache:
    """Memory-efficient LRU cache implementation"""
    
    def __init__(self, max_size: int = 128, max_memory_mb: int = 50):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache = OrderedDict()
        self._memory_usage = 0
        self._lock = threading.RLock()
    
    def get(self, key: Any) -> Any:
        """Get item from cache"""
        with self._lock:
            if key in self._cache:
                # Move to end (most recent)
                value = self._cache.pop(key)
                self._cache[key] = value
                return value
            return None
    
    def set(self, key: Any, value: Any):
        """Set item in cache"""
        with self._lock:
            # Estimate memory usage
            item_size = self._estimate_size(value)
            
            # Remove existing item if present
            if key in self._cache:
                old_value = self._cache.pop(key)
                self._memory_usage -= self._estimate_size(old_value)
            
            # Check memory limit
            while (self._memory_usage + item_size > self.max_memory_bytes or
                   len(self._cache) >= self.max_size):
                if not self._cache:
                    break
                
                # Remove oldest item
                oldest_key, oldest_value = self._cache.popitem(last=False)
                self._memory_usage -= self._estimate_size(oldest_value)
            
            # Add new item
            self._cache[key] = value
            self._memory_usage += item_size
    
    def clear(self):
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()
            self._memory_usage = 0
    
    def _estimate_size(self, obj: Any) -> int:
        """Estimate memory size of object"""
        try:
            # Simple estimation based on type
            if isinstance(obj, str):
                return len(obj.encode('utf-8'))
            elif isinstance(obj, (bytes, bytearray)):
                return len(obj)
            elif isinstance(obj, (list, tuple)):
                return sum(self._estimate_size(item) for item in obj)
            elif isinstance(obj, dict):
                return sum(self._estimate_size(k) + self._estimate_size(v) 
                          for k, v in obj.items())
            else:
                return 1024  # Default estimate
        except Exception:
            return 1024  # Fallback estimate
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage': self._memory_usage,
                'max_memory': self.max_memory_bytes,
                'memory_utilization': self._memory_usage / self.max_memory_bytes * 100
            }


class StreamingFileProcessor:
    """Process files in chunks to reduce memory usage"""
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        self.chunk_size = chunk_size
        self.memory_tracker = MemoryTracker()
    
    def process_file_chunked(self, file_path: str, processor_func: Callable) -> Generator[Any, None, None]:
        """Process file in chunks"""
        self.memory_tracker.start_monitoring()
        
        try:
            file_path_obj = Path(file_path)
            file_size = file_path_obj.stat().st_size
            
            logger.debug(f"Processing file {file_path} ({file_size} bytes) in {self.chunk_size} byte chunks")
            
            with open(file_path_obj, 'rb') as file:
                chunk_count = 0
                
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    chunk_count += 1
                    self.memory_tracker.checkpoint(f"chunk_{chunk_count}")
                    
                    # Process chunk and yield result
                    try:
                        result = processor_func(chunk, chunk_count == 1)  # First chunk flag
                        if result is not None:
                            yield result
                    finally:
                        # Ensure chunk is dereferenced
                        del chunk
                        
                        # Force garbage collection every 10 chunks
                        if chunk_count % 10 == 0:
                            gc.collect()
                            
            logger.debug(f"Processed {chunk_count} chunks from {file_path}")
            
        finally:
            stats = self.memory_tracker.stop_monitoring()
            logger.debug(f"File processing memory stats: {stats}")
    
    def process_text_file_lines(self, file_path: str, line_processor: Callable) -> Generator[str, None, None]:
        """Process text file line by line"""
        self.memory_tracker.start_monitoring()
        
        try:
            with open(file_path, 'r', encoding='utf-8', buffering=8192) as file:
                line_count = 0
                
                for line in file:
                    line_count += 1
                    
                    if line_count % 1000 == 0:
                        self.memory_tracker.checkpoint(f"line_{line_count}")
                    
                    # Process line
                    processed_line = line_processor(line.rstrip('\n\r'))
                    if processed_line is not None:
                        yield processed_line
                    
                    # Periodic cleanup
                    if line_count % 5000 == 0:
                        gc.collect()
                        
                logger.debug(f"Processed {line_count} lines from {file_path}")
                
        finally:
            stats = self.memory_tracker.stop_monitoring()
            logger.debug(f"Line processing memory stats: {stats}")


class MemoryPool:
    """Object pool to reduce frequent allocations"""
    
    def __init__(self, factory: Callable, max_size: int = 10):
        self.factory = factory
        self.max_size = max_size
        self._pool = []
        self._lock = threading.Lock()
    
    def acquire(self) -> Any:
        """Acquire object from pool"""
        with self._lock:
            if self._pool:
                return self._pool.pop()
            else:
                return self.factory()
    
    def release(self, obj: Any):
        """Return object to pool"""
        with self._lock:
            if len(self._pool) < self.max_size:
                # Reset object if it has a reset method
                if hasattr(obj, 'reset'):
                    obj.reset()
                self._pool.append(obj)
    
    def clear(self):
        """Clear the pool"""
        with self._lock:
            self._pool.clear()


class WeakReferenceManager:
    """Manage weak references to prevent memory leaks"""
    
    def __init__(self):
        self._refs = set()
        self._callbacks = {}
        self._lock = threading.Lock()
    
    def add_reference(self, obj: Any, callback: Optional[Callable] = None) -> weakref.ReferenceType:
        """Add weak reference with optional cleanup callback"""
        def cleanup_callback(ref):
            with self._lock:
                self._refs.discard(ref)
                if ref in self._callbacks:
                    try:
                        self._callbacks[ref]()
                    except Exception as e:
                        logger.warning(f"Error in weak reference callback: {e}")
                    finally:
                        del self._callbacks[ref]
        
        weak_ref = weakref.ref(obj, cleanup_callback)
        
        with self._lock:
            self._refs.add(weak_ref)
            if callback:
                self._callbacks[weak_ref] = callback
        
        return weak_ref
    
    def cleanup_dead_references(self):
        """Manually cleanup dead references"""
        with self._lock:
            dead_refs = {ref for ref in self._refs if ref() is None}
            for ref in dead_refs:
                self._refs.discard(ref)
                self._callbacks.pop(ref, None)
        
        return len(dead_refs)
    
    def get_stats(self) -> Dict[str, int]:
        """Get reference statistics"""
        with self._lock:
            live_refs = sum(1 for ref in self._refs if ref() is not None)
            dead_refs = len(self._refs) - live_refs
            
            return {
                'total_references': len(self._refs),
                'live_references': live_refs,
                'dead_references': dead_refs,
                'callbacks_registered': len(self._callbacks)
            }


def memory_efficient_decorator(func: Callable) -> Callable:
    """Decorator to make functions more memory efficient"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Force garbage collection before execution
        gc.collect()
        
        tracker = MemoryTracker()
        tracker.start_monitoring()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Cleanup and report
            stats = tracker.stop_monitoring()
            
            # Force another garbage collection
            gc.collect()
            
            # Log if memory usage was high
            memory_increase = stats.get('memory_increase', 0)
            if memory_increase > 10 * 1024 * 1024:  # > 10MB
                logger.warning(
                    f"High memory usage in {func.__name__}: "
                    f"{memory_increase / (1024 * 1024):.1f} MB"
                )
    
    return wrapper


class MemoryOptimizer:
    """Main memory optimization coordinator"""
    
    def __init__(self):
        self.tracker = MemoryTracker()
        self.cache = LRUCache()
        self.file_processor = StreamingFileProcessor()
        self.weak_refs = WeakReferenceManager()
        self._memory_pools = {}
        self._optimization_enabled = True
    
    def enable_optimization(self):
        """Enable memory optimization features"""
        self._optimization_enabled = True
        logger.info("Memory optimization enabled")
    
    def disable_optimization(self):
        """Disable memory optimization features"""
        self._optimization_enabled = False
        logger.info("Memory optimization disabled")
    
    def start_session(self, session_name: str = "default"):
        """Start a memory optimization session"""
        if self._optimization_enabled:
            self.tracker.start_monitoring()
            logger.info(f"Memory optimization session '{session_name}' started")
    
    def end_session(self) -> Dict[str, Any]:
        """End memory optimization session"""
        if not self._optimization_enabled:
            return {}
        
        stats = self.tracker.stop_monitoring()
        
        # Cleanup
        self.cleanup_resources()
        
        logger.info(f"Memory optimization session ended. Peak usage: {stats.get('peak_memory', 0)}")
        
        return stats
    
    def cleanup_resources(self):
        """Cleanup all managed resources"""
        if not self._optimization_enabled:
            return
        
        # Clear caches
        self.cache.clear()
        
        # Cleanup weak references
        dead_refs = self.weak_refs.cleanup_dead_references()
        if dead_refs > 0:
            logger.debug(f"Cleaned up {dead_refs} dead weak references")
        
        # Clear memory pools
        for pool in self._memory_pools.values():
            pool.clear()
        
        # Force garbage collection
        collected = gc.collect()
        if collected > 0:
            logger.debug(f"Garbage collection freed {collected} objects")
    
    def get_memory_pool(self, pool_name: str, factory: Callable, max_size: int = 10) -> MemoryPool:
        """Get or create a memory pool"""
        if pool_name not in self._memory_pools:
            self._memory_pools[pool_name] = MemoryPool(factory, max_size)
        return self._memory_pools[pool_name]
    
    def create_context_manager(self, resource_name: str):
        """Create context manager for resource lifecycle"""
        
        class ResourceContextManager:
            def __init__(self, optimizer, name):
                self.optimizer = optimizer
                self.name = name
                self.checkpoint_data = None
            
            def __enter__(self):
                if self.optimizer._optimization_enabled:
                    self.checkpoint_data = self.optimizer.tracker.checkpoint(f"enter_{self.name}")
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.optimizer._optimization_enabled:
                    self.optimizer.tracker.checkpoint(f"exit_{self.name}")
                    
                    # Cleanup if exception occurred
                    if exc_type is not None:
                        logger.debug(f"Exception in {self.name}, cleaning up resources")
                        self.optimizer.cleanup_resources()
        
        return ResourceContextManager(self, resource_name)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        stats = {
            'optimization_enabled': self._optimization_enabled,
            'cache_stats': self.cache.get_stats(),
            'weak_ref_stats': self.weak_refs.get_stats(),
            'memory_pools': {name: len(pool._pool) for name, pool in self._memory_pools.items()},
            'gc_stats': {
                'collections': gc.get_count(),
                'thresholds': gc.get_threshold()
            }
        }
        
        # Add current memory info
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            stats['system_memory'] = {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent()
            }
        except Exception as e:
            logger.warning(f"Could not get system memory info: {e}")
        
        return stats
    
    def generate_memory_report(self) -> str:
        """Generate comprehensive memory report"""
        stats = self.get_comprehensive_stats()
        
        report = [
            "Memory Optimization Report",
            "=" * 50,
            f"Optimization Enabled: {stats['optimization_enabled']}",
            "",
            "Cache Statistics:",
            f"  Size: {stats['cache_stats']['size']}/{stats['cache_stats']['max_size']}",
            f"  Memory Usage: {stats['cache_stats']['memory_usage'] / (1024*1024):.1f} MB",
            f"  Memory Utilization: {stats['cache_stats']['memory_utilization']:.1f}%",
            "",
            "Weak References:",
            f"  Total: {stats['weak_ref_stats']['total_references']}",
            f"  Live: {stats['weak_ref_stats']['live_references']}",
            f"  Dead: {stats['weak_ref_stats']['dead_references']}",
            "",
            "Memory Pools:",
        ]
        
        for pool_name, pool_size in stats['memory_pools'].items():
            report.append(f"  {pool_name}: {pool_size} objects")
        
        if 'system_memory' in stats:
            memory_mb = stats['system_memory']['rss'] / (1024 * 1024)
            report.extend([
                "",
                "System Memory:",
                f"  RSS: {memory_mb:.1f} MB",
                f"  Memory Percent: {stats['system_memory']['percent']:.1f}%"
            ])
        
        report.append("")
        report.append(self.tracker.get_memory_report())
        
        return "\n".join(report)
    
    # Compatibility methods for file_manager.py
    def start_monitoring(self):
        """Start memory monitoring (compatibility method)"""
        self.start_session("file_manager")
    
    def cleanup(self):
        """Cleanup resources (compatibility method)"""
        self.cleanup_resources()
    
    def should_trigger_gc(self) -> bool:
        """Check if garbage collection should be triggered"""
        try:
            process = psutil.Process()
            memory_percent = process.memory_percent()
            # Trigger GC if memory usage is above 70%
            return memory_percent > 70.0
        except Exception:
            # Default to triggering GC every so often
            return True
    
    def force_gc(self):
        """Force garbage collection"""
        collected = gc.collect()
        logger.debug(f"Forced garbage collection freed {collected} objects")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory statistics (compatibility method)"""
        stats = self.get_comprehensive_stats()
        
        # Convert to format expected by file_manager
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            peak_memory_mb = memory_info.rss / (1024 * 1024)
        except Exception:
            peak_memory_mb = 0.0
        
        return {
            'peak_memory_mb': peak_memory_mb,
            'current_memory_mb': peak_memory_mb,
            'cache_size': stats['cache_stats']['size'],
            'optimization_enabled': stats['optimization_enabled']
        }
    
    def get_cached_result(self, cache_key: str) -> Any:
        """Get cached result (compatibility method)"""
        return self.cache.get(cache_key)
    
    def cache_result(self, cache_key: str, result: Any):
        """Cache result (compatibility method)"""
        self.cache.set(cache_key, result)


# Global memory optimizer instance
memory_optimizer = MemoryOptimizer()