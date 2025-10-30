"""
Connection reference validation checks.
"""

import re
from typing import List, Set

from airflow.models import DAG, Connection
from airflow.hooks.base import BaseHook
from ..models import LintResult, LintSeverity, LintCategory
from ..config import LintConfig


def extract_connection_ids(task) -> Set[str]:
    """
    Extract connection IDs from task configuration.
    
    Args:
        task: Airflow task instance
        
    Returns:
        Set of connection IDs found in task
    """
    conn_ids = set()
    
    # Check common connection attributes
    for attr in ['http_conn_id', 'postgres_conn_id', 'mysql_conn_id', 
                 'aws_conn_id', 'gcp_conn_id', 'conn_id', 'connection_id']:
        if hasattr(task, attr):
            conn_id = getattr(task, attr)
            if conn_id and isinstance(conn_id, str):
                conn_ids.add(conn_id)
    
    # Check task kwargs for conn_id patterns
    if hasattr(task, 'op_kwargs'):
        for key, value in task.op_kwargs.items():
            if 'conn' in key.lower() and isinstance(value, str):
                conn_ids.add(value)
    
    # Check templated fields for connection references
    if hasattr(task, 'template_fields'):
        for field in task.template_fields:
            if hasattr(task, field):
                value = getattr(task, field)
                if isinstance(value, str):
                    # Look for Jinja template references like {{ conn.my_conn.host }}
                    matches = re.findall(r'\{\{\s*conn\.(\w+)', value)
                    conn_ids.update(matches)
    
    return conn_ids


def check_connection_existence(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check if referenced connections exist in Airflow.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    if not config.check_connection_existence:
        return results
    
    for task in dag.tasks:
        conn_ids = extract_connection_ids(task)
        
        for conn_id in conn_ids:
            try:
                # Try to get connection from Airflow
                Connection.get_connection_from_secrets(conn_id)
            except Exception:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.CONNECTIONS,
                    severity=LintSeverity.ERROR,
                    message=f"Connection '{conn_id}' not found in Airflow",
                    recommendation=(
                        f"Create connection '{conn_id}' in Airflow UI or "
                        "define it in airflow_settings.yaml"
                    )
                ))
    
    return results


def check_hardcoded_credentials(dag: DAG) -> List[LintResult]:
    """
    Check for potential hardcoded credentials in task parameters.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        List of lint results
    """
    results = []
    
    # Patterns that might indicate hardcoded credentials
    suspicious_patterns = [
        r'password\s*=\s*["\'](?!{{)[^"\']+ ["\']',
        r'api_key\s*=\s*["\'](?!{{)[^"\']+ ["\']',
        r'secret\s*=\s*["\'](?!{{)[^"\']+ ["\']',
        r'token\s*=\s*["\'](?!{{)[^"\']+ ["\']',
    ]
    
    # Check DAG file content for suspicious patterns
    try:
        with open(dag.fileloc, 'r') as f:
            content = f.read()
            
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    category=LintCategory.CONNECTIONS,
                    severity=LintSeverity.ERROR,
                    message="Potential hardcoded credentials detected in DAG file",
                    file_path=dag.fileloc,
                    recommendation=(
                        "Use Airflow Connections or Variables to store sensitive data. "
                        "Never hardcode credentials in DAG files"
                    )
                ))
                break  # Only report once per DAG
    except Exception:
        # Skip if file can't be read
        pass
    
    return results


def check_connection_test_on_failure(dag: DAG) -> List[LintResult]:
    """
    Suggest testing connections before tasks that depend on them.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        List of lint results
    """
    results = []
    
    tasks_with_connections = []
    
    for task in dag.tasks:
        conn_ids = extract_connection_ids(task)
        if conn_ids:
            tasks_with_connections.append((task, conn_ids))
    
    # If DAG uses connections but has no retries, suggest it
    if tasks_with_connections:
        for task, conn_ids in tasks_with_connections:
            if task.retries == 0:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.CONNECTIONS,
                    severity=LintSeverity.INFO,
                    message=f"Task uses connections {conn_ids} but has no retries",
                    recommendation=(
                        "Configure retries for tasks using external connections "
                        "to handle transient failures"
                    )
                ))
    
    return results
