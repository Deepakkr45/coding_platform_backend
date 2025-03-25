import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

def modify_read_paths(code, user_id):
    """Modify file paths for reading CSV and JSON files using multiple libraries."""

    user_upload_folder = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_upload_folder, exist_ok=True)  # Ensure directory exists

    # Extended regex patterns to match multiple libraries
    file_read_patterns = [
        # Pandas
        (r'(pd\.read_csv|pd\.read_json|pd\.read_table|pd\.read_fwf)\(\s*["\'](.*?)["\']', 2),

        # NumPy
        (r'(np\.loadtxt|np\.genfromtxt)\(\s*["\'](.*?)["\']', 2),

        # CSV Module
        (r'(csv\.reader|csv\.DictReader)\(\s*open\(\s*["\'](.*?)["\']', 2),

        # JSON Module
        (r'(json\.load)\(\s*open\(\s*["\'](.*?)["\']', 2),

        # Dask
        (r'(dd\.read_csv|dd\.read_json)\(\s*["\'](.*?)["\']', 2),

        # Polars
        (r'(pl\.read_csv|pl\.read_json)\(\s*["\'](.*?)["\']', 2),

        # PyArrow (CSV & JSON)
        (r'(pa\.csv\.read_csv|pa\.json\.read_json)\(\s*["\'](.*?)["\']', 2),
    ]

        # Pattern to detect URL-based file paths
    url_pattern = r'https?://'

    def replace_path(match):
        """Replace hardcoded file paths inside function calls."""
        func_call, filename = match.groups()

        # Skip modification if the path is a URL
        if re.search(url_pattern, filename):
            return match.group(0)
            
        new_path = os.path.join(user_upload_folder, filename)
        # Handle open() separately if used inside csv or json
        if "open(" in match.group(0):
            return f'{func_call}(open("{new_path}"'
        return f'{func_call}("{new_path}"'

    # Modify direct file paths
    for pattern, group_idx in file_read_patterns:
        code = re.sub(pattern, replace_path, code)

    # Regex for variable assignments with file paths (only for CSV/JSON files)
    variable_assign_pattern = r'(\w+)\s*=\s*["\'](.*?)["\']'

    # Store modified variable paths
    modified_vars = {}

    def replace_variable_assignment(match):
        """Modify variable assignments storing file paths (CSV/JSON only)."""
        var_name, filename = match.groups()
        if filename.endswith((".csv", ".json")):  # Handle CSV/JSON only
            new_path = os.path.join(user_upload_folder, filename)
            modified_vars[var_name] = new_path
            return f'{var_name} = "{new_path}"'
        return match.group(0)  # Leave other file types unchanged

    # Modify variable assignments storing file paths
    code = re.sub(variable_assign_pattern, replace_variable_assignment, code)

    # Regex for variable-based file usage with supported libraries
    variable_usage_pattern = (
        r'(pd\.read_csv|pd\.read_json|pd\.read_table|pd\.read_fwf|'
        r'np\.loadtxt|np\.genfromtxt|csv\.reader|csv\.DictReader|'
        r'json\.load|dd\.read_csv|dd\.read_json|pl\.read_csv|pl\.read_json|'
        r'pa\.csv\.read_csv|pa\.json\.read_json)\(\s*(\w+)\s*\)'
    )

    def replace_variable_usage(match):
        """Modify variable-based file paths used in reading functions."""
        func_call, var_name = match.groups()
        if var_name in modified_vars:
            if "open(" in match.group(0):
                return f'{func_call}(open("{modified_vars[var_name]}")'
            return f'{func_call}("{modified_vars[var_name]}")'
        return match.group(0)  # Return unchanged if variable is not recognized

    # Modify file read functions that use variables
    code = re.sub(variable_usage_pattern, replace_variable_usage, code)

    return code
