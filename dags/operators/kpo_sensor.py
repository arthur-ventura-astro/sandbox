from airflow.exceptions import AirflowException
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sensors.base import BaseSensorOperator

class KubernetesPodSensor(BaseSensorOperator, KubernetesPodOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def poke(self, context):
        result = None
        try:
            result = KubernetesPodOperator.execute(self, context)
            return result["sensor_result"]
        except AirflowException:
            # not too sure why this is needed, following the video tutorial above
            if result is not None:
                self.logger.info(f'Sensor returned result: {result["sensor_result"]}.')
            raise
