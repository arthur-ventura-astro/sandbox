# Base on Avi's MultiCronTimeTable
# Reference: https://github.com/astronomer/coe-airflow-plugins/blob/main/plugins/multicron_timetable/timetable.py

from typing import Any, Optional

from airflow.exceptions import AirflowTimetableInvalid
from airflow.plugins_manager import AirflowPlugin
from airflow.timetables.base import DagRunInfo, DataInterval, TimeRestriction, Timetable
from multicron.cron_operations import CronOperations
from croniter import croniter
from pendulum import now, timezone, timezones

STRATEGIES = [
    "+", # gets multiple cron expressions and get the union of them
    "-" # gets multiple cron expressions using the first as base, taking the difference between the base and all the other expressions (exceptions)
]


class MultiCronTimetable(Timetable):
    def __init__(
        self,
        cron_list: list[str],
        timezone: str = "UTC",
        strategy: str = "-",
        description: Optional[str] = None,
    ):
        self.cron_list = cron_list
        self.timezone = timezone
        self.strategy = strategy
        self.description = description
        self.operations_manager = CronOperations(cron_list)

        # Validate inputs
        self.validate()
        self._set_strategy()

    def serialize(self) -> dict[str, Any]:
        return {
            "cron_list": self.cron_list,
            "timezone": self.timezone,
            "strategy": self.strategy,
            "description": self.description
        }

    @classmethod
    def deserialize(cls, value: dict[str, Any]) -> Timetable:
        return cls(
            value["cron_list"], 
            value["timezone"],
            value["strategy"],
            value["description"]    
        )

    @property
    def summary(self) -> str:
        return self.description or str(self.cron_list)

    def _set_strategy(self):
        strategies = {
            '+': self.operations_manager.union,
            'union': self.operations_manager.union,
            '-': self.operations_manager.difference,
            'diff': self.operations_manager.difference
        }
        self._handle_overlaps = strategies.get(self.strategy)

    def next_dagrun_info(
        self,
        *,
        last_automated_data_interval: DataInterval | None,
        restriction: TimeRestriction,
    ) -> DagRunInfo | None:
        tz = timezone(self.timezone)

        if last_automated_data_interval is None:
            next_start_utc = restriction.earliest
            if next_start_utc is None:  # No start_date. Don't schedule.
                return None
            if not restriction.catchup: # If the DAG has catchup=False, we consider past valid schedule based on today.
                next_start_utc = self._handle_overlaps(
                    max(next_start_utc, now(tzinfo=tz)),
                    past=True
                )
                next_start_utc = self._handle_overlaps(
                    next_start_utc, past=True
                )
            else:
                next_start_utc = self._handle_overlaps(
                    min(next_start_utc, now(tzinfo=tz)),
                    past=True
                )
        else:
            next_start_utc = last_automated_data_interval.end

        next_start_tz = tz.convert(next_start_utc)
        # Apply overlap strategy
        next_end_tz = self._handle_overlaps(next_start_tz)

        # Handle DST transitions
        if next_end_tz.fold != next_start_tz.fold:
            # Adjust for DST change
            dst_delta = tz.convert(next_end_tz) - tz.convert(next_start_tz)
            next_end_tz = next_start_tz + dst_delta

        if restriction.latest and next_start_tz > restriction.latest:
            return None

        return DagRunInfo.interval(start=next_start_tz, end=next_end_tz)

    def validate(self) -> None:
        if not self.cron_list:
            raise AirflowTimetableInvalid("Cron list cannot be empty")

        if not all(croniter.is_valid(cron) for cron in self.cron_list):
            raise AirflowTimetableInvalid(f"Invalid cron schedule(s): {self.cron_list}")

        if not all(len(cron.split()) == 5 for cron in self.cron_list):
            raise AirflowTimetableInvalid("All cron expressions must be in 5-part format")

        if self.strategy not in STRATEGIES:
            raise AirflowTimetableInvalid(f"Invalid overlap strategy: {self.strategy}")

        if self.timezone not in timezones():
            raise AirflowTimetableInvalid(f"Timezone `{self.timezone}` is not a valid pendulum timezone")

class MultiCronTimetablePlugin(AirflowPlugin):
    name = "multi_cron_timetable_plugin"
    timetables = [MultiCronTimetable]
