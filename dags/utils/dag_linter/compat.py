"""
Compatibility layer for Airflow 2.x and 3.x differences.
"""

import sys
from typing import TYPE_CHECKING

# Detect Airflow version
try:
    from airflow import __version__ as AIRFLOW_VERSION
    AIRFLOW_MAJOR_VERSION = int(AIRFLOW_VERSION.split('.')[0])
except Exception:
    AIRFLOW_MAJOR_VERSION = 2  # Default to 2 if detection fails


# Import DAG with version compatibility
try:
    from airflow.models import DAG
except ImportError:
    from airflow import DAG  # AF1 fallback


# Import BaseOperator with version compatibility
try:
    from airflow.models import BaseOperator
except ImportError:
    try:
        from airflow.models.baseoperator import BaseOperator
    except ImportError:
        from airflow.operators import BaseOperator


# Import Connection with version compatibility
try:
    from airflow.models import Connection
except ImportError:
    try:
        from airflow.models.connection import Connection
    except ImportError:
        Connection = None  # Graceful fallback


# Import BaseHook with version compatibility
try:
    from airflow.hooks.base import BaseHook
except ImportError:
    try:
        from airflow.hooks.base_hook import BaseHook
    except ImportError:
        BaseHook = None


# Import BaseSensorOperator with version compatibility
try:
    from airflow.sensors.base import BaseSensorOperator
except ImportError:
    try:
        from airflow.sensors.base_sensor_operator import BaseSensorOperator
    except ImportError:
        try:
            from airflow.sensors import BaseSensorOperator
        except ImportError:
            BaseSensorOperator = None


# Import DagBag with version compatibility
try:
    from airflow.models import DagBag
except ImportError:
    try:
        from airflow.models.dagbag import DagBag
    except ImportError:
        DagBag = None


def get_connection_exists(conn_id: str) -> bool:
    """
    Check if a connection exists in a version-agnostic way.
    
    Args:
        conn_id: Connection ID to check
        
    Returns:
        True if connection exists, False otherwise
    """
    if BaseHook is None:
        return True  # Can't check, assume it exists
    
    try:
        # Try AF2/AF3 method
        BaseHook.get_connection(conn_id)
        return True
    except Exception:
        return False


def safe_getattr(obj, attr: str, default=None):
    """
    Safely get attribute with fallback for renamed attributes across versions.
    
    Args:
        obj: Object to get attribute from
        attr: Attribute name
        default: Default value if attribute not found
        
    Returns:
        Attribute value or default
    """
    # Handle common attribute renames between AF2 and AF3
    attr_mappings = {
        'schedule_interval': ['schedule_interval', 'schedule', 'timetable'],
        'concurrency': ['concurrency', 'max_active_tasks'],
        'max_active_runs': ['max_active_runs', 'max_active_dag_runs'],
    }
    
    # Try the requested attribute first
    if hasattr(obj, attr):
        return getattr(obj, attr, default)
    
    # Try alternative names if available
    if attr in attr_mappings:
        for alt_attr in attr_mappings[attr]:
            if hasattr(obj, alt_attr):
                return getattr(obj, alt_attr, default)
    
    return default


def get_task_execution_timeout(task):
    """
    Get task execution timeout in a version-agnostic way.
    
    Args:
        task: Airflow task instance
        
    Returns:
        Execution timeout or None
    """
    return safe_getattr(task, 'execution_timeout', None)


def get_task_retries(task):
    """
    Get task retries in a version-agnostic way.
    
    Args:
        task: Airflow task instance
        
    Returns:
        Number of retries or 0
    """
    retries = safe_getattr(task, 'retries', None)
    return retries if retries is not None else 0


def get_task_concurrency(task):
    """
    Get task concurrency/max_active_tis in a version-agnostic way.
    
    Args:
        task: Airflow task instance
        
    Returns:
        Task concurrency or None
    """
    # AF3 uses max_active_tis_per_dag, AF2 uses task_concurrency
    for attr in ['max_active_tis_per_dag', 'task_concurrency', 'max_active_tis']:
        value = safe_getattr(task, attr, None)
        if value is not None:
            return value
    return None


def get_dag_schedule(dag):
    """
    Get DAG schedule in a version-agnostic way.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        Schedule interval/timetable or None
    """
    # AF3 uses 'schedule', AF2 uses 'schedule_interval'
    return safe_getattr(dag, 'schedule_interval', safe_getattr(dag, 'schedule', None))


def get_dag_concurrency(dag):
    """
    Get DAG concurrency in a version-agnostic way.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        DAG concurrency or None
    """
    # AF3 uses max_active_tasks, AF2 uses concurrency
    return safe_getattr(dag, 'concurrency', safe_getattr(dag, 'max_active_tasks', None))


def get_dag_max_active_runs(dag):
    """
    Get DAG max active runs in a version-agnostic way.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        Max active runs or None
    """
    # AF3 might rename this
    return safe_getattr(dag, 'max_active_runs', safe_getattr(dag, 'max_active_dag_runs', None))


__all__ = [
    'AIRFLOW_VERSION',
    'AIRFLOW_MAJOR_VERSION',
    'DAG',
    'BaseOperator',
    'Connection',
    'BaseHook',
    'BaseSensorOperator',
    'DagBag',
    'get_connection_exists',
    'safe_getattr',
    'get_task_execution_timeout',
    'get_task_retries',
    'get_task_concurrency',
    'get_dag_schedule',
    'get_dag_concurrency',
    'get_dag_max_active_runs',
]
