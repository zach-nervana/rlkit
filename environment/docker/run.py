#!/usr/bin/env python
"""
./run.py (--local | --kubernetes) (--shell | --run | --hyper | --notebook) [--no-build] [--watch]

TODO:

- [ ] rename top level files: docker_util, run_kubernetes, watch_kubernetes
- [ ] stream build logs
- [ ] allow including source as volume mount
"""
import os

# import atexit

import click

import utils
import docker_util
import run_kubernetes
import watch_kubernetes


def run(command):
    print(command)
    os.system(command)


@click.command()
@click.option("--local", "executor", flag_value="local")
@click.option("--kubernetes", "executor", flag_value="kubernetes", default=True)
@click.option("--run", "execute", flag_value="run", default=True)
@click.option("--shell", "execute", flag_value="shell")
@click.option("--hyper", "execute", flag_value="hyper")
@click.option("--notebook", "execute", flag_value="notebook")
@click.option("--build/--no-build", default=True)
@click.option("--watch/--no-watch", default=False)
@click.option("--rm/--no-rm", default=True)
@click.option("--command", default=None)
def main(executor, execute, build, watch, rm, command):
    if build:
        docker_util.build()

    if watch:
        raise NotImplementedError()

    if executor == "local":
        docker_util.make_volume()
        if execute == "run":
            docker_util.run(command=command, remove=rm)
            print("done")
        elif execute == "shell":
            # TODO: figure out why docker_util.run('/bin/bash') does not work
            # docker_util.run('/bin/9h')
            # if command is None:
            utils.project_config['command'] = "/bin/bash"
            run(
                'docker run {remove} -v {image_name}:/home/experiments -it {image_name} "{command}"'.format(
                    remove="--rm" if rm else "", **utils.project_config
                )
            )
        elif execute == "hyper":
            raise NotImplementedError()
        elif execute == "notebook":
            raise NotImplementedError()
    elif executor == "kubernetes":
        docker_util.push()

        if execute == "run":
            job_name = run_kubernetes.run(command=command)
            watch_kubernetes.watch_events(job_name, tail_events=True, tail_logs=True)
        elif execute == "shell":
            print("shell")
            if command is None:
                command = "/bin/bash"
            job_name = run_kubernetes.run(
                command="sleep {}".format(60 * 60 * 24 * 365),
                environment={"hello": "hello"},
            )
            watch_kubernetes.watch_events(job_name, tail_events=True, tail_logs=False)
            watch_kubernetes.watch_events(
                job_name,
                tail_events=False,
                tail_logs=False,
                subprocess=False,
                on_container_started=lambda pod_name: run(
                    'kubectl exec -it {pod_name} -- {command}'.format(
                        pod_name=pod_name, command=command
                    )
                ),
            )
            # TODO: exit after system command
        elif execute == "hyper":
            if execute == "run":
                job_name = run_kubernetes.run()
                watch_kubernetes.watch_events(
                    job_name, tail_events=True, tail_logs=False
                )
        elif execute == "notebook":
            raise NotImplementedError()

        # TODO: implement --rm : delete job on process exit


if __name__ == "__main__":
    main()
