import os
import subprocess
from collections.abc import Iterable

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from dbt_mcp.config.config import DbtCliConfig
from dbt_mcp.prompts.prompts import get_prompt


def register_dbt_cli_tools(dbt_mcp: FastMCP, config: DbtCliConfig) -> None:
    def _run_dbt_command(
        command: list[str],
        selector: str | None = None,
        timeout: int | None = None,
        resource_type: list[str] | None = None,
        is_selectable: bool = False,
    ) -> str:
        try:
            # Commands that should always be quiet to reduce output verbosity
            verbose_commands = [
                "build",
                "compile",
                "docs",
                "parse",
                "run",
                "test",
                "list",
            ]

            if selector:
                selector_params = str(selector).split(" ")
                command = command + ["--select"] + selector_params

            if isinstance(resource_type, Iterable):
                command = command + ["--resource-type"] + resource_type

            full_command = command.copy()
            # Add --quiet flag to specific commands to reduce context window usage
            if len(full_command) > 0 and full_command[0] in verbose_commands:
                main_command = full_command[0]
                command_args = full_command[1:] if len(full_command) > 1 else []
                full_command = [main_command, "--quiet", *command_args]

            # We change the path only if this is an absolute path, otherwise we can have
            # problems with relative paths applied multiple times as DBT_PROJECT_DIR
            # is applied to dbt Core and Fusion as well (but not the dbt Cloud CLI)
            cwd_path = config.project_dir if os.path.isabs(config.project_dir) else None

            process = subprocess.Popen(
                args=[config.dbt_path, *full_command],
                cwd=cwd_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output, _ = process.communicate(timeout=timeout)
            return output or "OK"
        except subprocess.TimeoutExpired:
            return "Timeout: dbt command took too long to complete." + (
                " Try using a specific selector to narrow down the results."
                if is_selectable
                else ""
            )
        except Exception as e:
            return str(e)

    @dbt_mcp.tool(description=get_prompt("dbt_cli/build"))
    def build(
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
    ) -> str:
        return _run_dbt_command(["build"], selector, is_selectable=True)

    @dbt_mcp.tool(description=get_prompt("dbt_cli/compile"))
    def compile( 
        sql_query: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/sql_query")
        ),
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
    ) -> str:
        """
        Render executable SQL.

        **One** of ``sql_query`` or ``selector`` may be passed. If both are
        provided, an error string is returned.

        An empty ``selector`` compiles the entire project.

        Parameters
        ----------
        sql_query:
            Raw SQL to compile via ``--inline``.
        selector:
            dbt node selector to compile via ``--select``.
        """
        # Handle Pydantic Field objects that might be passed instead of None
        if hasattr(sql_query, 'default'):
            sql_query = None
        if hasattr(selector, 'default'):
            selector = None
            
        if sql_query is not None and selector is not None:
            return (
                "You cannot provide *both* `sql_query` *and* `selector` "
                "when calling the `compile` tool"
            )

        args: list[str] = ["compile"]
        if sql_query is not None:
            args.extend(["--inline", sql_query])
            return _run_dbt_command(args)
        elif selector is not None:
            return _run_dbt_command(args, selector, is_selectable=True)
        else:
            # Neither provided - compile entire project
            return _run_dbt_command(args)

    @dbt_mcp.tool(description=get_prompt("dbt_cli/docs"))
    def docs() -> str:
        return _run_dbt_command(["docs", "generate"])

    @dbt_mcp.tool(name="list", description=get_prompt("dbt_cli/list"))
    def ls(
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
        resource_type: list[str] | None = Field(
            default=None,
            description=get_prompt("dbt_cli/args/resource_type"),
        ),
    ) -> str:
        return _run_dbt_command(
            ["list"],
            selector,
            timeout=config.dbt_cli_timeout,
            resource_type=resource_type,
            is_selectable=True,
        )

    @dbt_mcp.tool(description=get_prompt("dbt_cli/parse"))
    def parse() -> str:
        return _run_dbt_command(["parse"])

    @dbt_mcp.tool(description=get_prompt("dbt_cli/run"))
    def run(
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
    ) -> str:
        return _run_dbt_command(["run"], selector, is_selectable=True)

    @dbt_mcp.tool(description=get_prompt("dbt_cli/test"))
    def test(
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
    ) -> str:
        return _run_dbt_command(["test"], selector, is_selectable=True)

    @dbt_mcp.tool(description=get_prompt("dbt_cli/show"))
    def show(
        sql_query: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/sql_query")
        ),
        selector: str | None = Field(
            default=None, description=get_prompt("dbt_cli/args/selectors")
        ),
        limit: int | None = Field(
            default=None, description=get_prompt("dbt_cli/args/limit")
        ),
    ) -> str:
        """
        Execute `dbt show` with either an inline SQL query **or** a selector.

        Exactly one of `sql_query` or `selector` must be supplied. If both are
        provided (or neither), an error message is returned so the caller can
        correct the invocation.

        Arguments
        ---------
        sql_query : str | None
            Raw SQL to preview via `--inline`.
        selector : str | None
            dbt node selection syntax to preview via `--select`.
        limit : int | None
            Optional row limit to apply. If the SQL string already contains an
            explicit `LIMIT` clause we pass `--limit=-1` so dbt does not add a
            second limit.
        """
        # Handle Pydantic Field objects that might be passed instead of None
        if hasattr(sql_query, 'default'):
            sql_query = None
        if hasattr(selector, 'default'):
            selector = None
        if hasattr(limit, 'default'):
            limit = None
        
        # Validate mutually–exclusive arguments
        if (sql_query is None and selector is None) or (
            sql_query is not None and selector is not None
        ):
            return (
                "You must provide *either* `sql_query` *or* `selector` (but not both) "
                "when calling the `show` tool."
            )

        # Base command
        args = ["show", "--favor-state"]

        # Inline SQL vs selector
        if sql_query is not None:
            args.extend(["--inline", sql_query])
        else:  # selector is not None
            args.extend(["--select", *str(selector).split(" ")])

        # Handle limit logic
        cli_limit: int | None = None
        if sql_query and "limit" in sql_query.lower():
            # If the user wrote their own LIMIT we tell dbt not to add another.
            cli_limit = -1
        elif limit is not None:
            cli_limit = limit

        if cli_limit is not None:
            args.extend(["--limit", str(cli_limit)])

        # Always request JSON so callers can parse structured results
        args.extend(["--output", "json"])

        return _run_dbt_command(args)
