import subprocess

import pytest
from pytest import MonkeyPatch

from dbt_mcp.dbt_cli.tools import register_dbt_cli_tools
from tests.mocks.config import mock_dbt_cli_config


@pytest.fixture
def mock_process():
    class MockProcess:
        def communicate(self, timeout=None):
            return "command output", None

    return MockProcess()


@pytest.fixture
def mock_fastmcp():
    class MockFastMCP:
        def __init__(self):
            self.tools = {}

        def tool(self, **kwargs):
            def decorator(func):
                self.tools[func.__name__] = func
                return func

            return decorator

    fastmcp = MockFastMCP()
    return fastmcp, fastmcp.tools


@pytest.mark.parametrize(
    "sql_query,limit_param,expected_args",
    [
        # SQL with explicit LIMIT - should set --limit=-1
        (
            "SELECT * FROM my_model LIMIT 10",
            None,
            [
                "show",
                "--favor-state",
                "--inline",
                "SELECT * FROM my_model LIMIT 10",
                "--limit",
                "-1",
                "--output",
                "json",
            ],
        ),
        # SQL with lowercase limit - should set --limit=-1
        (
            "select * from my_model limit 5",
            None,
            [
                "show",
                "--favor-state",
                "--inline",
                "select * from my_model limit 5",
                "--limit",
                "-1",
                "--output",
                "json",
            ],
        ),
        # No SQL LIMIT but with limit parameter - should use provided limit
        (
            "SELECT * FROM my_model",
            10,
            [
                "show",
                "--favor-state",
                "--inline",
                "SELECT * FROM my_model",
                "--limit",
                "10",
                "--output",
                "json",
            ],
        ),
        # No limits at all - should not include --limit flag
        (
            "SELECT * FROM my_model",
            None,
            [
                "show",
                "--favor-state",
                "--inline",
                "SELECT * FROM my_model",
                "--output",
                "json",
            ],
        ),
    ],
)
def test_show_command_limit_logic(
    monkeypatch: MonkeyPatch,
    mock_process,
    mock_fastmcp,
    sql_query,
    limit_param,
    expected_args,
):
    # Mock Popen
    mock_calls = []

    def mock_popen(args, **kwargs):
        mock_calls.append(args)
        return mock_process

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    # Register tools and get show tool
    fastmcp, tools = mock_fastmcp
    register_dbt_cli_tools(fastmcp, mock_dbt_cli_config)
    show_tool = tools["show"]

    # Call show tool with test parameters
    result = show_tool(sql_query=sql_query, limit=limit_param)

    # Verify the command was called with expected arguments
    assert mock_calls
    args_list = mock_calls[0][1:]  # Skip the dbt path
    assert args_list == expected_args


def test_run_command_adds_quiet_flag_to_verbose_commands(
    monkeypatch: MonkeyPatch, mock_process, mock_fastmcp
):
    # Mock Popen
    mock_calls = []

    def mock_popen(args, **kwargs):
        mock_calls.append(args)
        return mock_process

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    # Setup
    mock_fastmcp_obj, tools = mock_fastmcp
    register_dbt_cli_tools(mock_fastmcp_obj, mock_dbt_cli_config)
    run_tool = tools["run"]

    # Execute
    run_tool()

    # Verify
    assert mock_calls
    args_list = mock_calls[0]
    assert "--quiet" in args_list


def test_run_command_correctly_formatted(
    monkeypatch: MonkeyPatch, mock_process, mock_fastmcp
):
    # Mock Popen
    mock_calls = []

    def mock_popen(args, **kwargs):
        mock_calls.append(args)
        return mock_process

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    fastmcp, tools = mock_fastmcp

    # Register the tools
    register_dbt_cli_tools(fastmcp, mock_dbt_cli_config)
    run_tool = tools["run"]

    # Run the command with a selector
    run_tool(selector="my_model")

    # Verify the command is correctly formatted
    assert mock_calls
    args_list = mock_calls[0]
    assert args_list == [
        "/path/to/dbt",
        "run",
        "--quiet",
        "--select",
        "my_model",
    ]


def test_show_command_correctly_formatted(
    monkeypatch: MonkeyPatch, mock_process, mock_fastmcp
):
    # Mock Popen
    mock_calls = []

    def mock_popen(args, **kwargs):
        mock_calls.append(args)
        return mock_process

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    # Setup
    mock_fastmcp_obj, tools = mock_fastmcp
    register_dbt_cli_tools(mock_fastmcp_obj, mock_dbt_cli_config)
    show_tool = tools["show"]

    # Execute
    show_tool(sql_query="SELECT * FROM my_model")

    # Verify
    assert mock_calls
    args_list = mock_calls[0]
    assert args_list[0].endswith("dbt")
    assert args_list[1] == "show"
    assert args_list[2] == "--favor-state"
    assert args_list[3] == "--inline"
    assert args_list[4] == "SELECT * FROM my_model"


def test_list_command_timeout_handling(monkeypatch: MonkeyPatch, mock_fastmcp):
    # Mock Popen
    class MockProcessWithTimeout:
        def communicate(self, timeout=None):
            raise subprocess.TimeoutExpired(cmd=["dbt", "list"], timeout=10)

    def mock_popen(*args, **kwargs):
        return MockProcessWithTimeout()

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    # Setup
    mock_fastmcp_obj, tools = mock_fastmcp
    register_dbt_cli_tools(mock_fastmcp_obj, mock_dbt_cli_config)
    list_tool = tools["ls"]

    # Test timeout case
    result = list_tool(resource_type=["model", "snapshot"])
    assert "Timeout: dbt command took too long to complete" in result
    assert "Try using a specific selector to narrow down the results" in result

    # Test with selector - should still timeout
    result = list_tool(selector="my_model", resource_type=["model"])
    assert "Timeout: dbt command took too long to complete" in result
    assert "Try using a specific selector to narrow down the results" in result


def test_show_command_with_selector(
    monkeypatch: MonkeyPatch, mock_process, mock_fastmcp
):
    # Mock Popen
    mock_calls = []

    def mock_popen(args, **kwargs):
        mock_calls.append(args)
        return mock_process

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    # Setup
    mock_fastmcp_obj, tools = mock_fastmcp
    register_dbt_cli_tools(mock_fastmcp_obj, mock_dbt_cli_config)
    show_tool = tools["show"]

    # Execute with selector
    show_tool(selector="my_model")

    # Verify
    assert mock_calls
    args_list = mock_calls[0]
    expected_args = [
        "/path/to/dbt",
        "show",
        "--favor-state",
        "--select",
        "my_model",
        "--output",
        "json",
    ]
    assert args_list == expected_args


def test_show_command_validation_errors(mock_fastmcp):
    # Setup
    mock_fastmcp_obj, tools = mock_fastmcp
    register_dbt_cli_tools(mock_fastmcp_obj, mock_dbt_cli_config)
    show_tool = tools["show"]

    # Test both sql_query and selector provided
    result = show_tool(sql_query="SELECT * FROM model", selector="my_model")
    assert "You must provide *either* `sql_query` *or* `selector` (but not both)" in result

    # Test neither sql_query nor selector provided
    result = show_tool()
    assert "You must provide *either* `sql_query` *or* `selector` (but not both)" in result


def test_compile_command_with_selector(
    monkeypatch: MonkeyPatch, mock_process, mock_fastmcp
):
    # Mock Popen
    mock_calls = []

    def mock_popen(args, **kwargs):
        mock_calls.append(args)
        return mock_process

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    # Setup
    mock_fastmcp_obj, tools = mock_fastmcp
    register_dbt_cli_tools(mock_fastmcp_obj, mock_dbt_cli_config)
    compile_tool = tools["compile"]

    # Execute with selector
    compile_tool(selector="my_model")

    # Verify
    assert mock_calls
    args_list = mock_calls[0]
    expected_args = [
        "/path/to/dbt",
        "compile",
        "--quiet",
        "--select",
        "my_model",
    ]
    assert args_list == expected_args


def test_compile_command_with_sql_query(
    monkeypatch: MonkeyPatch, mock_process, mock_fastmcp
):
    # Mock Popen
    mock_calls = []

    def mock_popen(args, **kwargs):
        mock_calls.append(args)
        return mock_process

    monkeypatch.setattr("subprocess.Popen", mock_popen)

    # Setup
    mock_fastmcp_obj, tools = mock_fastmcp
    register_dbt_cli_tools(mock_fastmcp_obj, mock_dbt_cli_config)
    compile_tool = tools["compile"]

    # Execute with sql_query
    compile_tool(sql_query="SELECT * FROM my_model")

    # Verify
    assert mock_calls
    args_list = mock_calls[0]
    expected_args = [
        "/path/to/dbt",
        "compile",
        "--quiet",
        "--inline",
        "SELECT * FROM my_model",
    ]
    assert args_list == expected_args


def test_compile_command_validation_errors(mock_fastmcp):
    # Setup
    mock_fastmcp_obj, tools = mock_fastmcp
    register_dbt_cli_tools(mock_fastmcp_obj, mock_dbt_cli_config)
    compile_tool = tools["compile"]

    # Test both sql_query and selector provided
    result = compile_tool(sql_query="SELECT * FROM model", selector="my_model")
    assert "You cannot provide *both* `sql_query` *and* `selector`" in result
