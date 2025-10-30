"""
Data models for DAG linting results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class LintSeverity(str, Enum):
    """Severity levels for lint findings."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class LintCategory(str, Enum):
    """Categories for lint checks."""
    PARSING = "PARSING"
    TASK_CONFIG = "TASK_CONFIG"
    CONNECTIONS = "CONNECTIONS"
    SENSORS = "SENSORS"
    DAG_CONFIG = "DAG_CONFIG"
    PERFORMANCE = "PERFORMANCE"


@dataclass
class LintResult:
    """Represents a single lint finding."""
    
    dag_id: str
    category: LintCategory
    severity: LintSeverity
    message: str
    task_id: Optional[str] = None
    file_path: Optional[str] = None
    metric_value: Optional[Any] = None
    recommendation: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the lint result."""
        task_info = f" [Task: {self.task_id}]" if self.task_id else ""
        return f"[{self.severity.value}] {self.dag_id}{task_info}: {self.message}"


@dataclass
class LintReport:
    """Aggregated lint report for all DAGs."""
    
    results: List[LintResult] = field(default_factory=list)
    total_dags_checked: int = 0
    total_issues: int = 0
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    
    def add_result(self, result: LintResult) -> None:
        """Add a lint result to the report."""
        self.results.append(result)
        self.total_issues += 1
        
        if result.severity == LintSeverity.ERROR:
            self.errors += 1
        elif result.severity == LintSeverity.WARNING:
            self.warnings += 1
        elif result.severity == LintSeverity.INFO:
            self.infos += 1
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics."""
        return {
            "total_dags": self.total_dags_checked,
            "total_issues": self.total_issues,
            "errors": self.errors,
            "warnings": self.warnings,
            "infos": self.infos,
        }
    
    def filter_by_severity(self, severity: LintSeverity) -> List[LintResult]:
        """Filter results by severity level."""
        return [r for r in self.results if r.severity == severity]
    
    def filter_by_category(self, category: LintCategory) -> List[LintResult]:
        """Filter results by category."""
        return [r for r in self.results if r.category == category]
