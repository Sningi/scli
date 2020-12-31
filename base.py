import click
from json import dumps


clean_data = dumps([{"op": "replace", "path": "/", "value": 0}])

@click.group()
def cli():
    """  base --> module --> scli  """
    pass
