"""
Example usage patterns for the DAG Linter.
"""

from utils.dag_linter import DagLinter
from utils.dag_linter.config import LintConfig
from utils.dag_linter.models import LintSeverity, LintCategory
from utils.dag_linter.reporters import ConsoleReporter, JSONReporter, MarkdownReporter


def example_basic_usage():
    """Basic linting with default configuration."""
    print("=" * 80)
    print("Example 1: Basic Usage")
    print("=" * 80)
    
    # Create linter with defaults
    linter = DagLinter()
    
    # Run all checks
    report = linter.run_all_checks()
    
    # Print to console
    ConsoleReporter.print_report(report)


def example_custom_config():
    """Linting with custom configuration."""
    print("=" * 80)
    print("Example 2: Custom Configuration")
    print("=" * 80)
    
    # Create custom config
    config = LintConfig(
        max_parsing_time_warning=3.0,
        max_parsing_time_error=7.0,
        min_retries=2,
        require_tags=True,
        require_doc_md=True,
        require_catchup_false=True
    )
    
    # Create linter with custom config
    linter = DagLinter(config=config)
    
    # Run checks and get report
    report = linter.run_all_checks()
    
    # Print summary
    summary = report.get_summary()
    print(f"Total DAGs: {summary['total_dags']}")
    print(f"Total Issues: {summary['total_issues']}")
    print(f"  - Errors: {summary['errors']}")
    print(f"  - Warnings: {summary['warnings']}")
    print(f"  - Info: {summary['infos']}")


def example_filter_results():
    """Filter lint results by severity and category."""
    print("=" * 80)
    print("Example 3: Filtering Results")
    print("=" * 80)
    
    linter = DagLinter()
    report = linter.run_all_checks()
    
    # Get only errors
    errors = report.filter_by_severity(LintSeverity.ERROR)
    print(f"\nFound {len(errors)} errors:")
    for error in errors:
        print(f"  - {error}")
    
    # Get only parsing issues
    parsing_issues = report.filter_by_category(LintCategory.PARSING)
    print(f"\nFound {len(parsing_issues)} parsing issues:")
    for issue in parsing_issues:
        print(f"  - {issue}")


def example_export_formats():
    """Export reports in different formats."""
    print("=" * 80)
    print("Example 4: Export Formats")
    print("=" * 80)
    
    linter = DagLinter()
    report = linter.run_all_check()
    
    # Export as JSON
    with open('/tmp/lint_report.json', 'w') as f:
        JSONReporter.write_report(report, f)
    print("JSON report written to /tmp/lint_report.json")
    
    # Export as Markdown
    with open('/tmp/lint_report.md', 'w') as f:
        MarkdownReporter.write_report(report, f)
    print("Markdown report written to /tmp/lint_report.md")
    
    # Console output
    print("\nConsole output:")
    ConsoleReporter.print_report(report)


def example_specific_dag_folder():
    """Lint DAGs from a specific folder."""
    print("=" * 80)
    print("Example 5: Specific DAG Folder")
    print("=" * 80)
    
    # Lint only DAGs from a specific subfolder
    linter = DagLinter(dag_folder="/path/to/specific/dags")
    
    report = linter.run_all_checks()
    ConsoleReporter.print_report(report)


def example_analyze_specific_issues():
    """Analyze specific types of issues."""
    print("=" * 80)
    print("Example 6: Analyze Specific Issues")
    print("=" * 80)
    
    linter = DagLinter()
    report = linter.run_all_checks()
    
    # Find DAGs with parsing issues
    print("\nDAGs with slow parsing:")
    for result in report.filter_by_category(LintCategory.PARSING):
        if result.metric_value and result.metric_value > 5:
            print(f"  - {result.dag_id}: {result.metric_value:.2f}s")
    
    # Find tasks without retries
    print("\nTasks without retries:")
    for result in report.results:
        if "no retries" in result.message.lower():
            print(f"  - {result.dag_id}.{result.task_id}")
    
    # Find missing connections
    print("\nMissing connections:")
    for result in report.filter_by_category(LintCategory.CONNECTIONS):
        if result.severity == LintSeverity.ERROR:
            print(f"  - {result.message}")


def example_integration_ci_cd():
    """Example for CI/CD integration."""
    import sys
    
    print("=" * 80)
    print("Example 7: CI/CD Integration")
    print("=" * 80)
    
    linter = DagLinter()
    report = linter.run_all_checks()
    
    # Export for CI artifacts
    with open('/tmp/dag_lint_report.json', 'w') as f:
        JSONReporter.write_report(report, f)
    
    # Print summary
    summary = report.get_summary()
    print(f"\nLint Summary:")
    print(f"  Errors: {summary['errors']}")
    print(f"  Warnings: {summary['warnings']}")
    
    # Exit with appropriate code
    if summary['errors'] > 0:
        print("\n❌ Linting failed with errors!")
        sys.exit(1)
    elif summary['warnings'] > 5:
        print("\n⚠️  Too many warnings!")
        sys.exit(1)
    else:
        print("\n✅ All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    # Run examples
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples = {
            "1": example_basic_usage,
            "2": example_custom_config,
            "3": example_filter_results,
            "4": example_export_formats,
            "5": example_specific_dag_folder,
            "6": example_analyze_specific_issues,
            "7": example_integration_ci_cd,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Unknown example: {example_num}")
            print(f"Available examples: {', '.join(examples.keys())}")
    else:
        print("Usage: python examples.py [1-7]")
        print("\nAvailable examples:")
        print("  1: Basic Usage")
        print("  2: Custom Configuration")
        print("  3: Filtering Results")
        print("  4: Export Formats")
        print("  5: Specific DAG Folder")
        print("  6: Analyze Specific Issues")
        print("  7: CI/CD Integration")
