"""
Multiple except handlers.
"""

try:
    import doesnt_exist
except ImportError as ie:
    print(str(ie))
except Exception as ee:
    print(str(ee))
