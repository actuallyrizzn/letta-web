"""
Letta Chatbot - Performance and Caching Utilities
Copyright (C) 2025 Mark Hopkins

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from flask import current_app
from functools import wraps
import time
import hashlib
import json

# Simple in-memory cache (in production, use Redis or Memcached)
_cache = {}
_cache_ttl = {}

def cache_result(ttl=300, key_prefix=''):
    """Decorator to cache function results"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{f.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Check if cached result exists and is not expired
            if cache_key in _cache:
                if time.time() - _cache_ttl.get(cache_key, 0) < ttl:
                    current_app.logger.debug(f"Cache hit for {cache_key}")
                    return _cache[cache_key]
                else:
                    # Remove expired cache entry
                    del _cache[cache_key]
                    del _cache_ttl[cache_key]
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            _cache[cache_key] = result
            _cache_ttl[cache_key] = time.time()
            
            current_app.logger.debug(f"Cached result for {cache_key}")
            return result
        
        return decorated_function
    return decorator

def invalidate_cache(pattern=None):
    """Invalidate cache entries matching pattern"""
    if pattern is None:
        _cache.clear()
        _cache_ttl.clear()
        return
    
    keys_to_remove = [key for key in _cache.keys() if pattern in key]
    for key in keys_to_remove:
        del _cache[key]
        del _cache_ttl[key]
    
    current_app.logger.debug(f"Invalidated {len(keys_to_remove)} cache entries matching '{pattern}'")

def clear_all_cache():
    """Clear all cache entries"""
    _cache.clear()
    _cache_ttl.clear()

def reset_rate_limiters():
    """Reset all rate limiters"""
    global api_rate_limiter, message_rate_limiter
    api_rate_limiter.requests.clear()
    message_rate_limiter.requests.clear()

def get_cache_stats():
    """Get cache statistics"""
    total_entries = len(_cache)
    expired_entries = 0
    
    current_time = time.time()
    for key, timestamp in _cache_ttl.items():
        if current_time - timestamp > 300:  # 5 minutes default TTL
            expired_entries += 1
    
    return {
        'total_entries': total_entries,
        'expired_entries': expired_entries,
        'active_entries': total_entries - expired_entries,
        'cache_size_mb': sum(len(str(v).encode()) for v in _cache.values()) / 1024 / 1024
    }

class RateLimiter:
    """Simple rate limiter using sliding window"""
    
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier):
        """Check if request is allowed for given identifier"""
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(current_time)
            return True
        
        return False
    
    def get_remaining_requests(self, identifier):
        """Get remaining requests for identifier"""
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if req_time > window_start
            ]
            return max(0, self.max_requests - len(self.requests[identifier]))
        
        return self.max_requests

# Global rate limiter instances
api_rate_limiter = RateLimiter(max_requests=200, window_seconds=60)  # 200 requests per minute
message_rate_limiter = RateLimiter(max_requests=30, window_seconds=60)  # 30 messages per minute

def rate_limit(limiter, get_identifier=None):
    """Decorator to rate limit requests"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            # Get identifier (default: IP address)
            if get_identifier:
                identifier = get_identifier()
            else:
                identifier = request.remote_addr
            
            if not limiter.is_allowed(identifier):
                remaining = limiter.get_remaining_requests(identifier)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': 60,
                    'remaining_requests': remaining
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def paginate_results(results, page=1, per_page=20):
    """Paginate results"""
    if not isinstance(results, list):
        return results
    
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_results = results[start:end]
    
    return {
        'results': paginated_results,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_next': end < total,
            'has_prev': page > 1
        }
    }
