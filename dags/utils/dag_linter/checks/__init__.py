"""
DAG linting check modules.
"""

from .parsing_checks import (
    check_parsing_time,
    check_import_errors,
    check_dag_count_per_file,
    check_parsing_resources,
)
from .task_checks import (
    check_task_retries,
    check_task_timeouts,
    check_task_concurrency,
    check_task_pools,
    check_operator_whitelist_blacklist,
)
from .sensor_checks import (
    check_sensor_mode,
    check_sensor_timeouts,
    check_sensor_poke_interval,
    check_sensor_soft_fail,
)
from .connection_checks import (
    check_connection_existence,
    check_hardcoded_credentials,
    check_connection_test_on_failure,
)
from .dag_checks import (
    check_dag_tags,
    check_dag_documentation,
    check_catchup_configuration,
    check_start_date,
    check_schedule_interval,
    check_default_args,
    check_dag_id_naming,
)

__all__ = [
    # Parsing checks
    "check_parsing_time",
    "check_import_errors",
    "check_dag_count_per_file",
    "check_parsing_resources",
    # Task checks
    "check_task_retries",
    "check_task_timeouts",
    "check_task_concurrency",
    "check_task_pools",
    "check_operator_whitelist_blacklist",
    # Sensor checks
    "check_sensor_mode",
    "check_sensor_timeouts",
    "check_sensor_poke_interval",
    "check_sensor_soft_fail",
    # Connection checks
    "check_connection_existence",
    "check_hardcoded_credentials",
    "check_connection_test_on_failure",
    # DAG checks
    "check_dag_tags",
    "check_dag_documentation",
    "check_catchup_configuration",
    "check_start_date",
    "check_schedule_interval",
    "check_default_args",
    "check_dag_id_naming",
]
