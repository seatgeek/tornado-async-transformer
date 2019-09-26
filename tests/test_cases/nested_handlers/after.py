"""
Nested handlers.
"""

try:
    import doesnt_exist
except ImportError:
    try:
        import also_doesnt_exist
    except ImportError as e:
        print(str(e))
