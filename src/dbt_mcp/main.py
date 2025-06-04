import argparse
import asyncio
from dataclasses import dataclass

from client import run
from dbt_mcp.mcp.server import create_dbt_mcp


@dataclass
class CliArgs:
    use_client: bool


def parse_args() -> CliArgs:
    parser = argparse.ArgumentParser(description="dbt-mcp CLI tool")
    parser.add_argument(
        "--use-client",
        action="store_true",
        default=False,
        help="Run dbt-mcp in a client locally for debugging purposes.",
    )
    args = parser.parse_args()
    return CliArgs(use_client=args.use_client)


def main() -> None:
    args = parse_args()
    if args.use_client:
        asyncio.run(run())
    else:
        asyncio.run(create_dbt_mcp()).run()


main()
