from json import dumps

'''
    Used to document some protocol REST APIs that are common to all modules

'''

general_clean_data = dumps([{"op": "replace", "path": "/", "value": 0}])
