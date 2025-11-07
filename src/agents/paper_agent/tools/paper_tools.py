
"""This module provides specialized tools for reading markdown files and papers.

It includes tools for reading entire markdown files, reading specific line ranges,
and reading content in pages or sections. These tools are designed to be flexible
for AI agents to process markdown documents efficiently.
"""

import os
import re
from typing import Any, Callable, List, Optional, Tuple
from langchain.tools import ToolRuntime

from src.agents.paper_agent.context import Context


def read_markdown_file(file_path: str, runtime: ToolRuntime[Context]) -> str:
    """Read the entire contents of a markdown file.
    
    Args:
        file_path: The path to the markdown file to read
        runtime: The tool runtime with agent context
        
    Returns:
        The contents of the markdown file as a string
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist"
            
        if not file_path.lower().endswith('.md'):
            return f"Warning: File '{file_path}' is not a markdown file (.md)"
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Add file metadata
        file_info = f"=== File: {file_path} ===\n"
        file_info += f"Total lines: {len(content.splitlines())}\n"
        file_info += f"File size: {len(content)} characters\n\n"
        
        return file_info + content
    except Exception as e:
        return f"Error reading markdown file: {str(e)}"


def read_markdown_lines(file_path: str, start_line: int, runtime: ToolRuntime[Context], end_line: Optional[int] = None) -> str:
    """Read specific lines from a markdown file.
    
    Args:
        file_path: The path to the markdown file to read
        start_line: The starting line number (1-based)
        end_line: The ending line number (1-based, inclusive). If None, reads to end of file
        
    Returns:
        The specified lines from the markdown file
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist"
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        
        # Adjust for 1-based indexing
        start_idx = max(0, start_line - 1)
        
        if end_line is None:
            end_idx = total_lines
        else:
            end_idx = min(total_lines, end_line)
            
        if start_idx >= total_lines:
            return f"Error: Start line {start_line} is beyond file length ({total_lines} lines)"
            
        selected_lines = lines[start_idx:end_idx]
        line_numbers = range(start_line, min(start_line + len(selected_lines), total_lines + 1))
        
        result = f"=== Lines {line_numbers[0]}-{line_numbers[-1]} from {file_path} ===\n"
        result += f"Total file lines: {total_lines}\n\n"
        
        for i, line in enumerate(selected_lines):
            result += f"{line_numbers[i]:4d} | {line}"
            
        return result
    except Exception as e:
        return f"Error reading markdown lines: {str(e)}"


def read_markdown_pages(file_path: str, runtime: ToolRuntime[Context], page_num: Optional[int] = None, lines_per_page: int = 50) -> str:
    """Read markdown file content in pages.
    
    Args:
        file_path: The path to the markdown file to read
        page_num: The page number to read (1-based). If None, returns all pages with metadata
        lines_per_page: Number of lines per page (default: 50)
        
    Returns:
        The specified page or information about all pages
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist"
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        total_pages = (total_lines + lines_per_page - 1) // lines_per_page
        
        if page_num is None:
            # Return metadata about all pages
            result = f"=== File: {file_path} ===\n"
            result += f"Total lines: {total_lines}\n"
            result += f"Lines per page: {lines_per_page}\n"
            result += f"Total pages: {total_pages}\n\n"
            
            for i in range(1, total_pages + 1):
                start_line = (i - 1) * lines_per_page + 1
                end_line = min(i * lines_per_page, total_lines)
                result += f"Page {i}: Lines {start_line}-{end_line}\n"
                
            return result
        else:
            # Return specific page
            if page_num < 1 or page_num > total_pages:
                return f"Error: Page {page_num} is out of range. File has {total_pages} pages."
                
            start_idx = (page_num - 1) * lines_per_page
            end_idx = min(page_num * lines_per_page, total_lines)
            start_line = start_idx + 1
            end_line = end_idx
            
            page_lines = lines[start_idx:end_idx]
            
            result = f"=== Page {page_num}/{total_pages} from {file_path} ===\n"
            result += f"Lines {start_line}-{end_line} of {total_lines}\n\n"
            
            for i, line in enumerate(page_lines):
                result += f"{start_line + i:4d} | {line}"
                
            return result
    except Exception as e:
        return f"Error reading markdown pages: {str(e)}"


def read_markdown_sections(file_path: str, runtime: ToolRuntime[Context], section_name: Optional[str] = None) -> str:
    """Read markdown file by sections (based on headers).
    
    Args:
        file_path: The path to the markdown file to read
        section_name: The name of the section to read. If None, returns all section headers
        
    Returns:
        The specified section content or list of all sections
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist"
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.splitlines()
        sections = []
        current_section = None
        current_content = []
        
        # Find all sections
        for line in lines:
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_section is not None:
                    sections.append((current_section, '\n'.join(current_content)))
                
                # Start new section
                level = len(header_match.group(1))
                name = header_match.group(2).strip()
                current_section = {'name': name, 'level': level, 'line': lines.index(line) + 1}
                current_content = [line]
            else:
                if current_section is not None:
                    current_content.append(line)
                else:
                    # Content before first header
                    current_content = [line] if not current_content else current_content + [line]
        
        # Save last section
        if current_section is not None:
            sections.append((current_section, '\n'.join(current_content)))
        
        if section_name is None:
            # Return list of all sections
            result = f"=== Sections in {file_path} ===\n\n"
            
            # Add content before first header if exists
            if sections and not sections[0][0]['name']:
                result += f"[Preamble] (Lines 1-{sections[0][0]['line']-1})\n"
                
            for section_info, content in sections:
                if section_info['name']:
                    indent = "  " * (section_info['level'] - 1)
                    result += f"{indent}- {section_info['name']} (Line {section_info['line']})\n"
                    
            return result
        else:
            # Find and return specific section
            for section_info, content in sections:
                if section_info['name'] and section_name.lower() in section_info['name'].lower():
                    result = f"=== Section: {section_info['name']} ===\n"
                    result += f"Line: {section_info['line']}, Level: {section_info['level']}\n\n"
                    result += content
                    return result
                    
            return f"Error: Section '{section_name}' not found in file"
    except Exception as e:
        return f"Error reading markdown sections: {str(e)}"


def search_markdown_content(file_path: str, search_term: str, runtime: ToolRuntime[Context], context_lines: int = 3) -> str:
    """Search for specific content in a markdown file with context.
    
    Args:
        file_path: The path to the markdown file to search
        search_term: The term to search for
        context_lines: Number of lines to show before and after each match
        
    Returns:
        Search results with context
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist"
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        matches = []
        search_term_lower = search_term.lower()
        
        for i, line in enumerate(lines):
            if search_term_lower in line.lower():
                start_line = max(0, i - context_lines)
                end_line = min(len(lines), i + context_lines + 1)
                
                context_lines_list = lines[start_line:end_line]
                match_line_in_context = i - start_line
                
                context_text = ""
                for j, ctx_line in enumerate(context_lines_list):
                    line_num = start_line + j + 1
                    marker = ">>> " if j == match_line_in_context else "    "
                    context_text += f"{marker}{line_num:4d} | {ctx_line}"
                
                matches.append((i + 1, context_text))
        
        if not matches:
            return f"No matches found for '{search_term}' in {file_path}"
            
        result = f"=== Search Results for '{search_term}' in {file_path} ===\n"
        result += f"Found {len(matches)} match{'es' if len(matches) != 1 else ''}\n\n"
        
        for i, (line_num, context) in enumerate(matches, 1):
            result += f"Match {i} (Line {line_num}):\n"
            result += context + "\n"
            
        return result
    except Exception as e:
        return f"Error searching markdown content: {str(e)}"


# Register all tools
PAPER_TOOLS: List[Callable[..., Any]] = [
    # read_markdown_file,
    read_markdown_lines,
    read_markdown_pages,
    read_markdown_sections,
    search_markdown_content,
]


if __name__ == "__main__":
    import tempfile
    from unittest.mock import Mock
    
    # Create a mock ToolRuntime for testing
    mock_runtime = Mock(spec=ToolRuntime)
    
    # Create a test markdown file
    test_content = """# Test Document

This is a test markdown file for testing the paper tools.

## Introduction

This is the introduction section with some important content.

## Methods

Here we describe the methods used in our research.

### Data Collection

We collected data from various sources.

### Analysis

The analysis was performed using statistical methods.

## Results

Our results show significant findings.

## Conclusion

This concludes our test document.
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        print("=== Testing Paper Tools ===\n")
        
        # Test 1: read_markdown_file
        print("1. Testing read_markdown_file:")
        result = read_markdown_file(test_file, mock_runtime)
        print(result[:300] + "..." if len(result) > 300 else result)
        print()
        
        # Test 2: read_markdown_lines
        print("2. Testing read_markdown_lines:")
        result = read_markdown_lines(test_file, 5, mock_runtime, 10)
        print(result)
        print()
        
        # Test 3: read_markdown_pages
        print("3. Testing read_markdown_pages (metadata):")
        result = read_markdown_pages(test_file, mock_runtime, None, 10)
        print(result)
        print()
        
        print("4. Testing read_markdown_pages (page 2):")
        result = read_markdown_pages(test_file, mock_runtime, 2, 10)
        print(result)
        print()
        
        # Test 4: read_markdown_sections
        print("5. Testing read_markdown_sections (list):")
        result = read_markdown_sections(test_file, mock_runtime, None)
        print(result)
        print()
        
        print("6. Testing read_markdown_sections (specific):")
        result = read_markdown_sections(test_file, mock_runtime, "Methods")
        print(result)
        print()
        
        # Test 5: search_markdown_content
        print("7. Testing search_markdown_content:")
        result = search_markdown_content(test_file, "data", mock_runtime)
        print(result)
        print()
        
        print("=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up test file
        try:
            os.unlink(test_file)
            print(f"\nCleaned up test file: {test_file}")
        except Exception as e:
            print(f"Error cleaning up test file: {e}")