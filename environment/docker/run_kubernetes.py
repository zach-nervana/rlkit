"""
create job
stream related job/pod kubernetes events
stream pod logs
"""

import yaml
import json
from kubernetes import client, config, watch
from string import Template
import tqdm

import utils
from watch_kubernetes import watch_events
import docker_util


def load_job_dict(name, **kwargs):
    template = Template(open("cpu_job.yaml").read())
    return yaml.load(template.substitute(name=name, **kwargs))


def set_environment(job_dict, environment):
    container = job_dict["spec"]["template"]["spec"]["containers"][0]
    try:
        container["env"]
    except KeyError:
        container["env"] = []

    job_environment = container["env"]
    for k, v in environment.items():
        job_environment.append({"name": str(k), "value": str(v)})


def run(command=None, environment=None):
    """
    command: string
    environment: dict
    """
    if command is not None:
        utils.project_config["command"] = command

    utils.project_config["command_list"] = utils.project_config["command"].split()

    job_dict = load_job_dict(
        **utils.project_config, **utils.project_config["kubernetes"]
    )

    if environment is not None:
        set_environment(job_dict, environment)

    # utils.print_path(job_dict, "job_dict")
    response = utils.batch.create_namespaced_job(
        body=job_dict, namespace=utils.project_config["kubernetes"]["namespace"]
    )
    return response.metadata.name

def delete_jobs():
    namespace = utils.project_config["kubernetes"]["namespace"]
    jobs = utils.batch.list_namespaced_job(namespace)
    for job in tqdm.tqdm(jobs.items):
        try:
            utils.batch.delete_namespaced_job(job.metadata.name, namespace=namespace, body=client.V1DeleteOptions())
        except Exception as e:
            print(e)

def delete_pods(name):
    namespace = utils.project_config["kubernetes"]["namespace"]
    print('delete pods')
    pods = utils.api_instance.list_namespaced_pod(namespace)
    for pod in tqdm.tqdm(pods.items):
        if name not in pod.metadata.name:
            continue
        try:
            utils.api_instance.delete_namespaced_pod(pod.metadata.name, namespace=namespace, body=client.V1DeleteOptions())
        except Exception as e:
            print(e)
