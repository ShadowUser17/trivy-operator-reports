import os
import yaml
import json
import logging
import pathlib

from kubernetes import config as k8s_config
from kubernetes import client as k8s_client


def get_logger(name: str | None = None) -> logging.Logger:
    log_level = logging.DEBUG if os.environ.get("DEBUG_MODE", "") else logging.INFO
    logging.basicConfig(
        format=r'%(levelname)s [%(asctime)s]: "%(message)s"',
        datefmt=r'%Y-%m-%d %H:%M:%S', level=log_level
    )
    return logging.getLogger(name)


def error_if_empty(arg: str) -> str:
    if not arg:
        raise Exception("The required argument is empty!")

    return arg


class TrivyReports:
    def __init__(self, logger: logging.Logger = None) -> None:
        k8s_config.load_kube_config()
        self._logger = logger if logger else logging.getLogger(__name__)

        self._core_api = k8s_client.CoreV1Api()
        self._custom_api = k8s_client.CustomObjectsApi()
        self._resource_group = "aquasecurity.github.io"
        self._resource_version = "v1alpha1"
        self._resource_base_dir = pathlib.Path("./reports")

    def get_namespaces(self) -> list:
        self._logger.debug("Run: get_namespaces()")
        res = self._core_api.list_namespace()
        return [item.metadata.name for item in res.items]

    def get_api_resources(self, namespaced: bool = True) -> list:
        self._logger.debug("Run: get_api_resources({})".format(namespaced))
        res = self._custom_api.get_api_resources(self._resource_group, self._resource_version)
        res = filter(lambda item: item.namespaced == namespaced, res.resources)
        return list(map(lambda item: item.name, res))

    def get_cluster_custom_objects(self, rs_name: str) -> list:
        self._logger.debug("Run: get_cluster_custom_objects({})".format(rs_name))
        res = self._custom_api.list_cluster_custom_object(self._resource_group, self._resource_version, rs_name)
        return res.get("items", [])

    def get_namespaced_custom_objects(self, ns_name: str, rs_type: str) -> list:
        self._logger.debug("Run: get_namespaced_custom_objects({}, {})".format(ns_name, rs_type))
        res = self._custom_api.list_namespaced_custom_object(self._resource_group, self._resource_version, ns_name, rs_type)
        return res.get("items", [])

    def dump_custom_object(self, item: dict, format: str) -> None:
        self._logger.debug("Run: dump_custom_object()")

        path = self._resource_base_dir
        namespace = item["metadata"].get("namespace", "")
        if namespace:
            path = path.joinpath(namespace)

        path = path.joinpath(item["metadata"]["name"])
        path.parent.mkdir(parents=True, exist_ok=True)

        self._logger.info("Dump: {}".format(path))
        if format == "yaml":
            path.write_text(yaml.dump(item.get("report", {})))

        else:
            path.write_text(json.dumps(item.get("report", {})))
