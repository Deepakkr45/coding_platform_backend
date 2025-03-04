import os
import ast
import astunparse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

def modify_read_csv_paths(code,user_id):
    """Modify CSV reading functions to point to the uploaded file directory and add debugging."""
    
    user_upload_folder = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_upload_folder, exist_ok=True)  # Ensure directory exists

    class ReadCSVTransformer(ast.NodeTransformer):
        def visit_Assign(self, node):
            """Modify variable assignments containing CSV file paths."""
            if is_string_assignment(node):
                return update_string_path(node, user_upload_folder)
            if is_os_path_join(node):
                return update_os_path_join(node, user_upload_folder)
            return node

        def visit_Call(self, node):
            """Modify various CSV reading calls."""
            if is_read_csv_call(node) or is_numpy_loadtxt(node) or is_numpy_genfromtxt(node) or is_csv_reader(node):
                return modify_csv_read_call(node, user_upload_folder)
            return node

    tree = ast.parse(code)
    tree = ReadCSVTransformer().visit(tree)
    return astunparse.unparse(tree)

# ---------------------------- #
#       Helper Functions       #
# ---------------------------- #

def is_string_assignment(node):
    """Check if an assignment is a string, e.g., csv_file = 'test.csv'."""
    return isinstance(node.value, ast.Str)

def update_string_path(node, user_upload_folder):
    """Update string assignments to point to the correct upload folder."""
    filename = node.value.s
    modified_path = os.path.join(user_upload_folder, filename)
    print(f"🔄 Updating string path: {filename} → {modified_path}")  # Debugging output
    node.value = ast.Str(s=modified_path)
    return node

def is_os_path_join(node):
    """Check if an assignment uses os.path.join()."""
    return isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "join"

def update_os_path_join(node, user_upload_folder):
    """Modify os.path.join() assignments to use the upload folder."""
    modified_path = os.path.join(user_upload_folder, node.value.args[-1].s)
    print(f"🔄 Updating os.path.join path: {modified_path}")  # Debugging output
    node.value = ast.Str(s=modified_path)
    return node

def is_read_csv_call(node):
    """Check if the function call is pd.read_csv()."""
    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
        if node.func.value.id == 'pd' and node.func.attr == 'read_csv':
            print("✅ Found pd.read_csv() call in AST")  # Debugging output
            return True
    return False

def is_numpy_loadtxt(node):
    """Check if the function call is np.loadtxt()."""
    return isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'np' and node.func.attr == 'loadtxt'

def is_numpy_genfromtxt(node):
    """Check if the function call is np.genfromtxt()."""
    return isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'np' and node.func.attr == 'genfromtxt'

def is_csv_reader(node):
    """Check if the function call is csv.reader()."""
    return isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'csv' and node.func.attr == 'reader'

def modify_csv_read_call(node, user_upload_folder):
    """Modify various CSV reading functions for both direct strings and variables."""
    if node.args:
        # Case 1: Direct String Path
        if isinstance(node.args[0], ast.Str):
            filename = node.args[0].s
            modified_path = os.path.join(user_upload_folder, filename)
            print(f"🔄 Changing CSV path: {filename} → {modified_path}")  # Debugging output
            node.args[0] = ast.Str(s=modified_path)
        
        # Case 2: Variable Path
        elif isinstance(node.args[0], ast.Name):
            var_name = node.args[0].id
            debug_code = (
                f"import os; print('Checking for file:', {var_name}); "
                f"if not os.path.exists({var_name}): print('❌ Error: File not found:', {var_name})"
            )
            debug_node = ast.parse(debug_code).body[0]
            return [debug_node, node]
    
    return node
