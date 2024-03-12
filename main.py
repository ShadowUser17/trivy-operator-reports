import sys
import common
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["resource_types", "list_resources", "dump_resources"], help="Select command.")
    parser.add_argument("--type", dest="type", help="Select specific report type.")
    parser.add_argument("--format", dest="format", default="yaml", choices=["json", "yaml"], help="Select output format.")
    parser.add_argument("--namespaced", dest="namespaced", action="store_true", help="Select namespaced or cluster objects.")
    return parser.parse_args()


logger = common.get_logger()
try:
    args = parse_args()
    client = common.TrivyReports(logger)

    if args.command == "resource_types":
        logger.info("Namespaced set: {}".format(args.namespaced))
        for item in client.get_api_resources(args.namespaced):
            logger.info("Type: {}".format(item))

    elif args.command == "list_resources":
        rs_type = common.error_if_empty(args.type)

        if args.namespaced:
            for ns_name in client.get_namespaces():
                for item in client.get_namespaced_custom_objects(ns_name, rs_type):
                    rs_name = item["metadata"]["name"]
                    logger.info("kubectl -n {} get {} {} -o yaml".format(ns_name, rs_type, rs_name))

        else:
            for item in client.get_cluster_custom_objects(rs_type):
                rs_name = item["metadata"]["name"]
                logger.info("kubectl get {} {} -o yaml".format(rs_type, rs_name))

    elif args.command == "dump_resources":
        rs_type = common.error_if_empty(args.type)

        if args.namespaced:
            for ns_name in client.get_namespaces():
                for item in client.get_namespaced_custom_objects(ns_name, rs_type):
                    client.dump_custom_object(item, args.format)

        else:
            for item in client.get_cluster_custom_objects(rs_type):
                client.dump_custom_object(item, args.format)

except Exception:
    logger.exception(__name__)
    sys.exit(1)
