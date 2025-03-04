import re
import os
import ast
import astor 
import astunparse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

RESTRICTED_KEYWORDS = ['os', 'subprocess', 'shutil', 'sys', 'eval', 'exec', 'open', '__import__']

def validate_code(code):
    """Check for restricted keywords or modules."""
    for keyword in RESTRICTED_KEYWORDS:
        if re.search(fr'\b{keyword}\b', code):
            return False, f"Use of '{keyword}' is not allowed."
    return True, ""

# def modify_read_csv_paths(code,user_id):
#     """Modify read_csv paths to point to the uploaded file directory."""
#     user_upload_folder = os.path.join(UPLOAD_FOLDER, user_id)
#     os.makedirs(user_upload_folder, exist_ok=True) 
#     class ReadCSVTransformer(ast.NodeTransformer):
#             def visit_Call(self, node):
#                 if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
#                     if node.func.value.id == 'pd' and node.func.attr == 'read_csv':
#                         if node.args and isinstance(node.args[0], ast.Str):
#                             filename = node.args[0].s
#                             modified_path = os.path.join(user_upload_folder, filename)
#                             node.args[0] = ast.Str(s=modified_path)
#                 return self.generic_visit(node)
        
#     tree = ast.parse(code)
#     tree = ReadCSVTransformer().visit(tree)
#     return astor.to_source(tree)

