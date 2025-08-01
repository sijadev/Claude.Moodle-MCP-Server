#!/usr/bin/env python3
"""
Test Data Storage System für MoodleClaude
========================================

Persistente lokale Datenspeicherung für Test-Ergebnisse, 
Konfigurationen und Benchmark-Daten.
"""

import os
import json
import sqlite3
import pickle
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
import logging


@dataclass
class TestResult:
    """Test result data structure."""
    test_id: str
    test_name: str
    success: bool
    duration: float
    timestamp: str
    details: Dict[str, Any]
    environment: str
    version: str


@dataclass
class BenchmarkData:
    """Performance benchmark data structure."""
    benchmark_id: str
    test_name: str
    metric_name: str
    value: float
    unit: str
    timestamp: str
    environment: str
    metadata: Dict[str, Any]


class TestDataStorage:
    """Local storage system for test data and results."""
    
    def __init__(self, storage_dir: str = "test_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.storage_dir / "results").mkdir(exist_ok=True)
        (self.storage_dir / "benchmarks").mkdir(exist_ok=True)
        (self.storage_dir / "cache").mkdir(exist_ok=True)
        (self.storage_dir / "snapshots").mkdir(exist_ok=True)
        
        # Initialize databases
        self.db_path = self.storage_dir / "test_data.db"
        self._init_database()
        
        self.logger = logging.getLogger(__name__)
    
    def _init_database(self):
        """Initialize SQLite database for structured data."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT UNIQUE,
                    test_name TEXT,
                    success BOOLEAN,
                    duration REAL,
                    timestamp TEXT,
                    environment TEXT,
                    version TEXT,
                    details_json TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    benchmark_id TEXT,
                    test_name TEXT,
                    metric_name TEXT,
                    value REAL,
                    unit TEXT,
                    timestamp TEXT,
                    environment TEXT,
                    metadata_json TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    start_time TEXT,
                    end_time TEXT,
                    total_tests INTEGER,
                    passed_tests INTEGER,
                    failed_tests INTEGER,
                    environment TEXT,
                    config_hash TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_name ON test_results(test_name);
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_benchmark_name ON benchmarks(test_name, metric_name);
            """)
            
            conn.commit()
    
    def store_test_result(self, result: TestResult) -> bool:
        """Store a test result in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO test_results 
                    (test_id, test_name, success, duration, timestamp, environment, version, details_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.test_id,
                    result.test_name,
                    result.success,
                    result.duration,
                    result.timestamp,
                    result.environment,
                    result.version,
                    json.dumps(result.details)
                ))
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to store test result: {e}")
            return False
    
    def store_benchmark(self, benchmark: BenchmarkData) -> bool:
        """Store benchmark data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO benchmarks 
                    (benchmark_id, test_name, metric_name, value, unit, timestamp, environment, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    benchmark.benchmark_id,
                    benchmark.test_name,
                    benchmark.metric_name,
                    benchmark.value,
                    benchmark.unit,
                    benchmark.timestamp,
                    benchmark.environment,
                    json.dumps(benchmark.metadata)
                ))
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to store benchmark: {e}")
            return False
    
    def get_test_results(self, test_name: Optional[str] = None, 
                        environment: Optional[str] = None,
                        since: Optional[datetime] = None) -> List[TestResult]:
        """Retrieve test results with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM test_results WHERE 1=1"
                params = []
                
                if test_name:
                    query += " AND test_name = ?"
                    params.append(test_name)
                
                if environment:
                    query += " AND environment = ?"
                    params.append(environment)
                
                if since:
                    query += " AND timestamp >= ?"
                    params.append(since.isoformat())
                
                query += " ORDER BY timestamp DESC"
                
                cursor = conn.execute(query, params)
                results = []
                
                for row in cursor.fetchall():
                    results.append(TestResult(
                        test_id=row[1],
                        test_name=row[2],
                        success=bool(row[3]),
                        duration=row[4],
                        timestamp=row[5],
                        environment=row[6],
                        version=row[7],
                        details=json.loads(row[8]) if row[8] else {}
                    ))
                
                return results
        except Exception as e:
            self.logger.error(f"Failed to retrieve test results: {e}")
            return []
    
    def get_benchmarks(self, test_name: Optional[str] = None,
                      metric_name: Optional[str] = None) -> List[BenchmarkData]:
        """Retrieve benchmark data with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM benchmarks WHERE 1=1"
                params = []
                
                if test_name:
                    query += " AND test_name = ?"
                    params.append(test_name)
                
                if metric_name:
                    query += " AND metric_name = ?"
                    params.append(metric_name)
                
                query += " ORDER BY timestamp DESC"
                
                cursor = conn.execute(query, params)
                results = []
                
                for row in cursor.fetchall():
                    results.append(BenchmarkData(
                        benchmark_id=row[1],
                        test_name=row[2],
                        metric_name=row[3],
                        value=row[4],
                        unit=row[5],
                        timestamp=row[6],
                        environment=row[7],
                        metadata=json.loads(row[8]) if row[8] else {}
                    ))
                
                return results
        except Exception as e:
            self.logger.error(f"Failed to retrieve benchmarks: {e}")
            return []
    
    def store_json_data(self, filename: str, data: Dict[str, Any]) -> bool:
        """Store arbitrary JSON data to file."""
        try:
            file_path = self.storage_dir / "results" / f"{filename}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to store JSON data: {e}")
            return False
    
    def load_json_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load JSON data from file."""
        try:
            file_path = self.storage_dir / "results" / f"{filename}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Failed to load JSON data: {e}")
            return None
    
    def cache_object(self, key: str, obj: Any, ttl_hours: int = 24) -> bool:
        """Cache a Python object with TTL."""
        try:
            cache_file = self.storage_dir / "cache" / f"{key}.pkl"
            cache_meta = self.storage_dir / "cache" / f"{key}.meta"
            
            # Store object
            with open(cache_file, 'wb') as f:
                pickle.dump(obj, f)
            
            # Store metadata
            metadata = {
                'created': datetime.now().isoformat(),
                'expires': (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
                'key': key
            }
            
            with open(cache_meta, 'w') as f:
                json.dump(metadata, f)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to cache object: {e}")
            return False
    
    def get_cached_object(self, key: str) -> Optional[Any]:
        """Retrieve cached object if not expired."""
        try:
            cache_file = self.storage_dir / "cache" / f"{key}.pkl"
            cache_meta = self.storage_dir / "cache" / f"{key}.meta"
            
            if not cache_file.exists() or not cache_meta.exists():
                return None
            
            # Check expiration
            with open(cache_meta, 'r') as f:
                metadata = json.load(f)
            
            expires = datetime.fromisoformat(metadata['expires'])
            if datetime.now() > expires:
                # Cleanup expired cache
                cache_file.unlink(missing_ok=True)
                cache_meta.unlink(missing_ok=True)
                return None
            
            # Return cached object
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve cached object: {e}")
            return None
    
    def create_snapshot(self, snapshot_name: str, include_cache: bool = False) -> bool:
        """Create a snapshot of all test data."""
        try:
            snapshot_dir = self.storage_dir / "snapshots" / f"{snapshot_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy database
            import shutil
            shutil.copy2(self.db_path, snapshot_dir / "test_data.db")
            
            # Copy results
            results_src = self.storage_dir / "results"
            if results_src.exists():
                shutil.copytree(results_src, snapshot_dir / "results", dirs_exist_ok=True)
            
            # Copy benchmarks
            benchmarks_src = self.storage_dir / "benchmarks"
            if benchmarks_src.exists():
                shutil.copytree(benchmarks_src, snapshot_dir / "benchmarks", dirs_exist_ok=True)
            
            # Optionally copy cache
            if include_cache:
                cache_src = self.storage_dir / "cache"
                if cache_src.exists():
                    shutil.copytree(cache_src, snapshot_dir / "cache", dirs_exist_ok=True)
            
            # Create manifest
            manifest = {
                'snapshot_name': snapshot_name,
                'created': datetime.now().isoformat(),
                'include_cache': include_cache,
                'files': list(str(p.relative_to(snapshot_dir)) for p in snapshot_dir.rglob('*') if p.is_file())
            }
            
            with open(snapshot_dir / "manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            self.logger.info(f"Snapshot created: {snapshot_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create snapshot: {e}")
            return False
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get comprehensive test statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Overall stats
                cursor = conn.execute("SELECT COUNT(*) FROM test_results")
                stats['total_tests'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM test_results WHERE success = 1")
                stats['passed_tests'] = cursor.fetchone()[0]
                
                stats['failed_tests'] = stats['total_tests'] - stats['passed_tests']
                stats['success_rate'] = (stats['passed_tests'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0
                
                # By environment
                cursor = conn.execute("""
                    SELECT environment, COUNT(*), 
                           SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as passed
                    FROM test_results 
                    GROUP BY environment
                """)
                stats['by_environment'] = {}
                for row in cursor.fetchall():
                    env, total, passed = row
                    stats['by_environment'][env] = {
                        'total': total,
                        'passed': passed,
                        'failed': total - passed,
                        'success_rate': (passed / total * 100) if total > 0 else 0
                    }
                
                # Recent activity (last 7 days)
                seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM test_results 
                    WHERE timestamp >= ?
                """, (seven_days_ago,))
                stats['recent_tests'] = cursor.fetchone()[0]
                
                # Average test duration
                cursor = conn.execute("SELECT AVG(duration) FROM test_results WHERE duration > 0")
                result = cursor.fetchone()
                stats['avg_duration'] = result[0] if result[0] else 0
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get test statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> bool:
        """Clean up test data older than specified days."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Clean old test results
                cursor = conn.execute("DELETE FROM test_results WHERE timestamp < ?", (cutoff_date,))
                deleted_tests = cursor.rowcount
                
                # Clean old benchmarks
                cursor = conn.execute("DELETE FROM benchmarks WHERE timestamp < ?", (cutoff_date,))
                deleted_benchmarks = cursor.rowcount
                
                conn.commit()
            
            # Clean expired cache
            cache_dir = self.storage_dir / "cache"
            if cache_dir.exists():
                for meta_file in cache_dir.glob("*.meta"):
                    try:
                        with open(meta_file, 'r') as f:
                            metadata = json.load(f)
                        
                        expires = datetime.fromisoformat(metadata['expires'])
                        if datetime.now() > expires:
                            # Remove cache files
                            cache_file = meta_file.with_suffix('.pkl')
                            meta_file.unlink(missing_ok=True)
                            cache_file.unlink(missing_ok=True)
                    except:
                        continue
            
            self.logger.info(f"Cleaned up {deleted_tests} test results and {deleted_benchmarks} benchmarks")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            return False


def create_test_data_storage() -> TestDataStorage:
    """Factory function to create test data storage."""
    project_root = Path(__file__).parent.parent.parent
    storage_dir = project_root / "test_storage"
    return TestDataStorage(str(storage_dir))


# Example usage and testing
if __name__ == "__main__":
    # Demo usage
    storage = create_test_data_storage()
    
    # Store a test result
    result = TestResult(
        test_id="test_001",
        test_name="mcp_server_basic",
        success=True,
        duration=0.5,
        timestamp=datetime.now().isoformat(),
        details={"modules_loaded": 5, "errors": []},
        environment="local_test",
        version="3.0.0"
    )
    
    storage.store_test_result(result)
    
    # Store benchmark data
    benchmark = BenchmarkData(
        benchmark_id="bench_001",
        test_name="async_performance",
        metric_name="response_time",
        value=0.011,
        unit="seconds",
        timestamp=datetime.now().isoformat(),
        environment="local_test",
        metadata={"concurrent_requests": 10}
    )
    
    storage.store_benchmark(benchmark)
    
    # Get statistics
    stats = storage.get_test_statistics()
    print("Test Statistics:", json.dumps(stats, indent=2))