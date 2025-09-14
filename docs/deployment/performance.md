# Performance Tuning

## Overview

This guide covers performance optimization strategies for the MarkItDown GUI application, including system resource management, conversion performance tuning, and scalability considerations.

## Performance Benchmarks

### Target Performance Metrics
- **Application Startup**: < 3 seconds cold start
- **File Loading**: < 1 second for 1000 files
- **Conversion Speed**: 1MB document in < 5 seconds
- **Memory Usage**: < 512MB for typical workloads
- **CPU Usage**: < 30% average, < 80% peak
- **UI Responsiveness**: 60 FPS, < 100ms input latency

### Performance Testing Framework
```python
# tests/performance/benchmark.py
import time
import psutil
import memory_profiler
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    operation: str
    duration_seconds: float
    memory_peak_mb: float
    cpu_percent: float
    files_processed: int = 0
    
    @property
    def throughput(self) -> float:
        if self.duration_seconds > 0 and self.files_processed > 0:
            return self.files_processed / self.duration_seconds
        return 0.0

class PerformanceBenchmark:
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.process = psutil.Process()
    
    def benchmark_operation(self, operation_name: str, operation_func, *args, **kwargs):
        # Start monitoring
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        
        # Execute operation
        result = operation_func(*args, **kwargs)
        
        # End monitoring
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        cpu_percent = self.process.cpu_percent()
        
        # Record metrics
        metrics = PerformanceMetrics(
            operation=operation_name,
            duration_seconds=end_time - start_time,
            memory_peak_mb=max(start_memory, end_memory),
            cpu_percent=cpu_percent
        )
        
        self.metrics.append(metrics)
        return result, metrics
```

## Memory Optimization

### Memory Management Strategy
```python
# markitdown_gui/core/memory_manager.py
import gc
import psutil
import threading
from typing import Optional
import weakref

class MemoryManager:
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb
        self.process = psutil.Process()
        self.cache_registry = weakref.WeakSet()
        self.monitoring = False
        
    def start_monitoring(self):
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        monitor_thread.start()
    
    def _monitor_memory(self):
        while self.monitoring:
            current_memory = self.get_memory_usage_mb()
            if current_memory > self.max_memory_mb * 0.8:  # 80% threshold
                self.cleanup_memory()
            time.sleep(5)
    
    def get_memory_usage_mb(self) -> float:
        return self.process.memory_info().rss / 1024 / 1024
    
    def cleanup_memory(self):
        # Clear weak references
        for cache in list(self.cache_registry):
            if hasattr(cache, 'clear'):
                cache.clear()
        
        # Force garbage collection
        gc.collect()
    
    def register_cache(self, cache_object):
        self.cache_registry.add(cache_object)

# Global memory manager
memory_manager = MemoryManager()
```

### Efficient File Handling
```python
# markitdown_gui/core/efficient_file_manager.py
import mmap
import os
from typing import Generator, Optional
from pathlib import Path

class EfficientFileReader:
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
    
    def read_large_file_chunked(self, file_path: str) -> Generator[bytes, None, None]:
        """Read large files in chunks to avoid memory issues"""
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
    
    def memory_mapped_read(self, file_path: str) -> Optional[mmap.mmap]:
        """Use memory mapping for very large files"""
        try:
            with open(file_path, 'rb') as f:
                return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        except (OSError, ValueError):
            return None
    
    def get_file_sample(self, file_path: str, sample_size: int = 1024) -> bytes:
        """Get a small sample of a file for type detection"""
        try:
            with open(file_path, 'rb') as f:
                return f.read(sample_size)
        except Exception:
            return b""
```

## CPU Optimization

### Parallel Processing
```python
# markitdown_gui/core/parallel_processor.py
import multiprocessing
import concurrent.futures
from typing import List, Callable, Any, Dict
import queue
import threading

class ParallelConversionManager:
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(8, multiprocessing.cpu_count())
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers)
        
    def convert_files_parallel(self, file_paths: List[str], 
                             conversion_func: Callable,
                             use_processes: bool = False) -> List[Any]:
        """Convert multiple files in parallel"""
        executor = self.process_pool if use_processes else self.thread_pool
        
        futures = []
        for file_path in file_paths:
            future = executor.submit(conversion_func, file_path)
            futures.append(future)
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        
        return results
    
    def batch_process_with_queue(self, items: List[Any], 
                                processor_func: Callable,
                                batch_size: int = 100):
        """Process items in batches using queue"""
        result_queue = queue.Queue()
        
        def worker():
            while True:
                batch = []
                for _ in range(batch_size):
                    try:
                        item = item_queue.get_nowait()
                        batch.append(item)
                    except queue.Empty:
                        break
                
                if not batch:
                    break
                
                batch_results = [processor_func(item) for item in batch]
                for result in batch_results:
                    result_queue.put(result)
                
                for _ in batch:
                    item_queue.task_done()
        
        # Fill input queue
        item_queue = queue.Queue()
        for item in items:
            item_queue.put(item)
        
        # Start workers
        threads = []
        for _ in range(self.max_workers):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        
        # Collect results
        results = []
        for _ in range(len(items)):
            results.append(result_queue.get())
        
        # Wait for completion
        for t in threads:
            t.join()
        
        return results
```

### Async UI Operations
```python
# markitdown_gui/core/async_operations.py
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QTimer
from typing import Callable, Any

class AsyncWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class AsyncOperationManager:
    def __init__(self):
        self.active_threads = []
    
    def run_async(self, func: Callable, callback: Callable = None, 
                  error_callback: Callable = None, *args, **kwargs):
        """Run function asynchronously"""
        thread = QThread()
        worker = AsyncWorker(func, *args, **kwargs)
        worker.moveToThread(thread)
        
        # Connect signals
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        if callback:
            worker.finished.connect(callback)
        if error_callback:
            worker.error.connect(error_callback)
        
        # Start thread
        thread.start()
        self.active_threads.append(thread)
        
        # Clean up finished threads
        thread.finished.connect(lambda: self.active_threads.remove(thread))
        
        return thread
```

## I/O Optimization

### Caching Strategy
```python
# markitdown_gui/core/cache_manager.py
import sqlite3
import pickle
import hashlib
import time
from typing import Any, Optional, Dict
from pathlib import Path

class DiskCache:
    def __init__(self, cache_dir: str = ".cache", max_size_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_mb = max_size_mb
        self.db_path = self.cache_dir / "cache.db"
        self._init_db()
    
    def _init_db(self):
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                data BLOB,
                created_at REAL,
                accessed_at REAL,
                size_bytes INTEGER
            )
        """)
        self.conn.commit()
    
    def get(self, key: str) -> Optional[Any]:
        cursor = self.conn.execute(
            "SELECT data FROM cache_entries WHERE key = ?", (key,)
        )
        row = cursor.fetchone()
        
        if row:
            # Update access time
            self.conn.execute(
                "UPDATE cache_entries SET accessed_at = ? WHERE key = ?",
                (time.time(), key)
            )
            self.conn.commit()
            
            return pickle.loads(row[0])
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        data = pickle.dumps(value)
        size_bytes = len(data)
        current_time = time.time()
        
        self.conn.execute("""
            INSERT OR REPLACE INTO cache_entries 
            (key, data, created_at, accessed_at, size_bytes)
            VALUES (?, ?, ?, ?, ?)
        """, (key, data, current_time, current_time, size_bytes))
        
        self.conn.commit()
        
        # Clean up if cache is too large
        self._cleanup_cache()
    
    def _cleanup_cache(self):
        # Remove expired entries
        current_time = time.time()
        self.conn.execute(
            "DELETE FROM cache_entries WHERE created_at < ?",
            (current_time - 3600,)  # 1 hour TTL
        )
        
        # Check total size
        cursor = self.conn.execute("SELECT SUM(size_bytes) FROM cache_entries")
        total_size = cursor.fetchone()[0] or 0
        
        if total_size > self.max_size_mb * 1024 * 1024:
            # Remove least recently accessed entries
            self.conn.execute("""
                DELETE FROM cache_entries WHERE key IN (
                    SELECT key FROM cache_entries 
                    ORDER BY accessed_at ASC 
                    LIMIT (SELECT COUNT(*) FROM cache_entries) / 4
                )
            """)
        
        self.conn.commit()

class FileHashCache:
    def __init__(self):
        self.disk_cache = DiskCache("file_cache")
    
    def get_file_hash(self, file_path: str) -> str:
        """Get or compute file hash for caching"""
        stat = os.stat(file_path)
        cache_key = f"hash_{file_path}_{stat.st_mtime}_{stat.st_size}"
        
        file_hash = self.disk_cache.get(cache_key)
        if file_hash:
            return file_hash
        
        # Compute hash
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        file_hash = hasher.hexdigest()
        self.disk_cache.set(cache_key, file_hash)
        return file_hash
    
    def get_conversion_result(self, file_path: str, options: Dict) -> Optional[Any]:
        """Get cached conversion result"""
        file_hash = self.get_file_hash(file_path)
        options_hash = hashlib.md5(str(sorted(options.items())).encode()).hexdigest()
        cache_key = f"conversion_{file_hash}_{options_hash}"
        
        return self.disk_cache.get(cache_key)
    
    def set_conversion_result(self, file_path: str, options: Dict, result: Any):
        """Cache conversion result"""
        file_hash = self.get_file_hash(file_path)
        options_hash = hashlib.md5(str(sorted(options.items())).encode()).hexdigest()
        cache_key = f"conversion_{file_hash}_{options_hash}"
        
        self.disk_cache.set(cache_key, result)
```

## UI Performance

### Lazy Loading and Virtualization
```python
# markitdown_gui/ui/components/virtual_list.py
from PyQt6.QtWidgets import QAbstractItemView, QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal
from typing import List, Any, Callable

class VirtualListWidget(QScrollArea):
    """Virtualized list widget for handling large datasets efficiently"""
    
    item_clicked = pyqtSignal(int, object)
    
    def __init__(self, item_height: int = 50):
        super().__init__()
        self.item_height = item_height
        self.items: List[Any] = []
        self.item_renderer: Optional[Callable] = None
        self.visible_items = {}
        
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container widget
        self.container = QWidget()
        self.setWidget(self.container)
        
        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self.update_visible_items)
    
    def set_items(self, items: List[Any]):
        """Set the list items"""
        self.items = items
        self.update_container_size()
        self.update_visible_items()
    
    def set_item_renderer(self, renderer: Callable[[Any, int], QWidget]):
        """Set the item renderer function"""
        self.item_renderer = renderer
    
    def update_container_size(self):
        """Update container size based on item count"""
        total_height = len(self.items) * self.item_height
        self.container.setFixedSize(self.width() - 20, total_height)
    
    def update_visible_items(self):
        """Update only visible items for performance"""
        if not self.item_renderer:
            return
        
        # Calculate visible range
        scroll_value = self.verticalScrollBar().value()
        visible_height = self.viewport().height()
        
        start_index = max(0, scroll_value // self.item_height - 1)
        end_index = min(len(self.items), 
                       (scroll_value + visible_height) // self.item_height + 2)
        
        # Remove items outside visible range
        for index in list(self.visible_items.keys()):
            if index < start_index or index >= end_index:
                widget = self.visible_items.pop(index)
                widget.hide()
                widget.setParent(None)
        
        # Add items in visible range
        for index in range(start_index, end_index):
            if index not in self.visible_items and index < len(self.items):
                widget = self.item_renderer(self.items[index], index)
                widget.setParent(self.container)
                widget.setGeometry(0, index * self.item_height, 
                                 self.container.width(), self.item_height)
                widget.show()
                self.visible_items[index] = widget

class LazyImageLoader:
    """Lazy loading for image previews"""
    
    def __init__(self, cache_size: int = 50):
        self.cache_size = cache_size
        self.image_cache = {}
        self.loading_queue = []
        self.loading_thread = None
    
    def load_image_async(self, image_path: str, callback: Callable):
        """Load image asynchronously"""
        if image_path in self.image_cache:
            callback(self.image_cache[image_path])
            return
        
        # Add to loading queue
        self.loading_queue.append((image_path, callback))
        
        if not self.loading_thread or not self.loading_thread.isAlive():
            self.loading_thread = threading.Thread(target=self._process_loading_queue)
            self.loading_thread.start()
    
    def _process_loading_queue(self):
        """Process image loading queue"""
        while self.loading_queue:
            image_path, callback = self.loading_queue.pop(0)
            
            try:
                # Load and resize image
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Scale to reasonable size
                    scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
                    
                    # Cache with LRU eviction
                    if len(self.image_cache) >= self.cache_size:
                        # Remove oldest item
                        oldest_key = next(iter(self.image_cache))
                        del self.image_cache[oldest_key]
                    
                    self.image_cache[image_path] = scaled_pixmap
                    callback(scaled_pixmap)
                else:
                    callback(None)
            except Exception:
                callback(None)
```

## Configuration Tuning

### Performance Configuration
```yaml
# config/performance.yaml
performance:
  # Memory settings
  memory:
    max_usage_mb: 1024
    cache_size_mb: 128
    gc_threshold: 100
    enable_memory_profiling: false
  
  # CPU settings
  cpu:
    max_worker_threads: 8
    conversion_workers: 4
    ui_worker_threads: 2
    enable_multiprocessing: true
  
  # I/O settings
  io:
    read_buffer_size: 65536
    write_buffer_size: 65536
    use_memory_mapping: true
    async_file_operations: true
  
  # UI settings
  ui:
    enable_virtualization: true
    lazy_load_images: true
    animation_duration_ms: 150
    debounce_delay_ms: 300
  
  # Conversion settings
  conversion:
    batch_size: 10
    timeout_seconds: 300
    enable_caching: true
    cache_ttl_hours: 24
    parallel_conversions: true
  
  # Monitoring
  monitoring:
    enable_profiling: false
    log_performance_metrics: false
    memory_check_interval_ms: 5000
```

## Monitoring and Profiling

### Performance Monitoring
```python
# markitdown_gui/core/performance_monitor.py
import time
import psutil
import threading
from typing import Dict, List
from collections import deque
from dataclasses import dataclass

@dataclass
class PerformanceSnapshot:
    timestamp: float
    cpu_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    thread_count: int

class PerformanceMonitor:
    def __init__(self, history_size: int = 300):  # 5 minutes at 1s intervals
        self.history_size = history_size
        self.snapshots = deque(maxlen=history_size)
        self.process = psutil.Process()
        self.monitoring = False
        self.monitor_thread = None
        
        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_mb': 512.0,
            'thread_count': 50
        }
        
        # Alert callbacks
        self.alert_callbacks = []
    
    def start_monitoring(self, interval: float = 1.0):
        """Start performance monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        last_io = self.process.io_counters()
        
        while self.monitoring:
            try:
                # Collect metrics
                current_io = self.process.io_counters()
                
                snapshot = PerformanceSnapshot(
                    timestamp=time.time(),
                    cpu_percent=self.process.cpu_percent(),
                    memory_mb=self.process.memory_info().rss / 1024 / 1024,
                    disk_io_read_mb=(current_io.read_bytes - last_io.read_bytes) / 1024 / 1024,
                    disk_io_write_mb=(current_io.write_bytes - last_io.write_bytes) / 1024 / 1024,
                    thread_count=self.process.num_threads()
                )
                
                self.snapshots.append(snapshot)
                last_io = current_io
                
                # Check thresholds
                self._check_thresholds(snapshot)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(interval)
    
    def _check_thresholds(self, snapshot: PerformanceSnapshot):
        """Check if any thresholds are exceeded"""
        alerts = []
        
        if snapshot.cpu_percent > self.thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {snapshot.cpu_percent:.1f}%")
        
        if snapshot.memory_mb > self.thresholds['memory_mb']:
            alerts.append(f"High memory usage: {snapshot.memory_mb:.1f}MB")
        
        if snapshot.thread_count > self.thresholds['thread_count']:
            alerts.append(f"High thread count: {snapshot.thread_count}")
        
        # Notify callbacks
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert, snapshot)
                except Exception:
                    pass
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]
        return {
            'cpu_percent': latest.cpu_percent,
            'memory_mb': latest.memory_mb,
            'thread_count': latest.thread_count,
            'disk_io_read_mb': latest.disk_io_read_mb,
            'disk_io_write_mb': latest.disk_io_write_mb
        }
    
    def get_average_metrics(self, duration_seconds: int = 60) -> Dict[str, float]:
        """Get average metrics over specified duration"""
        cutoff_time = time.time() - duration_seconds
        recent_snapshots = [s for s in self.snapshots if s.timestamp >= cutoff_time]
        
        if not recent_snapshots:
            return {}
        
        return {
            'cpu_percent': sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots),
            'memory_mb': sum(s.memory_mb for s in recent_snapshots) / len(recent_snapshots),
            'thread_count': sum(s.thread_count for s in recent_snapshots) / len(recent_snapshots)
        }
    
    def add_alert_callback(self, callback: Callable):
        """Add performance alert callback"""
        self.alert_callbacks.append(callback)

# Global performance monitor
performance_monitor = PerformanceMonitor()
```

## Related Documentation

- 🚀 [Deployment Guide](deployment.md) - Production deployment
- ⚙️ [Configuration Management](configuration.md) - Environment settings
- 🔒 [Security Guidelines](security.md) - Security best practices
- 📋 [Monitoring](monitoring.md) - System monitoring and alerts

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development