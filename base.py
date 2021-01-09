import click


def SF_PRINT(*args, **kwargs):
    if not kwargs.get("fg"):
        kwargs["fg"] = 'green'
    click.secho(*args, **kwargs)


@click.group()
def cli():
    """  base --> module --> scli  """
    pass
