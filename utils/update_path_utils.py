import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

def modify_read_paths(code, user_id):
    """Modify file paths for reading CSV and JSON files (handles both single and double quotes)."""

    user_upload_folder = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_upload_folder, exist_ok=True)  # Ensure directory exists

    # Regex patterns to match file reading functions with direct paths
    file_read_patterns = [
        (r'(pd\.read_csv|pd\.read_json|np\.loadtxt|np\.genfromtxt|open)\(\s*["\'](.*?)["\']', 2),
    ]

    def replace_path(match):
        """Replace hardcoded file paths inside function calls."""
        func_call, filename = match.groups()
        new_path = os.path.join(user_upload_folder, filename)
        return f'{func_call}("{new_path}"'  # Always use double quotes for safety

    # Modify direct file paths
    for pattern, group_idx in file_read_patterns:
        code = re.sub(pattern, replace_path, code)

    # Regex to find variable assignments with file names (handles both single and double quotes)
    variable_assign_pattern = r'(\w+)\s*=\s*["\'](.*?)["\']'

    # Store modified variable paths
    modified_vars = {}

    def replace_variable_assignment(match):
        """Modify variable assignments storing file paths (handles both quote types)."""
        var_name, filename = match.groups()
        new_path = os.path.join(user_upload_folder, filename)
        modified_vars[var_name] = new_path
        return f'{var_name} = "{new_path}"'  # Always use double quotes for consistency

    # Modify variable assignments storing file paths
    code = re.sub(variable_assign_pattern, replace_variable_assignment, code)

    # Regex to find variables used in read functions
    variable_usage_pattern = r'(pd\.read_csv|pd\.read_json|np\.loadtxt|np\.genfromtxt|open)\(\s*(\w+)\s*\)'

    def replace_variable_usage(match):
        """Modify variable-based file paths used in reading functions."""
        func_call, var_name = match.groups()
        if var_name in modified_vars:
            return f'{func_call}("{modified_vars[var_name]}")'  # Convert variable use into a direct path
        return match.group(0)  # Return unchanged if variable is unknown

    # Modify read functions that use variables
    code = re.sub(variable_usage_pattern, replace_variable_usage, code)

    return code
