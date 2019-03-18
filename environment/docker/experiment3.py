"""
TODO: hyper-parameter set status screen of some kind: % complete each job, % jobs started, % jobs waiting, etc.
"""
import datetime
import random
import itertools

import docker_util
import run_kubernetes
import watch_kubernetes

from flexible_robotics.environments import time_constants
from utils import get_env_name

docker_util.build()
docker_util.push()

TAIL_LOGS = False

envs = ("FlexibleReacher", "FlexibleReacherStay", "FlexibleStriker", "FlexibleThrower")
date_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
for train_env_name, test_env_name in itertools.product(envs, repeat=2):
    for sensor_selection in ("withIMU", "withoutIMU"):
        # setting experiment name for particular env
        EXPERIMENT_NAME = "experiment3-{}-{}-{}-{}".format(
            train_env_name, test_env_name, sensor_selection, date_string
        )

        for n in range(10):
            for time_constant in time_constants:
                level = get_env_name(
                    train_env_name, time_constant, sensor_selection, eval=False
                )
                eval_level = get_env_name(
                    test_env_name, time_constant, sensor_selection, eval=True
                )

                job_name = run_kubernetes.run(
                    command="python3 /root/flexible_robotics/flexible_robotics/agents/coach_script_ddpg.py --experiment_name {experiment_name}".format(
                        experiment_name=EXPERIMENT_NAME
                    ),
                    environment={"level": level, "eval_level": eval_level},
                )

                # hack to not tail all logs ... job_name should accept a list
                if random.random() < 0.1:
                    watch_kubernetes.watch_events(
                        job_name, tail_events=True, tail_logs=TAIL_LOGS
                    )
