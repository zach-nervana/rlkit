import os
import json
from string import Template

import yaml
import kubernetes
import urllib3
import lazy_object_proxy

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def print_path(object, prefix=""):
    if isinstance(object, dict):
        for k, v in object.items():
            print_path(v, "{prefix}['{k}']".format(**locals()))
    elif isinstance(object, list):
        for i, v in enumerate(object):
            print_path(v, "{prefix}[{i}]".format(**locals()))
    else:
        object_json = json.dumps(object)
        print("{prefix} = {object_json}".format(**locals()))


project_config = yaml.load(open("config.yaml"))
project_config["user"] = project_config.get("user", os.environ["USER"])
project_config["registry_user"] = project_config.get(
    "registry_user", project_config["user"]
)
project_config["image_name"] = (
    project_config["name"].replace(" ", "_").replace("-", "_")
)
project_config["full_image_name"] = "{}/{}/{}:latest".format(
    project_config["registry"], project_config["registry_user"], project_config["name"]
)
# print_path(project_config, "project_config")

kubernetes.config.load_kube_config()


def connect_batch():
    return kubernetes.client.BatchV1Api()


def connect_core():
    kubernetes.config.load_kube_config()
    return kubernetes.client.CoreV1Api()


batch = lazy_object_proxy.Proxy(connect_batch)
api_instance = lazy_object_proxy.Proxy(connect_core)
