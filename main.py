# https://github.com/kubernetes-client/python
import os
import sys
import json
import pathlib
import logging
import argparse
import traceback

from kubernetes import config as k8s_config
from kubernetes import client as k8s_client


class TrivyReports:
    def __init__(self) -> None:
        k8s_config.load_kube_config()
        self._core_api = k8s_client.CoreV1Api()
        self._custom_api = k8s_client.CustomObjectsApi()
        self._resource_group = "aquasecurity.github.io"
        self._resource_version = "v1alpha1"
        self._resource_base_dir = pathlib.Path("./reports")

    def get_namespaces(self) -> list:
        logging.debug("Run: get_namespaces()")
        res = self._core_api.list_namespace()
        return [item.metadata.name for item in res.items]

    def get_api_resources(self, namespaced: bool = True) -> list:
        logging.debug("Run: get_api_resources({})".format(namespaced))
        res = self._custom_api.get_api_resources(self._resource_group, self._resource_version)
        res = filter(lambda item: item.namespaced == namespaced, res.resources)
        return list(map(lambda item: item.name, res))

    def get_cluster_custom_objects(self, rs_name: str) -> list:
        logging.debug("Run: get_cluster_custom_objects({})".format(rs_name))
        res = self._custom_api.list_cluster_custom_object(self._resource_group, self._resource_version, rs_name)
        return res.get("items", [])

    def get_namespaced_custom_objects(self, ns_name: str, rs_type: str) -> list:
        logging.debug("Run: get_namespaced_custom_objects({}, {})".format(ns_name, rs_name))
        res = self._custom_api.list_namespaced_custom_object(self._resource_group, self._resource_version, ns_name, rs_type)
        return res.get("items", [])

    def dump_custom_object(self, item: dict) -> None:
        logging.debug("Run: dump_custom_object()")

        path = self._resource_base_dir
        namespace = item["metadata"].get("namespace", "")
        if namespace:
            path = path.joinpath(namespace)

        path = path.joinpath(item["metadata"]["name"])
        path.parent.mkdir(parents=True, exist_ok=True)

        logging.info("Dump: {}".format(path))
        path.write_text(json.dumps(item))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["resource_types", "list_resources", "dump_resources"], help="Select command.")
    parser.add_argument("--type", dest="type", help="Select specific report type.")
    parser.add_argument("--namespaced", dest="namespaced", action="store_true", help="Select namespaced or cluster objects.")
    return parser.parse_args()


def error_if_empty(arg: str) -> str:
    if not arg:
        raise Exception("The required argument is empty!")

    return arg


try:
    log_level = logging.DEBUG if os.environ.get("DEBUG_MODE", "") else logging.INFO
    logging.basicConfig(
        format=r'%(levelname)s [%(asctime)s]: "%(message)s"',
        datefmt=r'%Y-%m-%d %H:%M:%S',
        level=log_level
    )

    args = parse_args()
    client = TrivyReports()

    if args.command == "resource_types":
        logging.info("Namespaced set: {}".format(args.namespaced))
        for item in client.get_api_resources(args.namespaced):
            logging.info("Type: {}".format(item))

    elif args.command == "list_resources":
        rs_type = error_if_empty(args.type)

        if args.namespaced:
            for ns_name in client.get_namespaces():
                for item in client.get_namespaced_custom_objects(ns_name, rs_type):
                    rs_name = item["metadata"]["name"]
                    logging.info("kubectl -n {} get {} {} -o yaml".format(ns_name, rs_type, rs_name))

        else:
            for item in client.get_cluster_custom_objects(rs_type):
                rs_name = item["metadata"]["name"]
                logging.info("kubectl get {} {} -o yaml".format(rs_type, rs_name))

    elif args.command == "dump_resources":
        rs_type = error_if_empty(args.type)

        if args.namespaced:
            for ns_name in client.get_namespaces():
                for item in client.get_namespaced_custom_objects(ns_name, rs_type):
                    client.dump_custom_object(item)

        else:
            for item in client.get_cluster_custom_objects(rs_type):
                client.dump_custom_object(item)

except Exception:
    logging.error(traceback.format_exc())
    sys.exit(1)
