from croniter import croniter
from pendulum import DateTime, duration

class CronOperations:
    def __init__(self, cron_expressions):
        self.cron_expressions = cron_expressions


    def __union_prev(self, start: DateTime):
        crons = [
            croniter(expr, start) for expr in self.cron_expressions
        ]
        next_iterations = [
            cron.get_prev(DateTime) for cron in crons
        ]
        return max(next_iterations)

    def __union_next(self, start: DateTime):
        crons = [
            croniter(expr, start) for expr in self.cron_expressions
        ]
        next_iterations = [
            cron.get_next(DateTime) for cron in crons
        ]
        return min(next_iterations)

    # Main union method
    def union(self, start: DateTime, past=False):
        if past:
            return self.__union_prev(start)
        else:
            return self.__union_next(start)

    # Still causing weird behaviour - skipping some exceptions
    def __difference_prev(self, start: DateTime):
        target, excluded = self.cron_expressions[0], self.cron_expressions[1:]

        if excluded:
            max_iteration = start + duration(days=30)
            while start < max_iteration:
                target_cron = croniter(target, start)
                next_iteration = target_cron.get_prev(DateTime)

                excluded_iterations = [
                    croniter(expr, start).get_next(DateTime) for expr in excluded
                ]
                latest_exclusion = max(excluded_iterations)
                print(next_iteration, latest_exclusion)

                if next_iteration < latest_exclusion:
                    validated = next_iteration not in excluded_iterations
                    if validated:
                        return next_iteration
                    else:
                        start = next_iteration
                else:
                    start = latest_exclusion
        else:
            return croniter(target, start).get_prev(DateTime)

        raise Exception("No intersection was found using difference strategy.")

    def __difference_next(self, start: DateTime):
        target, excluded = self.cron_expressions[0], self.cron_expressions[1:]

        if excluded:
            max_iteration = start + duration(days=30)
            while start < max_iteration:
                target_cron = croniter(target, start)
                next_iteration = target_cron.get_next(DateTime)

                excluded_iterations = [
                    croniter(expr, start).get_next(DateTime) for expr in excluded
                ]
                earliest_exclusion = min(excluded_iterations)

                if next_iteration < earliest_exclusion:
                    validated = next_iteration not in excluded_iterations
                    if validated:
                        return next_iteration
                    else:
                        start = next_iteration
                else:
                    start = earliest_exclusion
        else:
            return croniter(target, start).get_next(DateTime)

        raise Exception("No intersection was found using difference strategy.")

    # Main difference method
    def difference(self, start: DateTime, past=False):
        if past:
            return self.__difference_prev(start)
        else:
            return self.__difference_next(start)
