"""
DAG parsing performance and syntax checks.
"""

import os
import sys
import tracemalloc
import importlib.util
from typing import List, Dict, Optional

from airflow.models import DagBag
from ..models import LintResult, LintSeverity, LintCategory
from ..config import LintConfig


def check_parsing_time(dag_bag: DagBag, config: LintConfig) -> List[LintResult]:
    """
    Check DAG parsing times against configured thresholds.
    
    Args:
        dag_bag: Airflow DagBag instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    # dagbag_stats is a list of FileLoadStat objects
    for file_stat in dag_bag.dagbag_stats:
        # Extract parse time (in seconds)
        parse_time = file_stat.duration.total_seconds() if hasattr(file_stat.duration, 'total_seconds') else 0
        file_path = file_stat.file
        
        # Get DAGs from this file - file_stat.file is relative, dag.fileloc is absolute
        dags_in_file = [
            dag for dag in dag_bag.dags.values() 
            if dag.fileloc.endswith(file_path) or file_path in dag.fileloc
        ]
        
        # If no DAGs found but file was parsed, skip
        if not dags_in_file:
            continue
            
        for dag in dags_in_file:
            if parse_time > config.max_parsing_time_error:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    category=LintCategory.PARSING,
                    severity=LintSeverity.ERROR,
                    message=f"DAG parsing time ({parse_time:.2f}s) exceeds error threshold",
                    file_path=dag.fileloc,
                    metric_value=parse_time,
                    recommendation=(
                        "Optimize top-level code, move heavy imports inside task callables, "
                        "avoid expensive API calls or database queries at the module level"
                    )
                ))
            elif parse_time > config.max_parsing_time_warning:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    category=LintCategory.PARSING,
                    severity=LintSeverity.WARNING,
                    message=f"DAG parsing time ({parse_time:.2f}s) exceeds warning threshold",
                    file_path=dag.fileloc,
                    metric_value=parse_time,
                    recommendation="Consider optimizing imports and top-level code"
                ))
    
    return results


def check_import_errors(dag_bag: DagBag) -> List[LintResult]:
    """
    Check for DAGs that failed to import.
    
    Args:
        dag_bag: Airflow DagBag instance
        
    Returns:
        List of lint results
    """
    results = []
    
    for file_path, error_msg in dag_bag.import_errors.items():
        # Create a result for each import error
        results.append(LintResult(
            dag_id=f"ImportError:{file_path.split('/')[-1]}",
            category=LintCategory.PARSING,
            severity=LintSeverity.ERROR,
            message=f"Failed to import DAG: {error_msg}",
            file_path=file_path,
            recommendation="Fix syntax errors, missing imports, or dependency issues"
        ))
    
    return results


def check_dag_count_per_file(dag_bag: DagBag) -> List[LintResult]:
    """
    Check if files contain too many DAGs (performance best practice).
    
    Args:
        dag_bag: Airflow DagBag instance
        
    Returns:
        List of lint results
    """
    results = []
    
    # Group DAGs by file
    dags_by_file = {}
    for dag in dag_bag.dags.values():
        if dag.fileloc not in dags_by_file:
            dags_by_file[dag.fileloc] = []
        dags_by_file[dag.fileloc].append(dag)
    
    # Check for files with many DAGs
    for file_path, dags in dags_by_file.items():
        if len(dags) > 5:
            for dag in dags:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    category=LintCategory.PERFORMANCE,
                    severity=LintSeverity.INFO,
                    message=f"File contains {len(dags)} DAGs which may impact parsing performance",
                    file_path=file_path,
                    metric_value=len(dags),
                    recommendation="Consider splitting into multiple files for better scalability"
                ))
    
    return results


def check_parsing_resources(dag_bag: DagBag, config: LintConfig) -> List[LintResult]:
    """
    Check memory and CPU usage during DAG parsing.
    
    Args:
        dag_bag: Airflow DagBag instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    # Group DAGs by file to profile each file once
    dags_by_file = {}
    for dag in dag_bag.dags.values():
        if dag.fileloc not in dags_by_file:
            dags_by_file[dag.fileloc] = []
        dags_by_file[dag.fileloc].append(dag)
    
    # Profile each unique DAG file
    for file_path, dags in dags_by_file.items():
        # Skip files that don't exist or are not Python files
        if not file_path.endswith('.py') or not os.path.exists(file_path):
            continue
        
        try:
            # Profile memory usage
            profile_data = _profile_dag_file(file_path)
            
            if profile_data:
                memory_mb = profile_data['memory_mb']
                
                # Check memory thresholds
                for dag in dags:
                    if memory_mb > getattr(config, 'max_parsing_memory_mb_error', 500):
                        results.append(LintResult(
                            dag_id=dag.dag_id,
                            category=LintCategory.PARSING,
                            severity=LintSeverity.ERROR,
                            message=f"DAG parsing uses excessive memory ({memory_mb:.1f} MB)",
                            file_path=file_path,
                            metric_value=memory_mb,
                            recommendation=(
                                "Reduce memory usage: avoid loading large datasets at module level, "
                                "use lazy imports, defer heavy computations to task execution"
                            )
                        ))
                    elif memory_mb > getattr(config, 'max_parsing_memory_mb_warning', 100):
                        results.append(LintResult(
                            dag_id=dag.dag_id,
                            category=LintCategory.PARSING,
                            severity=LintSeverity.WARNING,
                            message=f"DAG parsing uses significant memory ({memory_mb:.1f} MB)",
                            file_path=file_path,
                            metric_value=memory_mb,
                            recommendation="Consider reducing module-level memory usage"
                        ))
        except Exception as e:
            # Skip profiling errors to avoid breaking the linter
            pass
    
    return results


def _profile_dag_file(file_path: str) -> Optional[Dict]:
    """
    Profile a single DAG file for memory usage.
    
    Args:
        file_path: Path to DAG file
        
    Returns:
        Dictionary with profiling metrics or None if profiling failed
    """
    try:
        # Start memory tracking
        tracemalloc.start()
        
        # Get baseline memory
        baseline_current, baseline_peak = tracemalloc.get_traced_memory()
        
        # Import the module (simulates parsing)
        spec = importlib.util.spec_from_file_location("__dag_profile__", file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            
            # Execute module in isolated namespace
            try:
                spec.loader.exec_module(module)
            except Exception:
                # Module execution failed, but we can still measure what was loaded
                pass
            
            # Get peak memory after import
            current, peak = tracemalloc.get_traced_memory()
            
            # Stop tracking
            tracemalloc.stop()
            
            # Calculate memory used (peak - baseline)
            memory_bytes = peak - baseline_peak
            memory_mb = memory_bytes / (1024 * 1024)
            
            # Clean up module
            if "__dag_profile__" in sys.modules:
                del sys.modules["__dag_profile__"]
            
            return {
                'memory_mb': memory_mb,
                'memory_bytes': memory_bytes,
            }
    except Exception:
        # Profiling failed, return None
        pass
    finally:
        # Ensure tracemalloc is stopped
        if tracemalloc.is_tracing():
            tracemalloc.stop()
    
    return None
