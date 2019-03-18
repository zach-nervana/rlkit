import os
import json
import atexit

import docker

import utils

# client = docker.from_env()
client = docker.DockerClient(base_url="unix://var/run/docker.sock")
low_level_client = docker.APIClient(base_url="unix://var/run/docker.sock")


def system(command):
    print(command)
    os.system(command)


def buildargs():
    ret = {}
    if "http_proxy" in os.environ:
        ret["http_proxy"] = os.environ["http_proxy"]
    if "https_proxy" in os.environ:
        ret["https_proxy"] = os.environ["https_proxy"]
    return ret


def guess_build_context(path):
    if path == "/":
        return None

    path = os.path.abspath(path)
    if os.path.exists(os.path.join(path, ".dockerignore")):
        return path
    elif os.path.exists(os.path.join(path, ".git")):
        return path
    else:
        return guess_build_context(os.path.abspath(path + "/../"))


def make_relative_path(path, relative_to):
    assert relative_to == path[: len(relative_to)]
    return path[len(relative_to) + 1 :]


def guess_dockerfile_path(build_context):
    """
    assumes that the dockerfile is in the same directory as this file
    """
    return make_relative_path(
        os.path.abspath(__file__ + "/../Dockerfile"), build_context
    )


def build():
    if utils.project_config["build_context"]:
        build_context = utils.project_config["build_context"]
        if build_context[0] != "/":
            build_context = os.path.abspath(__file__ + "/" + build_context)
    else:
        build_context = guess_build_context(__file__)

    dockerfile_path = guess_dockerfile_path(build_context)
    print("dockerfile_path", dockerfile_path)
    print("build_context", build_context)
    print("building", utils.project_config["image_name"])
    line_generator = low_level_client.build(
        path=build_context,
        dockerfile=dockerfile_path,
        tag=utils.project_config["image_name"],
        buildargs=buildargs(),
    )
    for raw_line in line_generator:
        try:
            line = json.loads(raw_line.decode("utf-8"))
        except json.JSONDecodeError:
            line = raw_line.decode("utf-8")
            continue

        if "stream" in line:
            print(line["stream"], flush=True, end="")
        elif "error" in line:
            print(line["error"], flush=True, end="")
            raise ValueError(line["error"])
        else:
            print(line, flush=True, end="")


def run(command=None, remove=True):
    print("running", utils.project_config["image_name"])
    container = client.containers.create(
        utils.project_config["image_name"],
        command or utils.project_config["command"],
        volumes={
            utils.project_config["image_name"]: {
                "bind": "/home/experiments",
                "mode": "rw",
            }
        },
    )
    atexit.register(lambda: client.container.prune, utils.project_config["image_name"])
    container.start()
    for line in container.logs(stream=True):
        print(line.decode("utf-8"), flush=True, end="")


def push():
    os.system(
        "docker tag {image_name} {full_image_name}".format(**utils.project_config)
    )
    # print(client.images.push(utils.project_config["image"]))
    ret = os.system("docker push {}".format(utils.project_config["full_image_name"]))
    print(ret)
    assert ret == 0, "return value was {}, expected 0".format(ret)


def make_volume():
    # TODO: should this be remote nfs home or local home?
    local_experiments = os.path.expanduser("/dataset/experiments")
    experiments_volume = utils.project_config["image_name"]

    system("mkdir {local_experiments}".format(**locals()))
    system("chmod a+w {local_experiments}".format(**locals()))
    system("docker volume rm {experiments_volume}".format(**locals()))
    # docker volume create --name ${EXPERIMENTS} --opt type=nfs --opt device=:/nrv_algo_home01/${USER}/experiments --opt o=addr=fmcfs05n02b-03.fm.intel.com
    # uncomment when running locally:
    system(
        "docker volume create --name {experiments_volume} -o type=none -o device={local_experiments} -o o=bind".format(
            **locals()
        )
    )
