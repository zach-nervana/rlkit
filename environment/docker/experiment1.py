"""
TODO: hyper-parameter set status screen of some kind: % complete each job, % jobs started, % jobs waiting, etc.
"""
import datetime
import random

import docker_util
import run_kubernetes
import watch_kubernetes
from utils import get_env_name

# avoid requiring flexible_robotics package to be installed which has many requirements just to launch jobs
# from flexible_robotics.environments import time_constants
time_constants = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40)

# docker_util.build()
# docker_util.push()

TAIL_LOGS = False
# date_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
date_string = "2019-02-28-22-17-34"
for env_name in (
    # "FlexibleReacher",
    # "FlexibleReacherStay",
    # "FlexibleStriker2d",
    "FlexibleThrower2d",
    "FlexibleAnt",
):
    for include_joint_angles in (True, False):
        for include_quat in (True, False):
            if not include_joint_angles and not include_quat:
                continue

            # setting experiment name for particular env
            EXPERIMENT_NAME = "{}-{}-{}-{}-{}".format(
                'experiment1', env_name, include_joint_angles, include_quat, date_string
            )

            for n in range(25):
                for time_constant in time_constants:
                    level = get_env_name(
                        env_name,
                        time_constant,
                        include_joint_angles,
                        include_quat,
                        eval=False,
                    )
                    eval_level = get_env_name(
                        env_name,
                        time_constant,
                        include_joint_angles,
                        include_quat,
                        eval=True,
                    )

                    job_name = run_kubernetes.run(
                        command="python3 /root/flexible_robotics/flexible_robotics/agents/coach_script_ddpg.py --experiment_name {experiment_name}".format(
                            experiment_name=EXPERIMENT_NAME
                        ),
                        environment={"level": level, "eval_level": eval_level},
                    )
                    print(job_name, level)

                    # # hack to not tail all logs ... job_name should accept a list
                    # if random.random() < 0.01:
                    #     watch_kubernetes.watch_events(
                    #         job_name, tail_events=True, tail_logs=TAIL_LOGS
                    #     )
