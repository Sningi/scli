from click import group, secho, option, STRING
from utils.http_helper import set_hp
def sprint(*args, **kwargs):
    if not kwargs.get("fg"):
        kwargs["fg"] = 'green'
    secho(*args, **kwargs)

def get_args(args):
    from click import __version__
    if __version__.startswith('8.') or True:
        from click.parser import split_arg_string
        import os
        args = split_arg_string(os.environ["COMP_WORDS"])
    return args

@option('--sw','-s', type=STRING, required=False)
@option('--cpu','-c', type=STRING, required=False)
@group()
def cli(sw, cpu):
    if sw or cpu:
        set_hp(sw=sw,cpu=cpu)
    """  base --> module --> scli  """
    pass
