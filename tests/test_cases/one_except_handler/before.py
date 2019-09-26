"""
One exception handler with deprecated syntax to update.
"""
try:
    import doesnt_exist
except ImportError as e:
    print(e.message)
