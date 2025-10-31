#!/usr/bin/env python3
"""
DAG Linting CLI Script

Run this script inside the Airflow scheduler container to analyze
DAGs for best practices and potential issues.

Usage:
    python dags/lint_dags.py [--format console|json|markdown] [--output FILE]
    
Examples:
    # Print results to console
    python dags/lint_dags.py
    
    # Save results as JSON
    python dags/lint_dags.py --format json --output lint_report.json
    
    # Save results as Markdown
    python dags/lint_dags.py --format markdown --output LINT_REPORT.md
    
    # Customize configuration
    python dags/lint_dags.py --max-parsing-time 3.0 --require-tags
"""

import argparse
import sys
import os
from pathlib import Path

# Add dags folder to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.dag_linter import DagLinter
from utils.dag_linter.config import LintConfig
from utils.dag_linter.reporters import (
    ConsoleReporter,
    JSONReporter,
    MarkdownReporter
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Lint Airflow DAGs for best practices",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Output options
    parser.add_argument(
        "--format",
        choices=["console", "json", "markdown"],
        default="console",
        help="Output format (default: console)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (default: print to stdout)"
    )
    
    # Configuration file
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to YAML configuration file (overrides defaults)"
    )
    
    # DAG loading options
    parser.add_argument(
        "--dag-folder",
        type=str,
        help="Path to DAG folder (default: Airflow's configured dag_folder)"
    )
    parser.add_argument(
        "--include-examples",
        action="store_true",
        help="Include Airflow example DAGs in linting"
    )
    
    # Configuration overrides
    parser.add_argument(
        "--max-parsing-time",
        type=float,
        help="Maximum acceptable parsing time in seconds (warning threshold)"
    )
    parser.add_argument(
        "--require-tags",
        action="store_true",
        help="Require all DAGs to have tags"
    )
    parser.add_argument(
        "--require-doc",
        action="store_true",
        help="Require all DAGs to have documentation"
    )
    parser.add_argument(
        "--min-retries",
        type=int,
        help="Minimum number of retries required for tasks"
    )
    
    # Filtering options
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Only show errors, ignore warnings and info"
    )
    parser.add_argument(
        "--severity",
        choices=["ERROR", "WARNING", "INFO"],
        help="Only show issues of this severity or higher"
    )
    
    # Report type
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Generate raw (detailed) report instead of summary report"
    )
    
    return parser.parse_args()


def create_config(args) -> LintConfig:
    """Create linting configuration from arguments."""
    # Load from YAML if provided, otherwise use defaults
    if args.config:
        print(f"Loading configuration from: {args.config}", file=sys.stderr)
        config = LintConfig.from_yaml(args.config)
    else:
        config = LintConfig()
    
    # Override config with command-line arguments (CLI args take precedence)
    if args.max_parsing_time is not None:
        config.max_parsing_time_warning = args.max_parsing_time
    
    if args.require_tags:
        config.require_tags = True
    
    if args.require_doc:
        config.require_doc_md = True
    
    if args.min_retries is not None:
        config.min_retries = args.min_retries
    
    if args.include_examples:
        config.include_examples = True
    
    return config


def main():
    """Main entry point."""
    args = parse_args()
    
    # Create configuration
    config = create_config(args)
    
    # Create linter and run checks
    print("Initializing DAG linter...", file=sys.stderr)
    linter = DagLinter(
        dag_folder=args.dag_folder,
        config=config,
        include_examples=args.include_examples
    )
    
    print("Running lint checks...", file=sys.stderr)
    report = linter.run_all_checks()
    
    # Filter results if requested
    if args.errors_only:
        from utils.dag_linter.models import LintSeverity
        report.results = [
            r for r in report.results 
            if r.severity == LintSeverity.ERROR
        ]
        report.total_issues = len(report.results)
    
    # Generate output
    print("Generating report...", file=sys.stderr)
    
    if args.output:
        # Generate either raw or summary report (mutually exclusive)
        output_path = Path(args.output)
        
        # Determine report type
        use_raw = args.raw
        report_type = "raw" if use_raw else "summary"
        
        print(f"Generating {report_type} report...", file=sys.stderr)
        
        with open(output_path, 'w') as output_file:
            if args.format == "json":
                if use_raw:
                    JSONReporter.write_report(report, output_file)
                else:
                    # JSON summary uses raw format (JSON is already structured)
                    JSONReporter.write_report(report, output_file)
            elif args.format == "markdown":
                if use_raw:
                    MarkdownReporter.write_report(report, output_file)
                else:
                    output_file.write(MarkdownReporter.format_summary_report(report))
            else:  # console format not supported for file output
                if use_raw:
                    output_file.write(ConsoleReporter.format_report(report))
                else:
                    output_file.write(ConsoleReporter.format_summary_report(report))
        
        print(f"Report written to: {output_path}", file=sys.stderr)
    
    else:
        # Console output - always print summary
        if args.format == "json":
            import json
            print(json.dumps(JSONReporter.format_report(report), indent=2))
        elif args.format == "markdown":
            print(MarkdownReporter.format_summary_report(report))
        else:  # console
            print(ConsoleReporter.format_summary_report(report))
    
    # Exit with error code if critical issues found
    if report.errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
