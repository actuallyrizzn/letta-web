from flask import Blueprint, render_template, request, jsonify, current_app
from functools import wraps
import traceback
import logging

error_bp = Blueprint('errors', __name__)

def handle_api_error(f):
    """Decorator to handle API errors consistently"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            current_app.logger.warning(f'Validation error in {f.__name__}: {e}')
            return jsonify({'error': str(e)}), 400
        except PermissionError as e:
            current_app.logger.warning(f'Permission error in {f.__name__}: {e}')
            return jsonify({'error': 'Permission denied'}), 403
        except FileNotFoundError as e:
            current_app.logger.warning(f'Not found error in {f.__name__}: {e}')
            return jsonify({'error': 'Resource not found'}), 404
        except ConnectionError as e:
            current_app.logger.error(f'Connection error in {f.__name__}: {e}')
            return jsonify({'error': 'Service temporarily unavailable'}), 503
        except Exception as e:
            current_app.logger.error(f'Unexpected error in {f.__name__}: {e}')
            current_app.logger.error(traceback.format_exc())
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function

def handle_htmx_error(f):
    """Decorator to handle HTMX errors with proper templates"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            current_app.logger.warning(f'Validation error in {f.__name__}: {e}')
            return render_template('components/error.html', 
                                 error=str(e), 
                                 error_type='validation')
        except PermissionError as e:
            current_app.logger.warning(f'Permission error in {f.__name__}: {e}')
            return render_template('components/error.html', 
                                 error='Permission denied', 
                                 error_type='permission')
        except FileNotFoundError as e:
            current_app.logger.warning(f'Not found error in {f.__name__}: {e}')
            return render_template('components/error.html', 
                                 error='Resource not found', 
                                 error_type='not_found')
        except ConnectionError as e:
            current_app.logger.error(f'Connection error in {f.__name__}: {e}')
            return render_template('components/error.html', 
                                 error='Service temporarily unavailable', 
                                 error_type='connection')
        except Exception as e:
            current_app.logger.error(f'Unexpected error in {f.__name__}: {e}')
            current_app.logger.error(traceback.format_exc())
            return render_template('components/error.html', 
                                 error='Internal server error', 
                                 error_type='internal')
    return decorated_function

@error_bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    if request.headers.get('HX-Request'):
        return render_template('components/error.html', 
                             error='Page not found', 
                             error_type='not_found'), 404
    return render_template('errors/404.html'), 404

@error_bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    current_app.logger.error(f'Server error: {error}')
    if request.headers.get('HX-Request'):
        return render_template('components/error.html', 
                             error='Internal server error', 
                             error_type='internal'), 500
    return render_template('errors/500.html'), 500

@error_bp.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    if request.headers.get('HX-Request'):
        return render_template('components/error.html', 
                             error='Permission denied', 
                             error_type='permission'), 403
    return render_template('errors/403.html'), 403

def log_error(error_message, error_type='error', extra_data=None):
    """Log error with structured data"""
    log_data = {
        'error_message': error_message,
        'error_type': error_type,
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.remote_addr,
        'url': request.url,
        'method': request.method
    }
    
    if extra_data:
        log_data.update(extra_data)
    
    if error_type == 'error':
        current_app.logger.error(log_data)
    elif error_type == 'warning':
        current_app.logger.warning(log_data)
    else:
        current_app.logger.info(log_data)

def validate_request_data(data, required_fields=None, optional_fields=None):
    """Validate request data structure"""
    errors = []
    
    if not isinstance(data, dict):
        errors.append('Request data must be a JSON object')
        return errors
    
    # Check required fields
    if required_fields:
        for field in required_fields:
            if field not in data:
                errors.append(f'Required field missing: {field}')
    
    # Check optional fields (if provided, validate their types)
    if optional_fields:
        for field, field_type in optional_fields.items():
            if field in data:
                if not isinstance(data[field], field_type):
                    errors.append(f'Field {field} must be of type {field_type.__name__}')
    
    return errors
