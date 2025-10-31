"""
Main DAG Linter class that orchestrates all checks.
"""

import logging
from typing import Optional, List

from .compat import DagBag
from .models import LintReport, LintResult
from .config import LintConfig, get_config
from . import checks

logger = logging.getLogger(__name__)


class DagLinter:
    """
    Main DAG linting orchestrator.
    
    Runs various checks on DAGs loaded from DagBag and produces
    a comprehensive lint report.
    """
    
    def __init__(
        self,
        dag_folder: Optional[str] = None,
        config: Optional[LintConfig] = None,
        include_examples: bool = False
    ):
        """
        Initialize the DAG linter.
        
        Args:
            dag_folder: Path to DAG folder. If None, uses Airflow default.
            config: Linting configuration. If None, uses defaults.
            include_examples: Whether to include example DAGs in linting.
        """
        self.config = config or get_config()
        self.include_examples = include_examples
        
        # Load DAGs
        logger.info(f"Loading DAGs from folder: {dag_folder or 'default'}")
        self.dag_bag = DagBag(
            dag_folder=dag_folder,
            include_examples=include_examples
        )
        
        logger.info(f"Loaded {len(self.dag_bag.dags)} DAGs")
        
        if self.dag_bag.import_errors:
            logger.warning(
                f"Found {len(self.dag_bag.import_errors)} import errors"
            )
    
    def run_all_checks(self) -> LintReport:
        """
        Run all configured checks on the loaded DAGs.
        
        Returns:
            LintReport with all findings
        """
        report = LintReport()
        report.total_dags_checked = len(self.dag_bag.dags)
        
        logger.info("Starting DAG linting...")
        
        # Run file-level parsing checks first (these don't iterate per DAG)
        if self.config.is_category_enabled("parsing"):
            logger.info("Running parsing checks...")
            results = self._run_parsing_checks()
            for result in results:
                report.add_result(result)
        else:
            logger.info("Parsing checks disabled")
        
        # Iterate once over all DAGs and run per-DAG checks
        logger.info(f"Running per-DAG checks on {len(self.dag_bag.dags)} DAGs...")
        for dag in self.dag_bag.dags.values():
            # Run all enabled check categories for this DAG
            results = self._run_dag_level_checks(dag)
            for result in results:
                report.add_result(result)
        
        logger.info(f"Linting complete. Found {report.total_issues} issues.")
        
        return report
    
    def _run_dag_level_checks(self, dag) -> List[LintResult]:
        """
        Run all enabled checks for a single DAG.
        
        Args:
            dag: Airflow DAG instance
            
        Returns:
            List of lint results for this DAG
        """
        results = []
        
        # Per-task checks - iterate once over all tasks
        if self.config.is_category_enabled("tasks"):
            # Iterate over tasks once and run all per-task checks
            for task in dag.tasks:
                if self.config.is_check_enabled('task_retries'):
                    results.extend(checks.check_task_retries(task, dag, self.config))
                if self.config.is_check_enabled('execution_timeout'):
                    results.extend(checks.check_task_timeouts(task, dag, self.config))
                if self.config.is_check_enabled('task_concurrency'):
                    results.extend(checks.check_task_concurrency(task, dag))
                if self.config.is_check_enabled('operator_whitelist_blacklist'):
                    results.extend(checks.check_operator_whitelist_blacklist(task, dag, self.config))
            
            # DAG-level aggregate task checks (not per-task)
            if self.config.is_check_enabled('pool_usage'):
                results.extend(checks.check_task_pools(dag))
        
        # Sensor checks
        if self.config.is_category_enabled("sensors"):
            if self.config.is_check_enabled('sensor_mode'):
                results.extend(checks.check_sensor_mode(dag, self.config))
            if self.config.is_check_enabled('sensor_timeout'):
                results.extend(checks.check_sensor_timeouts(dag, self.config))
            if self.config.is_check_enabled('sensor_poke_interval'):
                results.extend(checks.check_sensor_poke_interval(dag, self.config))
            if self.config.is_check_enabled('sensor_soft_fail'):
                results.extend(checks.check_sensor_soft_fail(dag))
        
        # Connection checks
        if self.config.is_category_enabled("connections"):
            if self.config.is_check_enabled('connection_exists'):
                try:
                    results.extend(checks.check_connection_existence(dag, self.config))
                except Exception as e:
                    logger.warning(f"Could not check connection existence for {dag.dag_id}: {e}")
            if self.config.is_check_enabled('hardcoded_credentials'):
                results.extend(checks.check_hardcoded_credentials(dag))
            if self.config.is_check_enabled('test_on_failure'):
                results.extend(checks.check_connection_test_on_failure(dag))
        
        # DAG configuration checks
        if self.config.is_category_enabled("dags"):
            if self.config.is_check_enabled('dag_tags'):
                results.extend(checks.check_dag_tags(dag, self.config))
            if self.config.is_check_enabled('dag_documentation'):
                results.extend(checks.check_dag_documentation(dag, self.config))
            if self.config.is_check_enabled('dag_catchup'):
                results.extend(checks.check_catchup_configuration(dag, self.config))
            if self.config.is_check_enabled('dag_start_date'):
                results.extend(checks.check_start_date(dag))
            if self.config.is_check_enabled('dag_schedule'):
                results.extend(checks.check_schedule_interval(dag))
            if self.config.is_check_enabled('dag_default_args'):
                results.extend(checks.check_default_args(dag, self.config))
            if self.config.is_check_enabled('dag_id_naming'):
                results.extend(checks.check_dag_id_naming(dag))
        
        return results
    
    def _run_parsing_checks(self) -> List[LintResult]:
        """Run all parsing-related checks."""
        results = []
        
        if self.config.is_check_enabled('parsing_time'):
            results.extend(checks.check_parsing_time(self.dag_bag, self.config))
        if self.config.is_check_enabled('import_errors'):
            results.extend(checks.check_import_errors(self.dag_bag))
        if self.config.is_check_enabled('dags_per_file'):
            results.extend(checks.check_dag_count_per_file(self.dag_bag))
        if self.config.is_check_enabled('parsing_resources'):
            results.extend(checks.check_parsing_resources(self.dag_bag, self.config))
        
        return results
    
    
    def get_dag_bag(self) -> DagBag:
        """Get the loaded DagBag."""
        return self.dag_bag
