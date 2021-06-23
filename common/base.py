from click import group, secho

def sprint(*args, **kwargs):
    if not kwargs.get("fg"):
        kwargs["fg"] = 'green'
    secho(*args, **kwargs)


@group()
def cli():
    """  base --> module --> scli  """
    pass
