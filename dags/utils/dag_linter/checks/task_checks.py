"""
Task configuration checks for best practices.
"""

from typing import List

from ..compat import DAG, BaseOperator, BaseSensorOperator
from ..compat import get_task_retries, get_task_execution_timeout, get_task_concurrency
from ..models import LintResult, LintSeverity, LintCategory
from ..config import LintConfig


def check_task_retries(task: BaseOperator, dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check if a task has appropriate retry configuration.
    
    Args:
        task: Airflow task instance
        dag: Airflow DAG instance (for dag_id)
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    # Check if retries are configured (version-agnostic)
    retries = get_task_retries(task)
    
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


def check_task_timeouts(task: BaseOperator, dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check if a task has execution timeout configured.
    
    Args:
        task: Airflow task instance
        dag: Airflow DAG instance (for dag_id)
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    # Get execution timeout (version-agnostic)
    execution_timeout = get_task_execution_timeout(task)
    
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


def check_task_concurrency(task: BaseOperator, dag: DAG) -> List[LintResult]:
    """
    Check if a task has concurrency limits that might cause bottlenecks.
    
    Args:
        task: Airflow task instance
        dag: Airflow DAG instance (for dag_id)
        
    Returns:
        List of lint results
    """
    results = []
    
    # Get task concurrency (version-agnostic)
    max_active = get_task_concurrency(task)
    if max_active and max_active == 1:
        results.append(LintResult(
            dag_id=dag.dag_id,
            task_id=task.task_id,
            category=LintCategory.TASK_CONFIG,
            severity=LintSeverity.INFO,
            message="Task has concurrency limit of 1 which may cause bottlenecks",
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


def check_operator_whitelist_blacklist(task: BaseOperator, dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check if a task uses only whitelisted operators or avoids blacklisted operators.
    
    Args:
        task: Airflow task instance
        dag: Airflow DAG instance (for dag_id)
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    # Get the operator class name
    operator_class = task.__class__.__name__
    operator_module = task.__class__.__module__
    
    # Full operator path for more precise matching
    full_operator_path = f"{operator_module}.{operator_class}"
    
    # Check blacklist
    if config.operator_blacklist_enabled and config.blacklisted_operators:
        for blacklisted in config.blacklisted_operators:
            # Support both simple class name and full module path
            if (blacklisted == operator_class or 
                blacklisted == full_operator_path or
                blacklisted in full_operator_path):
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.TASK_CONFIG,
                    severity=LintSeverity.ERROR,
                    message=f"Task uses blacklisted operator: {operator_class}",
                    recommendation=(
                        f"Replace '{operator_class}' with an approved operator. "
                        f"Blacklisted operators are not allowed in this environment."
                    )
                ))
                break  # Only report once per task
    
    # Check whitelist (only if enabled)
    if config.operator_whitelist_enabled and config.whitelisted_operators:
        is_whitelisted = False
        
        for whitelisted in config.whitelisted_operators:
            # Support both simple class name and full module path
            if (whitelisted == operator_class or 
                whitelisted == full_operator_path or
                whitelisted in full_operator_path):
                is_whitelisted = True
                break
        
        if not is_whitelisted:
            results.append(LintResult(
                dag_id=dag.dag_id,
                task_id=task.task_id,
                category=LintCategory.TASK_CONFIG,
                severity=LintSeverity.ERROR,
                message=f"Task uses non-whitelisted operator: {operator_class}",
                recommendation=(
                    f"Only whitelisted operators are allowed. "
                    f"Replace '{operator_class}' with an approved operator from the whitelist."
                )
            ))
    
    return results
