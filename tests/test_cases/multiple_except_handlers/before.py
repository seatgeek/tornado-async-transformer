"""
Multiple except handlers.
"""

try:
    import doesnt_exist
except ImportError as ie:
    print(ie.message)
except Exception as ee:
    print(ee.message)
