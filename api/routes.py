"""Contains all API routes for the external REST API."""

# standard
import os
import json
from flask import (Blueprint, jsonify, request, abort,
                   render_template, current_app as app)
from flask_cors import cross_origin
import requests
import logging

# local
import conf.config as conf
import modules.byzantine as byz

# globals
routes = Blueprint("routes", __name__)
logger = logging.getLogger(__name__)


@routes.route("/", methods=["GET"])
def index():
    """Return the status of the current API service."""
    _id = str(os.getenv("ID", 0))
    return jsonify({
        "status": app.resolver.system_status.name,
        "service": "DistributedSystemBlueprint",
        "id": _id
    })


@routes.route("/set-byz-behavior", methods=["POST"])
def set_byz_behavior():
    """Route for setting Byzantine behavior for this node at runtime."""
    data = request.get_json()
    behavior = data["behavior"]
    if not byz.is_valid_byz_behavior(behavior):
        return abort(400)

    byz.set_byz_behavior(behavior)
    return jsonify({"behavior": byz.get_byz_behavior()})


@routes.route("/byz-behaviors", methods=["GET"])
def get_byz_behaviors():
    """Returns the valid Byzantine behaviors."""
    return jsonify(byz.BYZ_BEHAVIORS)


@routes.route("/data", methods=["GET"])
@cross_origin()
def get_modules_data():
    """Returns current values of variables in the modules."""

    data = {"HELLO_WORLD_MODULE":
            app.resolver.get_hello_world_module_data(),
            "node_id": int(os.getenv("ID")),
            "byzantine": byz.is_byzantine(),
            "byzantine_behavior": byz.get_byz_behavior()
            }
    return json.dumps(data)


def fetch_data_for_all_nodes():
    """Fetches data from all nodes through their /data endpoint."""
    try:
        data = []
        for _, node in conf.get_nodes().items():
            r = requests.get(f"http://{node.ip}:{4000+node.id}/data")
            data.append({"node": node.to_dct(), "data": r.json()})
        return data
    except Exception as e:
        logger.error(f"Error when fetching data for other nodes: {e}")
        return None


def render_global_view(view="view-est"):
    """Renders the global view for a specified module."""
    nodes_data = fetch_data_for_all_nodes()
    if nodes_data is None:
        return jsonify({"STATUS": "SYSTEM_BOOT"})

    test_name = os.getenv("INTEGRATION_TEST")
    test_data = {"test_name": test_name} if test_name is not None else {}

    nss_on = os.getenv("NON_SELF_STAB")
    nss = {"nss": 1} if nss_on is not None else {}

    return render_template("view/main.html", data={
        "view": view,
        "nodes_data": nodes_data,
        "test_data": test_data,
        "nss": nss,
        "byz_behaviors": [byz.NONE] + byz.BYZ_BEHAVIORS
    })


@routes.route("/view/view-est", methods=["GET"])
def render_view_est_view():
    """Renders the global view for the View Establishment module.

    This view only displays data related to the view est module and should
    only be used when running integration test for that module.
    """
    return render_global_view("view-est")


@routes.route("/view/rep", methods=["GET"])
def render_rep_view():
    """Renders the global view for the Replication module.

    This view only displays data related to the rep module and should
    only be used when running integration test for that module.
    """
    return render_global_view("rep")


@routes.route("/view/prim-mon", methods=["GET"])
def render_prim_mon_view():
    """Renders the global view for the Primary Monitoring module.

    This view only displays data related to the prim monitoring module and
    should only be used when running integration test for that module.
    """
    return render_global_view("prim-mon")
