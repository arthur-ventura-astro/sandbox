from pydantic import BaseModel
from enum import IntEnum
from automated_workflows.models.storage import Storage
import json
import shutil
import fileinput
from datetime import datetime


class WorkflowType(IntEnum):
    a = 1
    b = 2


class WorkflowMetadata(BaseModel):
    id: str
    type: WorkflowType
    start: str


class Generator:
    def __init__(self, interval: int = 300):
        self._state_file = "generator-state.json"
        self._storage = Storage()
        self._templates_dir = "./dags/automated_workflows/templates"
        self._workflows_dir = "./dags/automated_workflows/workflows"
        self.interval = interval

        self._state = {}

    def _save_state(self):
        with open(self._state_file, "w") as f:
            f.write(json.dumps(self._state))

    def _read_state(self):
        try:
            with open(self._state_file, "r") as f:
                self._state = json.loads(f.read())
        except:
            pass


    def generate_workflows(self, workflows_config):
        for workflow_metadata in workflows_config:
            workflow = WorkflowMetadata(**workflow_metadata)
            template_filename = f"{self._templates_dir}/workflow_type_{workflow.type}.py"
            workflow_filename = f"{self._workflows_dir}/{workflow.id}_dag.py"
            shutil.copyfile(template_filename, workflow_filename)

            for line in fileinput.input(workflow_filename, inplace=True):
                line = line.replace("$DAG_ID", workflow.id)
                line = line.replace("$DAG_START", workflow.start)
                print(line, end="")


    def routine(self):
        execution_time = datetime.now()

        self._read_state()
        if self._state:
            last_execution = execution_time - datetime.fromtimestamp(self._state["last_execution"])
            if last_execution.total_seconds() > self.interval:
                workflows_config = self._storage.read()
                if workflows_config:
                    self.generate_workflows(workflows_config)
                    self._storage.remove()

        self._state = dict(
            last_execution=execution_time.timestamp()
        )

        self._save_state()

