"""
Reporting utilities for lint results.
"""

import json
from typing import Dict, TextIO
from collections import defaultdict

from .models import LintReport, LintSeverity, LintCategory


class ConsoleReporter:
    """Format lint reports for console output."""
    
    @staticmethod
    def format_report(report: LintReport) -> str:
        """
        Format a lint report for console output.
        
        Args:
            report: LintReport to format
            
        Returns:
            Formatted string
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("DAG LINTING REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        summary = report.get_summary()
        lines.append(f"Total DAGs checked: {summary['total_dags']}")
        lines.append(f"Total issues found: {summary['total_issues']}")
        lines.append("")
        lines.append(f"  Errors:   {summary['errors']}")
        lines.append(f"  Warnings: {summary['warnings']}")
        lines.append(f"  Info:     {summary['infos']}")
        lines.append("")
        
        if report.total_issues == 0:
            lines.append("✓ No issues found! All DAGs follow best practices.")
            lines.append("=" * 80)
            return "\n".join(lines)
        
        # Group results by DAG
        results_by_dag = defaultdict(list)
        for result in report.results:
            results_by_dag[result.dag_id].append(result)
        
        # Sort DAGs by number of issues (most issues first)
        sorted_dags = sorted(results_by_dag.items(), key=lambda x: len(x[1]), reverse=True)
        
        lines.append("-" * 80)
        lines.append("ISSUES BY DAG")
        lines.append("-" * 80)
        lines.append("")
        
        for dag_id, dag_results in sorted_dags:
            # Count severity for this DAG
            dag_errors = sum(1 for r in dag_results if r.severity == LintSeverity.ERROR)
            dag_warnings = sum(1 for r in dag_results if r.severity == LintSeverity.WARNING)
            dag_infos = sum(1 for r in dag_results if r.severity == LintSeverity.INFO)
            
            lines.append(f"📋 {dag_id}")
            lines.append(f"   Total issues: {len(dag_results)} (Errors: {dag_errors}, Warnings: {dag_warnings}, Info: {dag_infos})")
            lines.append("")
            
            # Group by severity within this DAG
            for severity in [LintSeverity.ERROR, LintSeverity.WARNING, LintSeverity.INFO]:
                severity_results = [r for r in dag_results if r.severity == severity]
                if not severity_results:
                    continue
                
                for result in severity_results:
                    lines.extend(ConsoleReporter._format_result(result, indent="   "))
            
            lines.append("-" * 80)
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_result(result, indent="") -> list:
        """Format a single lint result."""
        lines = []
        
        # Severity emoji
        emoji = "❌" if result.severity == LintSeverity.ERROR else "⚠️" if result.severity == LintSeverity.WARNING else "ℹ️"
        
        # Main message
        task_info = f" → {result.task_id}" if result.task_id else ""
        lines.append(f"{indent}{emoji} {result.category.value}{task_info}")
        lines.append(f"{indent}   {result.message}")
        
        # Metric value if present
        if result.metric_value is not None:
            lines.append(f"{indent}   Value: {result.metric_value}")
        
        # Recommendation
        if result.recommendation:
            lines.append(f"{indent}   💡 {result.recommendation}")
        
        lines.append("")
        
        return lines
    
    @staticmethod
    def print_report(report: LintReport) -> None:
        """Print report to console."""
        print(ConsoleReporter.format_report(report))
    
    @staticmethod
    def format_summary_report(report: LintReport) -> str:
        """
        Format a summary report grouping similar issues together.
        
        Args:
            report: LintReport to format
            
        Returns:
            Formatted summary string
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("DAG LINTING SUMMARY REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        summary = report.get_summary()
        lines.append(f"Total DAGs checked: {summary['total_dags']}")
        lines.append(f"Total issues found: {summary['total_issues']}")
        lines.append("")
        lines.append(f"  Errors:   {summary['errors']}")
        lines.append(f"  Warnings: {summary['warnings']}")
        lines.append(f"  Info:     {summary['infos']}")
        lines.append("")
        
        if report.total_issues == 0:
            lines.append("✓ No issues found! All DAGs follow best practices.")
            lines.append("=" * 80)
            return "\n".join(lines)
        
        # Group results by issue signature (category + message)
        issues_grouped = defaultdict(list)
        for result in report.results:
            # Create issue key from category, severity, and base message
            issue_key = (result.category, result.severity, result.message, result.recommendation or "")
            issues_grouped[issue_key].append(result)
        
        # Sort by severity and count
        def sort_key(item):
            category, severity, message, rec = item[0]
            count = len(item[1])
            severity_order = {LintSeverity.ERROR: 0, LintSeverity.WARNING: 1, LintSeverity.INFO: 2}
            return (severity_order[severity], -count)
        
        sorted_issues = sorted(issues_grouped.items(), key=sort_key)
        
        lines.append("-" * 80)
        lines.append("ISSUES GROUPED BY TYPE")
        lines.append("-" * 80)
        lines.append("")
        
        for (category, severity, message, recommendation), results in sorted_issues:
            # Severity emoji
            emoji = "❌" if severity == LintSeverity.ERROR else "⚠️" if severity == LintSeverity.WARNING else "ℹ️"
            
            # Issue header
            lines.append(f"{emoji} {severity.value} - {category.value}")
            lines.append(f"   {message}")
            
            # Determine if this is a DAG-level or task-level issue
            has_tasks = any(r.task_id for r in results)
            unique_dags = len(set(r.dag_id for r in results))
            
            if has_tasks:
                lines.append(f"   Affected: {len(results)} task(s) across {unique_dags} DAG(s)")
                lines.append("")
                lines.append("   Tasks:")
            else:
                lines.append(f"   Affected: {unique_dags} DAG(s)")
                lines.append("")
                lines.append("   DAGs:")
            
            # Group by DAG for inline display
            results_by_dag = defaultdict(list)
            for result in results:
                results_by_dag[result.dag_id].append(result)
            
            if has_tasks:
                # Show DAG with tasks as comma-separated list
                for dag_id in sorted(results_by_dag.keys()):
                    dag_results = results_by_dag[dag_id]
                    task_names = sorted([r.task_id for r in dag_results if r.task_id])
                    tasks_str = ", ".join(task_names)
                    lines.append(f"     {dag_id} -> {tasks_str}")
            else:
                # DAG-level issue, show as comma-separated list
                for dag_id in sorted(results_by_dag.keys()):
                    lines.append(f"     {dag_id}")
            
            # Recommendation
            if recommendation:
                lines.append("")
                lines.append(f"   💡 {recommendation}")
            
            lines.append("")
            lines.append("-" * 80)
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)


class JSONReporter:
    """Format lint reports as JSON."""
    
    @staticmethod
    def format_report(report: LintReport) -> Dict:
        """
        Format a lint report as JSON-serializable dict, grouped by DAG.
        
        Args:
            report: LintReport to format
            
        Returns:
            Dictionary representation
        """
        # Group results by DAG
        results_by_dag = defaultdict(list)
        for result in report.results:
            results_by_dag[result.dag_id].append({
                "task_id": result.task_id,
                "category": result.category.value,
                "severity": result.severity.value,
                "message": result.message,
                "file_path": result.file_path,
                "metric_value": result.metric_value,
                "recommendation": result.recommendation,
            })
        
        # Create DAG-grouped structure
        dags = []
        for dag_id, issues in sorted(results_by_dag.items()):
            dag_errors = sum(1 for i in issues if i["severity"] == "ERROR")
            dag_warnings = sum(1 for i in issues if i["severity"] == "WARNING")
            dag_infos = sum(1 for i in issues if i["severity"] == "INFO")
            
            dags.append({
                "dag_id": dag_id,
                "total_issues": len(issues),
                "errors": dag_errors,
                "warnings": dag_warnings,
                "infos": dag_infos,
                "issues": issues
            })
        
        return {
            "summary": report.get_summary(),
            "dags": dags
        }
    
    @staticmethod
    def write_report(report: LintReport, file: TextIO) -> None:
        """Write report as JSON to file."""
        json.dump(
            JSONReporter.format_report(report),
            file,
            indent=2
        )


class MarkdownReporter:
    """Format lint reports as Markdown."""
    
    @staticmethod
    def format_report(report: LintReport) -> str:
        """
        Format a lint report as Markdown.
        
        Args:
            report: LintReport to format
            
        Returns:
            Markdown formatted string
        """
        lines = []
        
        # Header
        lines.append("# DAG Linting Report")
        lines.append("")
        
        # Summary
        summary = report.get_summary()
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total DAGs checked:** {summary['total_dags']}")
        lines.append(f"- **Total issues found:** {summary['total_issues']}")
        lines.append(f"  - Errors: {summary['errors']}")
        lines.append(f"  - Warnings: {summary['warnings']}")
        lines.append(f"  - Info: {summary['infos']}")
        lines.append("")
        
        if report.total_issues == 0:
            lines.append("✅ **No issues found!** All DAGs follow best practices.")
            return "\n".join(lines)
        
        # Group results by DAG
        results_by_dag = defaultdict(list)
        for result in report.results:
            results_by_dag[result.dag_id].append(result)
        
        # Sort DAGs by number of issues (most issues first)
        sorted_dags = sorted(results_by_dag.items(), key=lambda x: len(x[1]), reverse=True)
        
        lines.append("## Issues by DAG")
        lines.append("")
        
        for dag_id, dag_results in sorted_dags:
            # Count severity for this DAG
            dag_errors = sum(1 for r in dag_results if r.severity == LintSeverity.ERROR)
            dag_warnings = sum(1 for r in dag_results if r.severity == LintSeverity.WARNING)
            dag_infos = sum(1 for r in dag_results if r.severity == LintSeverity.INFO)
            
            lines.append(f"### 📋 {dag_id}")
            lines.append("")
            lines.append(f"**Total issues:** {len(dag_results)} (❌ {dag_errors} errors, ⚠️ {dag_warnings} warnings, ℹ️ {dag_infos} info)")
            lines.append("")
            
            # Group by category within this DAG
            category_groups = defaultdict(list)
            for result in dag_results:
                category_groups[result.category].append(result)
            
            for category, category_results in sorted(category_groups.items(), key=lambda x: x[0].value):
                lines.append(f"#### {category.value}")
                lines.append("")
                
                for result in category_results:
                    emoji = "❌" if result.severity == LintSeverity.ERROR else "⚠️" if result.severity == LintSeverity.WARNING else "ℹ️"
                    task_info = f" → `{result.task_id}`" if result.task_id else ""
                    
                    lines.append(f"{emoji} **{result.severity.value}**{task_info}")
                    lines.append(f"   - {result.message}")
                    if result.recommendation:
                        lines.append(f"   - 💡 {result.recommendation}")
                    lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def write_report(report: LintReport, file: TextIO) -> None:
        """Write report as Markdown to file."""
        file.write(MarkdownReporter.format_report(report))
    
    @staticmethod
    def format_summary_report(report: LintReport) -> str:
        """
        Format a summary report grouping similar issues together.
        
        Args:
            report: LintReport to format
            
        Returns:
            Markdown formatted summary string
        """
        lines = []
        
        # Header
        lines.append("# DAG Linting Summary Report")
        lines.append("")
        
        # Summary
        summary = report.get_summary()
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total DAGs checked:** {summary['total_dags']}")
        lines.append(f"- **Total issues found:** {summary['total_issues']}")
        lines.append(f"  - Errors: {summary['errors']}")
        lines.append(f"  - Warnings: {summary['warnings']}")
        lines.append(f"  - Info: {summary['infos']}")
        lines.append("")
        
        if report.total_issues == 0:
            lines.append("✅ **No issues found!** All DAGs follow best practices.")
            return "\n".join(lines)
        
        # Group results by issue signature
        issues_grouped = defaultdict(list)
        for result in report.results:
            issue_key = (result.category, result.severity, result.message, result.recommendation or "")
            issues_grouped[issue_key].append(result)
        
        # Sort by severity and count
        def sort_key(item):
            category, severity, message, rec = item[0]
            count = len(item[1])
            severity_order = {LintSeverity.ERROR: 0, LintSeverity.WARNING: 1, LintSeverity.INFO: 2}
            return (severity_order[severity], -count)
        
        sorted_issues = sorted(issues_grouped.items(), key=sort_key)
        
        lines.append("## Issues Grouped by Type")
        lines.append("")
        
        for (category, severity, message, recommendation), results in sorted_issues:
            emoji = "❌" if severity == LintSeverity.ERROR else "⚠️" if severity == LintSeverity.WARNING else "ℹ️"
            
            # Issue header
            lines.append(f"### {emoji} {severity.value} - {category.value}")
            lines.append("")
            lines.append(f"**Message:** {message}")
            lines.append("")
            
            # Determine if this is a DAG-level or task-level issue
            has_tasks = any(r.task_id for r in results)
            unique_dags = len(set(r.dag_id for r in results))
            
            if has_tasks:
                lines.append(f"**Affected:** {len(results)} task(s) across {unique_dags} DAG(s)")
                lines.append("")
                lines.append("**Tasks:**")
            else:
                lines.append(f"**Affected:** {unique_dags} DAG(s)")
                lines.append("")
                lines.append("**DAGs:**")
            
            lines.append("")
            
            # Group by DAG for hierarchical display
            results_by_dag = defaultdict(list)
            for result in results:
                results_by_dag[result.dag_id].append(result)
            
            if has_tasks:
                # Show DAG with tasks as comma-separated list
                for dag_id in sorted(results_by_dag.keys()):
                    dag_results = results_by_dag[dag_id]
                    task_names = sorted([r.task_id for r in dag_results if r.task_id])
                    tasks_str = ", ".join(task_names)
                    lines.append(f"**{dag_id}** -> {tasks_str}")
                    lines.append("")
            else:
                # DAG-level issue, list each DAG on separate line
                for dag_id in sorted(results_by_dag.keys()):
                    lines.append(f"{dag_id}")
                    lines.append("")
            
            # Recommendation
            if recommendation:
                lines.append("")
                lines.append(f"**💡 Recommendation:** {recommendation}")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
