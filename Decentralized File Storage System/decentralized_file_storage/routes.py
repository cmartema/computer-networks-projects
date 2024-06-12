import logging
import os

from flask import jsonify, render_template, request, redirect, url_for

# Setup logger for this module
logger = logging.getLogger(__name__)

# Flag for additional logging
DEBUG_FLAG = 0

def create_peer():
    from .filesystem import BlockFileSystemPeer

    port = int(os.getenv("PEER_PORT", 50110))
    print(f"Starting peer with {port=}")
    tracker_host = os.getenv("TRACKER_HOST", "localhost")
    tracker_port = int(os.getenv("TRACKER_PORT", 60000))
    peer = BlockFileSystemPeer(port=port, tracker_host=tracker_host, tracker_port=tracker_port)
    logger.info(f"Creating peer at {port} connecting to tracker at {tracker_host}:{tracker_port}")
    return peer


def configure_routes(app):
    peer = create_peer()
    peer.start()

    @app.route("/")
    def index():
        files = peer.list_files()
        return render_template("index.html", files=files)

    @app.route("/files/create", methods=["POST"])
    def create_file():
        filename = request.form["filename"]
        try:
            response = peer.create_file(filename)
            if DEBUG_FLAG:
                logger.debug(f"Response from create_file: {response}")
            # Redirect to the homepage or another suitable page
            return redirect(url_for('index'))
        except KeyError as e:
            logger.error(f"Failed to create file '{filename}': {e}")
            return jsonify({"status": "error", "message": str(e)}), 409  # HTTP 409 Conflict
        except Exception as e:
            logger.error(f"Error during file creation '{filename}': {e}")
            return jsonify({"status": "error", "message": str(e)}), 400

    @app.route("/files/append", methods=["POST"])
    def append_to_file():
        filename = request.form["filename"]
        content = request.form["content"]
        try:
            response = peer.append_file(filename, content)
            if DEBUG_FLAG:
                logger.debug(f"Response from append_file: {response}")
            # Redirect to prevent form resubmission
            return redirect(url_for('index'))
        except KeyError:
            return jsonify({"status": "error", "message": "File not found"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @app.route("/files/delete/<filename>", methods=["POST"])
    def delete_file(filename):
        try:
            response = peer.delete_file(filename)
            if DEBUG_FLAG:
                logger.debug(f"Response from delete_file: {response}")
            # Redirect to prevent form resubmission
            return redirect(url_for('index'))
        except KeyError:
            return jsonify({"status": "error", "message": "File not found"}), 404
        except Exception as e:
            logger.error(f"Error during file deletion '{filename}': {e}")
            return jsonify({"status": "error", "message": str(e)}), 400

    @app.route("/files/read/<filename>", methods=["GET"])
    def read_file(filename):
        try:
            content = peer.read_file(filename)
            return jsonify({"filename": filename, "content": content}), 200
        except KeyError:
            return jsonify({"error": "File not found"}), 404

    @app.route("/simulate-tampering", methods=["POST"])
    def simulate_tampering():
        logger.info(f"Request headers: {request.headers}")
        logger.info(f"Request data: {request.data.decode('utf-8')}")  # Decode binary data to string
        data = request.get_json(silent=True)
        if not data:
            logger.error("No data received or data is not JSON.")
            return jsonify({"status": "error", "message": "No data or incorrect format."}), 400

        filename = data.get('filename')
        newContent = data.get('newContent')
        if not filename or not newContent:
            logger.error("Filename or new content missing in the received data.")
            return jsonify({"status": "error", "message": "Missing filename or content."}), 400

        try:
            message = peer.simulate_tampering(filename, newContent)
            return jsonify({"status": "success", "message": message}), 200
        except Exception as e:
            logger.error(f"Error during tampering simulation for '{filename}': {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500



    @app.route("/debug-request", methods=["POST"])
    def debug_request():
        print(f"Request headers: {request.headers}")
        print(f"Request data: {request.data}")
        print(f"Request form: {request.form}")
        print(f"Request files: {request.files}")
        print(f"Request json: {request.json}")
        return jsonify({"status": "success", "message": "Request received"})
