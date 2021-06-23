from click import group, secho
from click.decorators import argument

def sprint(*args, **kwargs):
    if not kwargs.get("fg"):
        kwargs["fg"] = 'green'
    secho(*args, **kwargs)

def get_args(args):
    from click import __version__
    if __version__.startswith('8.'):
        from click.parser import split_arg_string
        import os
        args = split_arg_string(os.environ["COMP_WORDS"])
    return args

@group()
def cli():
    """  base --> module --> scli  """
    pass
