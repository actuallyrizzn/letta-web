from flask import Blueprint, jsonify, current_app

runtime_bp = Blueprint('runtime', __name__)

@runtime_bp.route('/runtime', methods=['GET'])
def get_runtime_info():
    """Get runtime configuration information"""
    return jsonify({
        'LETTA_BASE_URL': current_app.config['LETTA_BASE_URL']
    })
