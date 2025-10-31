"""
Configuration for DAG linting rules and thresholds.
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


@dataclass
class LintConfig:
    """Configuration for DAG linting."""
    
    # Parsing performance thresholds (in seconds)
    max_parsing_time_warning: float = 5.0
    max_parsing_time_error: float = 10.0
    
    # Parsing resource thresholds (memory in MB)
    max_parsing_memory_mb_warning: float = 100.0
    max_parsing_memory_mb_error: float = 500.0
    
    # Task configuration requirements
    min_retries: int = 1
    max_retries_warning: int = 5
    recommended_retry_delay: int = 300  # 5 minutes
    
    # Timeout requirements
    require_execution_timeout: bool = True
    min_execution_timeout: int = 300  # 5 minutes
    max_execution_timeout_warning: int = 86400  # 24 hours
    
    # Sensor configuration
    sensor_modes: List[str] = None
    sensor_poke_interval_min: int = 30
    sensor_timeout_min: int = 600  # 10 minutes
    
    # Connection validation
    check_connection_existence: bool = True
    
    # DAG configuration
    require_tags: bool = True
    require_doc_md: bool = False
    require_default_args: bool = True
    require_catchup_false: bool = True
    
    # Task group best practices
    max_tasks_without_group: int = 10
    
    # Operator whitelist/blacklist
    whitelisted_operators: List[str] = field(default_factory=list)
    blacklisted_operators: List[str] = field(default_factory=list)
    operator_whitelist_enabled: bool = False
    operator_blacklist_enabled: bool = True
    
    # Check enable/disable flags
    enabled_check_categories: Set[str] = field(default_factory=lambda: {"parsing", "tasks", "sensors", "connections", "dags"})
    disabled_checks: Set[str] = field(default_factory=set)
    
    # Exclusions
    exclude_dags: List[str] = field(default_factory=list)
    exclude_folders: List[str] = field(default_factory=list)
    include_examples: bool = False
    
    def __post_init__(self):
        """Initialize default values."""
        if self.sensor_modes is None:
            self.sensor_modes = ["poke", "reschedule"]
    
    def is_check_enabled(self, check_name: str) -> bool:
        """Check if a specific check is enabled."""
        return check_name not in self.disabled_checks
    
    def is_category_enabled(self, category: str) -> bool:
        """Check if a check category is enabled."""
        return category in self.enabled_check_categories
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'LintConfig':
        """Load configuration from YAML file.
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            LintConfig instance with values from YAML
        """
        config_path = Path(yaml_path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {yaml_path}. Using defaults.")
            return cls()
        
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
        
        if not yaml_config:
            logger.warning(f"Empty config file: {yaml_path}. Using defaults.")
            return cls()
        
        # Extract values from YAML structure
        config_kwargs = {}
        enabled_categories = set()
        disabled_checks = set()
        
        # Parsing configuration
        if yaml_config.get('parsing', {}).get('enabled', True):
            enabled_categories.add('parsing')
            parsing = yaml_config.get('parsing', {}).get('checks', {})
            
            if parsing.get('parsing_time', {}).get('enabled', True):
                config_kwargs['max_parsing_time_warning'] = parsing.get('parsing_time', {}).get('warning_threshold', 5.0)
                config_kwargs['max_parsing_time_error'] = parsing.get('parsing_time', {}).get('error_threshold', 10.0)
            else:
                disabled_checks.add('parsing_time')
            
            if not parsing.get('import_errors', {}).get('enabled', True):
                disabled_checks.add('import_errors')
            if not parsing.get('dags_per_file', {}).get('enabled', True):
                disabled_checks.add('dags_per_file')
        
        # Task configuration
        if yaml_config.get('tasks', {}).get('enabled', True):
            enabled_categories.add('tasks')
            tasks = yaml_config.get('tasks', {}).get('checks', {})
            
            if tasks.get('retries', {}).get('enabled', True):
                config_kwargs['min_retries'] = tasks.get('retries', {}).get('min_retries', 1)
                config_kwargs['max_retries_warning'] = tasks.get('retries', {}).get('max_retries_warning', 5)
            else:
                disabled_checks.add('task_retries')
            
            if tasks.get('retry_delay', {}).get('enabled', True):
                config_kwargs['recommended_retry_delay'] = tasks.get('retry_delay', {}).get('recommended_delay', 300)
            else:
                disabled_checks.add('retry_delay')
            
            if tasks.get('execution_timeout', {}).get('enabled', True):
                config_kwargs['require_execution_timeout'] = tasks.get('execution_timeout', {}).get('require_timeout', True)
                config_kwargs['min_execution_timeout'] = tasks.get('execution_timeout', {}).get('min_timeout', 300)
            else:
                disabled_checks.add('execution_timeout')
            
            if not tasks.get('concurrency', {}).get('enabled', True):
                disabled_checks.add('task_concurrency')
            if not tasks.get('pool_usage', {}).get('enabled', True):
                disabled_checks.add('pool_usage')
            
            # Operator whitelist/blacklist
            operator_check = tasks.get('operator_whitelist_blacklist', {})
            if operator_check.get('enabled', True):
                config_kwargs['operator_whitelist_enabled'] = operator_check.get('whitelist_enabled', False)
                config_kwargs['operator_blacklist_enabled'] = operator_check.get('blacklist_enabled', True)
                config_kwargs['whitelisted_operators'] = operator_check.get('whitelisted_operators', [])
                config_kwargs['blacklisted_operators'] = operator_check.get('blacklisted_operators', [])
            else:
                disabled_checks.add('operator_whitelist_blacklist')
        
        # Read operators section (alternative location)
        if 'operators' in yaml_config:
            operators = yaml_config['operators']
            config_kwargs['operator_whitelist_enabled'] = operators.get('whitelist_enabled', False)
            config_kwargs['operator_blacklist_enabled'] = operators.get('blacklist_enabled', True)
            config_kwargs['whitelisted_operators'] = operators.get('whitelisted_operators', [])
            config_kwargs['blacklisted_operators'] = operators.get('blacklisted_operators', [])
        
        # Sensor configuration
        if yaml_config.get('sensors', {}).get('enabled', True):
            enabled_categories.add('sensors')
            sensors = yaml_config.get('sensors', {}).get('checks', {})
            
            if sensors.get('poke_interval', {}).get('enabled', True):
                config_kwargs['sensor_poke_interval_min'] = sensors.get('poke_interval', {}).get('min_poke_interval', 30)
            else:
                disabled_checks.add('sensor_poke_interval')
            
            if sensors.get('sensor_timeout', {}).get('enabled', True):
                config_kwargs['sensor_timeout_min'] = sensors.get('sensor_timeout', {}).get('min_timeout', 600)
            else:
                disabled_checks.add('sensor_timeout')
            
            if not sensors.get('sensor_mode', {}).get('enabled', True):
                disabled_checks.add('sensor_mode')
            if not sensors.get('soft_fail', {}).get('enabled', True):
                disabled_checks.add('sensor_soft_fail')
        
        # Connection checks
        if yaml_config.get('connections', {}).get('enabled', True):
            enabled_categories.add('connections')
            connections = yaml_config.get('connections', {}).get('checks', {})
            
            if connections.get('connection_exists', {}).get('enabled', True):
                config_kwargs['check_connection_existence'] = True
            else:
                disabled_checks.add('connection_exists')
            
            if not connections.get('hardcoded_credentials', {}).get('enabled', True):
                disabled_checks.add('hardcoded_credentials')
            if not connections.get('test_on_failure', {}).get('enabled', True):
                disabled_checks.add('test_on_failure')
        
        # DAG configuration
        if yaml_config.get('dags', {}).get('enabled', True):
            enabled_categories.add('dags')
            dags = yaml_config.get('dags', {}).get('checks', {})
            
            if dags.get('tags', {}).get('enabled', True):
                config_kwargs['require_tags'] = dags.get('tags', {}).get('require_tags', True)
            else:
                disabled_checks.add('dag_tags')
            
            if dags.get('documentation', {}).get('enabled', True):
                config_kwargs['require_doc_md'] = dags.get('documentation', {}).get('require_doc_md', False)
            else:
                disabled_checks.add('dag_documentation')
            
            if dags.get('catchup', {}).get('enabled', True):
                config_kwargs['require_catchup_false'] = dags.get('catchup', {}).get('require_catchup_false', True)
            else:
                disabled_checks.add('dag_catchup')
            
            if not dags.get('start_date', {}).get('enabled', True):
                disabled_checks.add('dag_start_date')
            if not dags.get('schedule_interval', {}).get('enabled', True):
                disabled_checks.add('dag_schedule')
            if not dags.get('default_args', {}).get('enabled', True):
                disabled_checks.add('dag_default_args')
            if not dags.get('dag_id_naming', {}).get('enabled', True):
                disabled_checks.add('dag_id_naming')
        
        # General settings
        general = yaml_config.get('general', {})
        config_kwargs['exclude_dags'] = general.get('exclude_dags', [])
        config_kwargs['exclude_folders'] = general.get('exclude_folders', [])
        config_kwargs['include_examples'] = general.get('include_examples', False)
        
        # Set enabled categories and disabled checks
        config_kwargs['enabled_check_categories'] = enabled_categories
        config_kwargs['disabled_checks'] = disabled_checks
        
        logger.info(f"Loaded configuration from {yaml_path}")
        logger.info(f"Enabled categories: {enabled_categories}")
        if disabled_checks:
            logger.info(f"Disabled checks: {disabled_checks}")
        
        return cls(**config_kwargs)


# Default configuration instance
DEFAULT_CONFIG = LintConfig()


def get_config() -> LintConfig:
    """Get the default linting configuration."""
    return DEFAULT_CONFIG
