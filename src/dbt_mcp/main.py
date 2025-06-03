import asyncio

import click

import client
from dbt_mcp.mcp.server import create_dbt_mcp


@click.command()
@click.option(
    "--use-client",
    is_flag=True,
    default=False,
    help="Run dbt-mcp in a client locally for debugging purposes.",
)
def main(use_client: bool) -> None:
    if use_client:
        asyncio.run(client.run())
    else:
        asyncio.run(create_dbt_mcp()).run()


main()
