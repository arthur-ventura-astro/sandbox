"""
Task configuration checks for best practices.
"""

from typing import List

from airflow.models import DAG, BaseOperator
from airflow.sensors.base import BaseSensorOperator
from ..models import LintResult, LintSeverity, LintCategory
from ..config import LintConfig


def check_task_retries(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check if tasks have appropriate retry configuration.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    for task in dag.tasks:
        # Check if retries are configured
        retries = task.retries if task.retries is not None else 0
        
        if retries < config.min_retries:
            results.append(LintResult(
                dag_id=dag.dag_id,
                task_id=task.task_id,
                category=LintCategory.TASK_CONFIG,
                severity=LintSeverity.WARNING,
                message=f"Task has no retries configured (retries={retries})",
                metric_value=retries,
                recommendation=f"Set retries to at least {config.min_retries} for resilience"
            ))
        elif retries > config.max_retries_warning:
            results.append(LintResult(
                dag_id=dag.dag_id,
                task_id=task.task_id,
                category=LintCategory.TASK_CONFIG,
                severity=LintSeverity.WARNING,
                message=f"Task has excessive retries (retries={retries})",
                metric_value=retries,
                recommendation="Consider if this many retries are necessary"
            ))
        
        # Check retry delay
        if retries > 0 and task.retry_delay:
            retry_delay_seconds = task.retry_delay.total_seconds()
            if retry_delay_seconds < 60:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.TASK_CONFIG,
                    severity=LintSeverity.INFO,
                    message=f"Retry delay is very short ({retry_delay_seconds}s)",
                    metric_value=retry_delay_seconds,
                    recommendation="Consider increasing retry_delay to avoid overwhelming systems"
                ))
    
    return results


def check_task_timeouts(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check if tasks have execution timeouts configured.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    for task in dag.tasks:
        execution_timeout = task.execution_timeout
        
        if config.require_execution_timeout and execution_timeout is None:
            # Skip sensor operators as they have their own timeout mechanism
            if not isinstance(task, BaseSensorOperator):
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.TASK_CONFIG,
                    severity=LintSeverity.WARNING,
                    message="Task has no execution timeout configured",
                    recommendation=(
                        f"Set execution_timeout to prevent tasks from running indefinitely. "
                        f"Recommended minimum: {config.min_execution_timeout}s"
                    )
                ))
        elif execution_timeout:
            timeout_seconds = execution_timeout.total_seconds()
            
            if timeout_seconds < config.min_execution_timeout:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.TASK_CONFIG,
                    severity=LintSeverity.WARNING,
                    message=f"Execution timeout is very short ({timeout_seconds}s)",
                    metric_value=timeout_seconds,
                    recommendation="Ensure timeout allows sufficient time for task completion"
                ))
            elif timeout_seconds > config.max_execution_timeout_warning:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.TASK_CONFIG,
                    severity=LintSeverity.INFO,
                    message=f"Execution timeout is very long ({timeout_seconds/3600:.1f} hours)",
                    metric_value=timeout_seconds,
                    recommendation="Consider if such a long timeout is necessary"
                ))
    
    return results


def check_task_concurrency(dag: DAG) -> List[LintResult]:
    """
    Check for tasks with concurrency limits that might cause bottlenecks.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        List of lint results
    """
    results = []
    
    for task in dag.tasks:
        if hasattr(task, 'max_active_tis_per_dag'):
            max_active = task.max_active_tis_per_dag
            if max_active and max_active == 1:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.TASK_CONFIG,
                    severity=LintSeverity.INFO,
                    message="Task has max_active_tis_per_dag=1 which may cause bottlenecks",
                    metric_value=max_active,
                    recommendation="Verify if this restriction is necessary for your use case"
                ))
    
    return results


def check_task_pools(dag: DAG) -> List[LintResult]:
    """
    Check for tasks using default pool which might need resource management.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        List of lint results
    """
    results = []
    
    # Count tasks per pool
    tasks_in_default_pool = 0
    
    for task in dag.tasks:
        if task.pool == 'default_pool':
            tasks_in_default_pool += 1
    
    # If many tasks use default pool, suggest pool organization
    if tasks_in_default_pool > 10:
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.TASK_CONFIG,
            severity=LintSeverity.INFO,
            message=f"{tasks_in_default_pool} tasks using default_pool",
            metric_value=tasks_in_default_pool,
            recommendation="Consider creating custom pools for better resource management"
        ))
    
    return results
