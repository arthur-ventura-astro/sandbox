"""
DAG-level configuration checks.
"""

from typing import List

from airflow.models import DAG
from ..models import LintResult, LintSeverity, LintCategory
from ..config import LintConfig


def check_dag_tags(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check if DAG has tags for organization.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    if not config.require_tags:
        return results
    
    if not dag.tags or len(dag.tags) == 0:
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.DAG_CONFIG,
            severity=LintSeverity.WARNING,
            message="DAG has no tags defined",
            recommendation="Add tags to organize and filter DAGs in the UI"
        ))
    
    return results


def check_dag_documentation(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check if DAG has documentation.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    # Check for doc_md or description
    has_doc = False
    
    if hasattr(dag, 'doc_md') and dag.doc_md:
        has_doc = True
    elif hasattr(dag, 'description') and dag.description:
        has_doc = True
    
    if not has_doc and config.require_doc_md:
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.DAG_CONFIG,
            severity=LintSeverity.INFO,
            message="DAG has no documentation (doc_md or description)",
            recommendation="Add doc_md or description to explain the DAG's purpose"
        ))
    
    return results


def check_catchup_configuration(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check catchup configuration to avoid unexpected backfills.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    if not config.require_catchup_false:
        return results
    
    if dag.catchup:
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.DAG_CONFIG,
            severity=LintSeverity.WARNING,
            message="DAG has catchup=True which may cause unexpected backfills",
            recommendation=(
                "Set catchup=False unless you specifically need to backfill "
                "historical runs"
            )
        ))
    
    return results


def check_start_date(dag: DAG) -> List[LintResult]:
    """
    Check start_date configuration best practices.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        List of lint results
    """
    results = []
    
    if dag.start_date is None:
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.DAG_CONFIG,
            severity=LintSeverity.ERROR,
            message="DAG has no start_date defined",
            recommendation="Define a start_date for the DAG"
        ))
    else:
        # Check if start_date is timezone-aware
        if dag.start_date.tzinfo is None:
            results.append(LintResult(
                dag_id=dag.dag_id,
                category=LintCategory.DAG_CONFIG,
                severity=LintSeverity.WARNING,
                message="DAG start_date is not timezone-aware",
                recommendation="Use timezone-aware datetime (e.g., pendulum.datetime)"
            ))
    
    return results


def check_schedule_interval(dag: DAG) -> List[LintResult]:
    """
    Check schedule_interval configuration.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        List of lint results
    """
    results = []
    
    schedule = dag.schedule_interval
    
    if schedule is None and not hasattr(dag, 'dataset_triggers'):
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.DAG_CONFIG,
            severity=LintSeverity.INFO,
            message="DAG has schedule=None (manual trigger only)",
            recommendation=(
                "Verify this is intentional. Consider using @once, dataset "
                "triggers, or a cron schedule"
            )
        ))
    
    return results


def check_default_args(dag: DAG, config: LintConfig) -> List[LintResult]:
    """
    Check if DAG has default_args configured.
    
    Args:
        dag: Airflow DAG instance
        config: Linting configuration
        
    Returns:
        List of lint results
    """
    results = []
    
    if not config.require_default_args:
        return results
    
    recommended_defaults = [
        'owner',
        'retries',
        'retry_delay',
    ]
    
    default_args = dag.default_args or {}
    
    missing_args = [arg for arg in recommended_defaults if arg not in default_args]
    
    if missing_args:
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.DAG_CONFIG,
            severity=LintSeverity.INFO,
            message=f"DAG missing recommended default_args: {', '.join(missing_args)}",
            recommendation=(
                "Define default_args with owner, retries, and retry_delay "
                "for consistent task behavior"
            )
        ))
    
    return results


def check_dag_id_naming(dag: DAG) -> List[LintResult]:
    """
    Check DAG ID naming conventions.
    
    Args:
        dag: Airflow DAG instance
        
    Returns:
        List of lint results
    """
    results = []
    
    dag_id = dag.dag_id
    
    # Check for spaces in DAG ID
    if ' ' in dag_id:
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.DAG_CONFIG,
            severity=LintSeverity.ERROR,
            message="DAG ID contains spaces",
            recommendation="Use underscores or hyphens instead of spaces in DAG IDs"
        ))
    
    # Check for uppercase letters (convention is lowercase with underscores)
    if dag_id != dag_id.lower():
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.DAG_CONFIG,
            severity=LintSeverity.INFO,
            message="DAG ID contains uppercase letters",
            recommendation="Consider using lowercase with underscores for consistency"
        ))
    
    # Check for very long DAG IDs
    if len(dag_id) > 50:
        results.append(LintResult(
            dag_id=dag.dag_id,
            category=LintCategory.DAG_CONFIG,
            severity=LintSeverity.INFO,
            message=f"DAG ID is very long ({len(dag_id)} characters)",
            recommendation="Consider using a shorter, more concise DAG ID"
        ))
    
    return results
