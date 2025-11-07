"""This module provides tools for file system operations and web scraping.

It includes file system tools for reading, writing, listing files and directories,
as well as basic search functionality.

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Callable, List
from langchain.tools import ToolRuntime

from src.agents.code_agent.context import Context
# from context import Context


def read_file(file_path: str, runtime: ToolRuntime[Context]) -> str:
    """Read the contents of a file.
    
    Args:
        file_path: The path to the file to read
        context: The agent context
        
    Returns:
        The contents of the file as a string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str, runtime: ToolRuntime[Context]) -> str:
    """Write content to a file.
    
    Args:
        file_path: The path to the file to write
        content: The content to write to the file
        runtime: The tool runtime with agent context
        
    Returns:
        Success message or error message
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def list_directory(dir_path: str, runtime: ToolRuntime[Context]) -> str:
    """List the contents of a directory.
    
    Args:
        dir_path: The path to the directory to list
        runtime: The tool runtime with agent context
        
    Returns:
        A formatted string with the directory contents
    """
    try:
        if not os.path.exists(dir_path):
            return f"Directory '{dir_path}' does not exist"
            
        if not os.path.isdir(dir_path):
            return f"'{dir_path}' is not a directory"
            
        items = os.listdir(dir_path)
        if not items:
            return f"Directory '{dir_path}' is empty"
            
        # Separate files and directories
        files = []
        dirs = []
        
        for item in items:
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                dirs.append(f"[DIR] {item}")
            else:
                size = os.path.getsize(item_path)
                files.append(f"[FILE] {item} ({size} bytes)")
        
        result = f"Contents of '{dir_path}':\n\n"
        if dirs:
            result += "Directories:\n" + "\n".join(dirs) + "\n\n"
        if files:
            result += "Files:\n" + "\n".join(files)
            
        return result
    except Exception as e:
        return f"Error listing directory: {str(e)}"


def create_directory(dir_path: str, runtime: ToolRuntime[Context]) -> str:
    """Create a new directory.
    
    Args:
        dir_path: The path to the directory to create
        runtime: The tool runtime with agent context
        
    Returns:
        Success message or error message
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return f"Successfully created directory '{dir_path}'"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


def delete_file_or_path(path: str, runtime: ToolRuntime[Context]) -> str:
    """Delete a file or directory.
    
    Args:
        path: The path to the file or directory to delete
        runtime: The tool runtime with agent context
        
    Returns:
        Success message or error message
    """
    try:
        if not os.path.exists(path):
            return f"Path '{path}' does not exist"
            
        if os.path.isdir(path):
            shutil.rmtree(path)
            return f"Successfully deleted directory '{path}'"
        else:
            os.remove(path)
            return f"Successfully deleted file '{path}'"
    except Exception as e:
        return f"Error deleting path: {str(e)}"


def copy_file_or_path(src: str, dst: str, runtime: ToolRuntime[Context]) -> str:
    """Copy a file or directory from source to destination.
    
    Args:
        src: The source path
        dst: The destination path
        runtime: The tool runtime with agent context
        
    Returns:
        Success message or error message
    """
    try:
        if not os.path.exists(src):
            return f"Source path '{src}' does not exist"
            
        if os.path.isdir(src):
            shutil.copytree(src, dst)
            return f"Successfully copied directory from '{src}' to '{dst}'"
        else:
            shutil.copy2(src, dst)
            return f"Successfully copied file from '{src}' to '{dst}'"
    except Exception as e:
        return f"Error copying: {str(e)}"


def move_file_or_path(src: str, dst: str, runtime: ToolRuntime[Context]) -> str:
    """Move a file or directory from source to destination.
    
    Args:
        src: The source path
        dst: The destination path
        runtime: The tool runtime with agent context
        
    Returns:
        Success message or error message
    """
    try:
        if not os.path.exists(src):
            return f"Source path '{src}' does not exist"
            
        shutil.move(src, dst)
        return f"Successfully moved from '{src}' to '{dst}'"
    except Exception as e:
        return f"Error moving: {str(e)}"


def get_file_info(file_path: str, runtime: ToolRuntime[Context]) -> str:
    """Get detailed information about a file or directory.
    
    Args:
        file_path: The path to the file or directory
        runtime: The tool runtime with agent context
        
    Returns:
        Formatted string with file information
    """
    try:
        if not os.path.exists(file_path):
            return f"Path '{file_path}' does not exist"
            
        stat = os.stat(file_path)
        path_obj = Path(file_path)
        
        info = f"Information for '{file_path}':\n\n"
        info += f"Type: {'Directory' if os.path.isdir(file_path) else 'File'}\n"
        info += f"Size: {stat.st_size} bytes\n"
        info += f"Created: {stat.st_ctime}\n"
        info += f"Modified: {stat.st_mtime}\n"
        info += f"Accessed: {stat.st_atime}\n"
        
        if os.path.isfile(file_path):
            info += f"Extension: {path_obj.suffix}\n"
            info += f"Parent directory: {path_obj.parent}\n"
            
        return info
    except Exception as e:
        return f"Error getting file info: {str(e)}"


def search_files(dir_path: str, pattern: str, runtime: ToolRuntime[Context]) -> str:
    """Search for files matching a pattern in a directory.
    
    Args:
        dir_path: The directory to search in
        pattern: The pattern to search for (supports wildcards)
        runtime: The tool runtime with agent context
        
    Returns:
        List of matching files
    """
    try:
        if not os.path.exists(dir_path):
            return f"Directory '{dir_path}' does not exist"
            
        if not os.path.isdir(dir_path):
            return f"'{dir_path}' is not a directory"
            
        path_obj = Path(dir_path)
        matches = list(path_obj.rglob(pattern))
        
        if not matches:
            return f"No files found matching pattern '{pattern}' in '{dir_path}'"
            
        result = f"Files matching pattern '{pattern}' in '{dir_path}':\n\n"
        for match in matches:
            if match.is_file():
                size = match.stat().st_size
                result += f"[FILE] {match} ({size} bytes)\n"
            else:
                result += f"[DIR] {match}\n"
                
        return result
    except Exception as e:
        return f"Error searching files: {str(e)}"


def get_current_working_directory(runtime: ToolRuntime[Context]) -> str:
    """Get the current working directory.
    
    Args:
        runtime: The tool runtime with agent context
        
    Returns:
        The current working directory path
    """
    try:
        return os.getcwd()
    except Exception as e:
        return f"Error getting current directory: {str(e)}"


def change_working_directory(dir_path: str, runtime: ToolRuntime[Context]) -> str:
    """Change the current working directory.
    
    Args:
        dir_path: The directory to change to
        runtime: The tool runtime with agent context
        
    Returns:
        Success message or error message
    """
    try:
        os.chdir(dir_path)
        return f"Successfully changed directory to '{dir_path}'. Current directory: {os.getcwd()}"
    except Exception as e:
        return f"Error changing directory: {str(e)}"


# Register all tools
FILE_TOOLS: List[Callable[..., Any]] = [
    read_file,
    write_file,
    list_directory,
    create_directory,
    delete_file_or_path,
    copy_file_or_path,
    move_file_or_path,
    get_file_info,
    search_files,
    get_current_working_directory,
    change_working_directory,
]

if __name__ == "__main__":
    import tempfile
    import time
    from unittest.mock import Mock
    
    # Create a mock ToolRuntime for testing
    mock_runtime = Mock(spec=ToolRuntime)
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="file_system_tools_test_")
    print(f"Created test directory: {test_dir}")
    
    try:
        print("\n=== Testing File System Tools ===\n")
        
        # Test 1: get_current_working_directory
        print("1. Testing get_current_working_directory:")
        result = get_current_working_directory(mock_runtime)
        print(f"   Current directory: {result}")
        print()
        
        # Test 2: create_directory
        print("2. Testing create_directory:")
        test_subdir = os.path.join(test_dir, "test_subdir")
        result = create_directory(test_subdir, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 3: write_file
        print("3. Testing write_file:")
        test_file = os.path.join(test_subdir, "test_file.txt")
        test_content = "Hello, World!\nThis is a test file."
        result = write_file(test_file, test_content, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 4: read_file
        print("4. Testing read_file:")
        result = read_file(test_file, mock_runtime)
        print(f"   File content:\n   {result}")
        print()
        
        # Test 5: get_file_info
        print("5. Testing get_file_info:")
        result = get_file_info(test_file, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 6: list_directory
        print("6. Testing list_directory:")
        result = list_directory(test_subdir, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 7: create more files for testing
        print("7. Creating more test files:")
        test_file2 = os.path.join(test_subdir, "test_file2.py")
        write_file(test_file2, "# Python test file\nprint('Hello')", mock_runtime)
        test_file3 = os.path.join(test_subdir, "README.md")
        write_file(test_file3, "# Test README\nThis is a markdown file.", mock_runtime)
        print("   Created test_file2.py and README.md")
        print()
        
        # Test 8: search_files
        print("8. Testing search_files:")
        result = search_files(test_dir, "*.py", mock_runtime)
        print(f"   Searching for *.py files:\n   {result}")
        print()
        
        result = search_files(test_dir, "*.txt", mock_runtime)
        print(f"   Searching for *.txt files:\n   {result}")
        print()
        
        # Test 9: copy_file_or_path
        print("9. Testing copy_file_or_path:")
        copy_dest = os.path.join(test_dir, "copied_file.txt")
        result = copy_file_or_path(test_file, copy_dest, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 10: move_file_or_path
        print("10. Testing move_file_or_path:")
        move_dest = os.path.join(test_dir, "moved_file.txt")
        result = move_file_or_path(copy_dest, move_dest, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 11: change_working_directory
        print("11. Testing change_working_directory:")
        original_dir = get_current_working_directory(mock_runtime)
        result = change_working_directory(test_subdir, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 12: list_directory in changed directory
        print("12. Testing list_directory in changed directory:")
        result = list_directory(".", mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 13: change back to original directory
        print("13. Changing back to original directory:")
        result = change_working_directory(original_dir, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 14: delete_file_or_path
        print("14. Testing delete_file_or_path:")
        result = delete_file_or_path(move_dest, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 15: delete directory
        print("15. Testing delete_file_or_path on directory:")
        result = delete_file_or_path(test_subdir, mock_runtime)
        print(f"   {result}")
        print()
        
        # Test 16: Error handling tests
        print("16. Testing error handling:")
        result = read_file("nonexistent_file.txt", mock_runtime)
        print(f"   Reading nonexistent file: {result}")
        
        result = list_directory("nonexistent_dir", mock_runtime)
        print(f"   Listing nonexistent directory: {result}")
        
        result = delete_file_or_path("nonexistent_path", mock_runtime)
        print(f"   Deleting nonexistent path: {result}")
        print()
        
        print("=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up test directory
        try:
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")
        except Exception as e:
            print(f"Error cleaning up test directory: {e}")