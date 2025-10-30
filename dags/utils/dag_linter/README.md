# DAG Linter

A comprehensive linting tool for Apache Airflow DAGs that checks for best practices, performance issues, and common configuration problems.

## Overview

The DAG Linter analyzes your Airflow DAGs using the DagBag API and reports issues across multiple categories:

- **Parsing Performance**: DAG parsing time and import errors
- **Task Configuration**: Retries, timeouts, concurrency settings
- **Sensor Configuration**: Mode, poke intervals, timeouts
- **Connection Management**: Connection existence and credential security
- **DAG Configuration**: Tags, documentation, scheduling, naming conventions

## Features

✅ **Modular Architecture**: Extensible check system with separate modules  
✅ **Multiple Output Formats**: Console, JSON, and Markdown reports  
✅ **YAML Configuration**: Enable/disable checks via configuration files  
✅ **Configurable Rules**: Customize thresholds and requirements  
✅ **Severity Levels**: ERROR, WARNING, and INFO classifications  
✅ **Actionable Recommendations**: Each finding includes remediation guidance  
✅ **Scheduler-Safe**: Runs within Airflow context with access to connections and variables

## Quick Start

### Basic Usage

```bash
# Run from the scheduler container
python dags/lint_dags.py
```

### With Output File

```bash
# Generate JSON report
python dags/lint_dags.py --format json --output lint_report.json

# Generate Markdown report
python dags/lint_dags.py --format markdown --output LINT_REPORT.md
```

### YAML Configuration

```bash
# Create your configuration file
cp dags/utils/dag_linter/lint_config.sample.yaml my_config.yaml

# Edit the config to enable/disable specific checks
# Then run with config
python dags/lint_dags.py --config my_config.yaml

# CLI arguments can override config
python dags/lint_dags.py --config my_config.yaml --max-parsing-time 3.0
```

See [CONFIG_GUIDE.md](CONFIG_GUIDE.md) for detailed configuration options.

### Command Line Configuration

```bash
# Stricter parsing time limits
python dags/lint_dags.py --max-parsing-time 3.0

# Require tags and documentation
python dags/lint_dags.py --require-tags --require-doc

# Show only errors
python dags/lint_dags.py --errors-only
```

## Checks Performed

### Parsing Checks

- **Parsing Time**: Flags DAGs that take too long to parse
- **Import Errors**: Reports DAGs that fail to import
- **DAGs per File**: Warns about files with too many DAGs

### Task Checks

- **Retries**: Ensures tasks have appropriate retry configuration
- **Retry Delay**: Validates retry delay settings
- **Execution Timeout**: Checks for missing or inappropriate timeouts
- **Concurrency**: Identifies potential bottlenecks
- **Pool Usage**: Suggests custom pools for resource management

### Sensor Checks

- **Sensor Mode**: Recommends `reschedule` mode for long-running sensors
- **Poke Interval**: Validates poke interval to avoid overwhelming systems
- **Timeouts**: Checks sensor timeout configuration
- **Soft Fail**: Suggests soft_fail for appropriate sensors

### Connection Checks

- **Connection Existence**: Verifies referenced connections exist
- **Hardcoded Credentials**: Detects potential credential exposure
- **Retry Configuration**: Ensures tasks with connections have retries

### DAG Configuration Checks

- **Tags**: Validates DAGs have organizational tags
- **Documentation**: Checks for doc_md or description
- **Catchup**: Warns about catchup=True to avoid unexpected backfills
- **Start Date**: Validates start_date and timezone awareness
- **Schedule Interval**: Reviews scheduling configuration
- **Default Args**: Ensures recommended default_args are set
- **Naming Conventions**: Validates DAG ID naming patterns

## Configuration

The linter behavior can be customized via `LintConfig`:

```python
from utils.dag_linter.config import LintConfig

config = LintConfig(
    max_parsing_time_warning=5.0,      # Warning threshold in seconds
    max_parsing_time_error=10.0,       # Error threshold in seconds
    min_retries=1,                     # Minimum required retries
    require_execution_timeout=True,    # Require timeouts on tasks
    require_tags=True,                 # Require tags on DAGs
    require_catchup_false=True,        # Warn on catchup=True
    sensor_poke_interval_min=30,       # Minimum sensor poke interval
    check_connection_existence=True,   # Validate connections exist
)
```

## Programmatic Usage

You can also use the linter programmatically:

```python
from utils.dag_linter import DagLinter
from utils.dag_linter.config import LintConfig
from utils.dag_linter.reporters import ConsoleReporter

# Create linter with custom config
config = LintConfig(max_parsing_time_warning=3.0)
linter = DagLinter(config=config)

# Run checks
report = linter.run_all_checks()

# Print results
ConsoleReporter.print_report(report)

# Filter by severity
from utils.dag_linter.models import LintSeverity
errors = report.filter_by_severity(LintSeverity.ERROR)
print(f"Found {len(errors)} errors")

# Filter by category
from utils.dag_linter.models import LintCategory
parsing_issues = report.filter_by_category(LintCategory.PARSING)
```

## Integration with CI/CD

### Exit Codes

The CLI script exits with:
- `0`: No errors found (warnings/info only)
- `1`: One or more errors found

### Example GitHub Actions

```yaml
- name: Lint Airflow DAGs
  run: |
    python dags/lint_dags.py --format json --output lint_report.json
  
- name: Upload Lint Report
  uses: actions/upload-artifact@v3
  with:
    name: dag-lint-report
    path: lint_report.json
```

### Example Pre-commit Hook

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: dag-lint
      name: Lint Airflow DAGs
      entry: python dags/lint_dags.py --errors-only
      language: system
      pass_filenames: false
```

## Extending the Linter

### Adding Custom Checks

Create a new check function in the appropriate module:

```python
# dags/utils/dag_linter/checks/custom_checks.py

def check_custom_requirement(dag_bag, config):
    """Check for custom requirement."""
    results = []
    
    for dag in dag_bag.dags.values():
        # Your check logic here
        if not meets_requirement(dag):
            results.append(LintResult(
                dag_id=dag.dag_id,
                category=LintCategory.DAG_CONFIG,
                severity=LintSeverity.WARNING,
                message="Custom requirement not met",
                recommendation="Fix the requirement"
            ))
    
    return results
```

Register it in the linter:

```python
# dags/utils/dag_linter/linter.py

def _run_dag_checks(self):
    results = []
    # ... existing checks ...
    results.extend(check_custom_requirement(self.dag_bag, self.config))
    return results
```

## Best Practices

1. **Run Regularly**: Integrate into CI/CD or run on a schedule
2. **Address Errors First**: Focus on ERROR severity issues before warnings
3. **Customize Thresholds**: Adjust config to match your organization's standards
4. **Document Exceptions**: If you need to ignore specific warnings, document why
5. **Monitor Trends**: Track lint metrics over time to measure code quality

## Troubleshooting

### "Connection not found" errors

The connection check requires access to Airflow's metadata database. Ensure you're running within the scheduler container where connections are available.

To disable connection checks:
```python
config = LintConfig(check_connection_existence=False)
```

### High parsing times reported

This often indicates:
- Heavy imports at the top level
- Expensive API calls or database queries in DAG file
- Complex dynamic DAG generation

See [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#top-level-python-code) for optimization guidance.

## Architecture

```
dag_linter/
├── __init__.py           # Package exports
├── models.py             # Data models (LintResult, LintReport)
├── config.py             # Configuration classes
├── linter.py             # Main orchestrator
├── reporters.py          # Output formatters
└── checks/               # Check modules
    ├── __init__.py
    ├── parsing_checks.py
    ├── task_checks.py
    ├── sensor_checks.py
    ├── connection_checks.py
    └── dag_checks.py
```

## References

- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Testing DAGs](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#testing-a-dag)
- [DagBag API](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/dagbag/index.html)

## License

Part of the Astronomer sandbox project.
