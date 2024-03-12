import os
import sys
import common
import logging
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["resource_types", "list_resources", "dump_resources"], help="Select command.")
    parser.add_argument("--type", dest="type", help="Select specific report type.")
    parser.add_argument("--format", dest="format", default="yaml", choices=["json", "yaml"], help="Select output format.")
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
    client = common.TrivyReports()

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
                    client.dump_custom_object(item, args.format)

        else:
            for item in client.get_cluster_custom_objects(rs_type):
                client.dump_custom_object(item, args.format)

except Exception:
    logging.exception(__name__)
    sys.exit(1)
