"""This module provides tools for executing bash commands and shell operations.

It includes tools for running commands, capturing output, and managing shell processes.

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

import os
import subprocess
import shlex
from typing import Any, Callable, List
from langchain.tools import ToolRuntime

from src.agents.code_agent.context import Context


def execute_command(command: str, runtime: ToolRuntime[Context]) -> str:
    """Execute a bash command and return the output.
    
    Args:
        command: The bash command to execute
        runtime: The tool runtime with agent context
        
    Returns:
        The output of the command, including stdout and stderr
    """
    try:
        # Use shell=True to allow shell features like pipes and redirection
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # Add timeout to prevent hanging
        )
        
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
            
        if not output:
            output = "Command executed successfully with no output"
            
        # Add exit code information
        output += f"\n\nExit code: {result.returncode}"
        
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out after 30 seconds: {command}"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def execute_command_with_cwd(command: str, working_dir: str, runtime: ToolRuntime[Context]) -> str:
    """Execute a bash command in a specific working directory.
    
    Args:
        command: The bash command to execute
        working_dir: The directory in which to execute the command
        runtime: The tool runtime with agent context
        
    Returns:
        The output of the command, including stdout and stderr
    """
    try:
        if not os.path.exists(working_dir):
            return f"Working directory '{working_dir}' does not exist"
            
        if not os.path.isdir(working_dir):
            return f"'{working_dir}' is not a directory"
        
        # Use shell=True to allow shell features like pipes and redirection
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=30  # Add timeout to prevent hanging
        )
        
        output = f"Command executed in directory: {working_dir}\n\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
            
        if not result.stdout and not result.stderr:
            output += "Command executed successfully with no output"
            
        # Add exit code information
        output += f"\n\nExit code: {result.returncode}"
        
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out after 30 seconds: {command}"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def execute_interactive_command(command: str, runtime: ToolRuntime[Context]) -> str:
    """Execute an interactive command (like vim, nano, etc.).
    
    Note: This function is limited in what it can do with truly interactive commands.
    It's best used for commands that might prompt for simple input.
    
    Args:
        command: The bash command to execute
        runtime: The tool runtime with agent context
        
    Returns:
        The output of the command
    """
    try:
        # For interactive commands, we need to use a different approach
        # This is a simplified implementation that may not work for all interactive commands
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send an empty input to handle simple prompts
        stdout, stderr = process.communicate(input="", timeout=10)
        
        output = ""
        if stdout:
            output += f"STDOUT:\n{stdout}"
        if stderr:
            output += f"\nSTDERR:\n{stderr}"
            
        if not output:
            output = "Command executed with no output"
            
        # Add exit code information
        output += f"\n\nExit code: {process.returncode}"
        
        return output
    except subprocess.TimeoutExpired:
        process.kill()
        return f"Interactive command timed out after 10 seconds: {command}"
    except Exception as e:
        return f"Error executing interactive command: {str(e)}"


def check_command_exists(command: str, runtime: ToolRuntime[Context]) -> str:
    """Check if a command exists on the system.
    
    Args:
        command: The command to check (without arguments)
        runtime: The tool runtime with agent context
        
    Returns:
        Whether the command exists or not
    """
    try:
        # Extract just the command name (first word)
        command_name = shlex.split(command)[0] if command.strip() else ""
        
        if not command_name:
            return "No command provided"
        
        # Use 'which' command to check if command exists
        result = subprocess.run(
            f"which {command_name}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return f"Command '{command_name}' exists at: {result.stdout.strip()}"
        else:
            return f"Command '{command_name}' not found in PATH"
    except Exception as e:
        return f"Error checking command: {str(e)}"


def get_environment_variable(var_name: str, runtime: ToolRuntime[Context]) -> str:
    """Get the value of an environment variable.
    
    Args:
        var_name: The name of the environment variable
        runtime: The tool runtime with agent context
        
    Returns:
        The value of the environment variable or an error message
    """
    try:
        value = os.environ.get(var_name)
        if value is not None:
            return f"{var_name}={value}"
        else:
            return f"Environment variable '{var_name}' is not set"
    except Exception as e:
        return f"Error getting environment variable: {str(e)}"


def set_environment_variable(var_name: str, value: str, runtime: ToolRuntime[Context]) -> str:
    """Set an environment variable for the current process.
    
    Note: This only sets the variable for the current process and its children.
    It does not permanently modify the system environment.
    
    Args:
        var_name: The name of the environment variable
        value: The value to set
        runtime: The tool runtime with agent context
        
    Returns:
        Success message or error message
    """
    try:
        os.environ[var_name] = value
        return f"Successfully set {var_name}={value}"
    except Exception as e:
        return f"Error setting environment variable: {str(e)}"


def list_environment_variables(runtime: ToolRuntime[Context]) -> str:
    """List all environment variables.
    
    Args:
        runtime: The tool runtime with agent context
        
    Returns:
        A formatted string with all environment variables
    """
    try:
        env_vars = os.environ
        result = "Environment Variables:\n\n"
        
        # Sort variables for consistent output
        for var_name in sorted(env_vars.keys()):
            result += f"{var_name}={env_vars[var_name]}\n"
            
        return result
    except Exception as e:
        return f"Error listing environment variables: {str(e)}"


def get_current_user(runtime: ToolRuntime[Context]) -> str:
    """Get information about the current user.
    
    Args:
        runtime: The tool runtime with agent context
        
    Returns:
        User information
    """
    try:
        # Get username
        username = os.environ.get("USER") or os.environ.get("USERNAME")
        
        # Get home directory
        home_dir = os.environ.get("HOME") or os.environ.get("USERPROFILE")
        
        # Get current working directory
        cwd = os.getcwd()
        
        result = f"Current User Information:\n\n"
        result += f"Username: {username}\n"
        result += f"Home Directory: {home_dir}\n"
        result += f"Current Working Directory: {cwd}\n"
        
        return result
    except Exception as e:
        return f"Error getting user information: {str(e)}"


# Register all tools
BASH_TOOLS: List[Callable[..., Any]] = [
    execute_command,
    execute_command_with_cwd,
    execute_interactive_command,
    check_command_exists,
    get_environment_variable,
    set_environment_variable,
    list_environment_variables,
    get_current_user,
]


if __name__ == "__main__":
    import tempfile
    import time
    from unittest.mock import Mock
    
    # Create a mock ToolRuntime for testing
    mock_runtime = Mock(spec=ToolRuntime)
    
    try:
        print("\n=== Testing Bash Tools ===\n")
        
        # Test 1: get_current_user
        print("1. Testing get_current_user:")
        result = get_current_user(mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 2: check_command_exists
        print("2. Testing check_command_exists:")
        result = check_command_exists("ls", mock_runtime)
        print(f"   {result}")
        
        result = check_command_exists("nonexistent_command_12345", mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 3: execute_command
        print("3. Testing execute_command:")
        result = execute_command("echo 'Hello from bash!'", mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 4: execute_command_with_cwd
        print("4. Testing execute_command_with_cwd:")
        result = execute_command_with_cwd("pwd", "/tmp", mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 5: get_environment_variable
        print("5. Testing get_environment_variable:")
        result = get_environment_variable("PATH", mock_runtime)
        print(f"   PATH length: {len(result)} characters")
        
        result = get_environment_variable("NONEXISTENT_VAR", mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 6: set_environment_variable
        print("6. Testing set_environment_variable:")
        result = set_environment_variable("TEST_VAR", "test_value", mock_runtime)
        print(f"   {result}")
        
        result = get_environment_variable("TEST_VAR", mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 7: list_environment_variables
        print("7. Testing list_environment_variables:")
        result = list_environment_variables(mock_runtime)
        print(f"   Number of environment variables: {result.count(chr(10))}")
        print()
        
        # Test 8: execute_command with error
        print("8. Testing execute_command with error:")
        result = execute_command("ls /nonexistent_directory", mock_runtime)
        print(f"   {result}")
        print()
        
        print("=== All bash tools tests completed successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()