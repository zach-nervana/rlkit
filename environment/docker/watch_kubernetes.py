import os
import time
import json
from multiprocessing import Process
from string import Template
import functools

import yaml
from kubernetes import client, config, watch
import urllib3

import utils
from print_colorful import print_colorful


def _tail_log(pod_name):
    try:
        while True:
            time.sleep(1)
            # Try to tail the pod logs
            try:
                for line in utils.api_instance.read_namespaced_pod_log(
                    pod_name,
                    utils.project_config["kubernetes"]["namespace"],
                    follow=True,
                    _preload_content=False,
                ):
                    print_colorful(pod_name, line.decode("utf-8"), flush=True, end="")
            except client.rest.ApiException as e:
                pass

            # This part will get executed if the pod is one of the following phases: not ready, failed or terminated.
            # Check if the pod has errored out, else just try again.
            # Get the pod
            try:
                pod = utils.api_instance.read_namespaced_pod(
                    pod_name, utils.project_config["kubernetes"]["namespace"]
                )
            except client.rest.ApiException as e:
                continue

            if not hasattr(pod, "status") or not pod.status:
                continue
            if (
                not hasattr(pod.status, "container_statuses")
                or not pod.status.container_statuses
            ):
                continue

            for container_status in pod.status.container_statuses:
                if container_status.state.waiting is not None:
                    if (
                        container_status.state.waiting.reason == "Error"
                        or container_status.state.waiting.reason == "CrashLoopBackOff"
                        or container_status.state.waiting.reason == "ImagePullBackOff"
                        or container_status.state.waiting.reason == "ErrImagePull"
                    ):
                        return
                if container_status.state.terminated is not None:
                    return
    except KeyboardInterrupt:
        pass


def tail_log(name):
    p = Process(target=_tail_log, args=(name,))
    p.start()
    return p


def event_stream(name, source):
    w = watch.Watch()
    # print("event_stream", name)
    api_instance = utils.connect_core()
    namespace = utils.project_config["kubernetes"]["namespace"]
    # for event in w.stream(utils.api_instance.list_event_for_all_namespaces):
    for event in w.stream(functools.partial(utils.api_instance.list_namespaced_event, namespace, limit=500)):
        if event["object"]["involvedObject"]["name"] != name:
            continue

        yield event


def _watch_events(name, tail_events, tail_logs, on_container_started=None):
    try:
        for event in event_stream(name, "subprocess"):
            if tail_events:
                print_colorful(
                    name,
                    "{}: {}".format(
                        event["object"]["involvedObject"]["name"], event["object"]["message"]
                    ),
                )

            if event["object"]["message"][:13] == "Created pod: ":
                pod_name = event["object"]["message"][13:]
                watch_events(pod_name, tail_events, tail_logs, on_container_started)
                print("tail_log", pod_name)

                if tail_logs:
                    print("tail_log", pod_name)
                    tail_log(pod_name)

            if on_container_started:
                if event["object"]["message"] == "Started container":
                    on_container_started(name)
    except KeyboardInterrupt:
        pass
    except urllib3.exceptions.ProtocolError as e:
        print(e)


def watch_events(
    name, tail_events, tail_logs, on_container_started=None, subprocess=True
):
    """
    Nonblocking call to watch events coming from objects with `name`
    """
    if subprocess:
        p = Process(
            target=_watch_events,
            args=(name, tail_events, tail_logs, on_container_started),
        )
        p.start()
    else:
        _watch_events(name, tail_events, tail_logs, on_container_started)


# for event in batch.list_namespaced_job(project_config["kubernetes"]["namespace"], watch=True):
#     print(event)

# w = watch.Watch()
# for event in w.stream(api_instance.list_pod_for_all_namespaces):
#     # print("Event: %s %s %s" % (event['type'],event['object'].kind, event['object'].metadata.name))
#     if event['object'].metadata.namespace != project_config['kubernetes']['namespace']:
#         continue
#
#     print("Event: %s %s %s" % (event['type'],event['object'].kind, event['object'].metadata.name))

# import pykube
#
# api = pykube.HTTPClient(pykube.KubeConfig.from_file(os.path.expanduser("~/.kube/config")))
# watch = pykube.Job.objects(api, namespace=project_config['kubernetes']['namespace'])
# watch = watch.filter(field_selector={'metadata.name': "flexible-robotics-job-67z7g"}).watch()
#
# # watch is a generator:
# for watch_event in watch:
#     print(watch_event)
#     print(dir(watch_event.object))
#     print(watch_event.object.objects)
