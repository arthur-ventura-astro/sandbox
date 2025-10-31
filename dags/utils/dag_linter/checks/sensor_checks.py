"""
Sensor-specific configuration checks.
"""

from typing import List

from ..compat import DAG, BaseSensorOperator, safe_getattr
from ..models import LintResult, LintSeverity, LintCategory
from ..config import LintConfig


def check_sensor_mode(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check sensor mode configuration for performance.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    for task in dag.tasks:
        if isinstance(task, BaseSensorOperator):
            mode = getattr(task, 'mode', 'poke')
            
            # Recommend reschedule mode for long-running sensors
            if mode == 'poke':
                poke_interval = getattr(task, 'poke_interval', 60)
                timeout = getattr(task, 'timeout', 604800)  # Default 7 days
                
                # If sensor runs for more than 10 minutes, suggest reschedule mode
                if timeout > 600:
                    results.append(LintResult(
                        dag_id=dag.dag_id,
                        task_id=task.task_id,
                        category=LintCategory.SENSORS,
                        severity=LintSeverity.WARNING,
                        message=(
                            f"Sensor using 'poke' mode with long timeout "
                            f"({timeout/3600:.1f}h)"
                        ),
                        metric_value={'mode': mode, 'timeout': timeout},
                        recommendation=(
                            "Use 'reschedule' mode for long-running sensors to free up "
                            "worker slots between pokes"
                        )
                    ))
    
    return results


def check_sensor_timeouts(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check sensor timeout configuration.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    for task in dag.tasks:
        if isinstance(task, BaseSensorOperator):
            timeout = getattr(task, 'timeout', 604800)  # Default 7 days
            
            if timeout < config.sensor_timeout_min:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.SENSORS,
                    severity=LintSeverity.WARNING,
                    message=f"Sensor timeout is very short ({timeout}s)",
                    metric_value=timeout,
                    recommendation=(
                        f"Consider increasing timeout to at least "
                        f"{config.sensor_timeout_min}s"
                    )
                ))
            elif timeout > 86400:  # More than 1 day
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.SENSORS,
                    severity=LintSeverity.INFO,
                    message=f"Sensor has very long timeout ({timeout/3600:.1f}h)",
                    metric_value=timeout,
                    recommendation="Verify if such a long timeout is necessary"
                ))
    
    return results


def check_sensor_poke_interval(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check sensor poke interval configuration.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    for task in dag.tasks:
        if isinstance(task, BaseSensorOperator):
            poke_interval = getattr(task, 'poke_interval', 60)
            
            if poke_interval < config.sensor_poke_interval_min:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.SENSORS,
                    severity=LintSeverity.WARNING,
                    message=f"Sensor poke interval is very short ({poke_interval}s)",
                    metric_value=poke_interval,
                    recommendation=(
                        f"Increase poke_interval to at least "
                        f"{config.sensor_poke_interval_min}s to avoid "
                        "overwhelming external systems"
                    )
                ))
            elif poke_interval < 10:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.SENSORS,
                    severity=LintSeverity.ERROR,
                    message=f"Sensor poke interval is extremely short ({poke_interval}s)",
                    metric_value=poke_interval,
                    recommendation="This may cause performance issues and rate limiting"
                ))
    
    return results


def check_sensor_soft_fail(dag: DAG) -> List[LintResult]:
    """
    Check if sensors have soft_fail enabled when appropriate.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        List of lint results
    """
    results = []
    
    for task in dag.tasks:
        if isinstance(task, BaseSensorOperator):
            soft_fail = getattr(task, 'soft_fail', False)
            timeout = getattr(task, 'timeout', 604800)
            
            # Suggest soft_fail for sensors with long timeouts
            if not soft_fail and timeout > 3600:
                results.append(LintResult(
                    dag_id=dag.dag_id,
                    task_id=task.task_id,
                    category=LintCategory.SENSORS,
                    severity=LintSeverity.INFO,
                    message="Consider enabling soft_fail for long-running sensor",
                    recommendation=(
                        "soft_fail=True allows downstream tasks to skip instead of "
                        "failing when sensor times out"
                    )
                ))
    
    return results
