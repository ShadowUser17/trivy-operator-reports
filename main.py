# https://github.com/kubernetes-client/python
import os
import sys
import logging
import traceback

from kubernetes import config as k8s_config
from kubernetes import client as k8s_client


try:
    log_level = logging.DEBUG if os.environ.get("DEBUG_MODE", "") else logging.INFO
    logging.basicConfig(
        format=r'%(levelname)s [%(asctime)s]: "%(message)s"',
        datefmt=r'%Y-%m-%d %H:%M:%S',
        level=log_level
    )

    k8s_config.load_kube_config()
    core_api_client = k8s_client.CoreV1Api()
    custom_api_client = k8s_client.CustomObjectsApi()

except Exception:
    logging.error(traceback.format_exc())
    sys.exit(1)
