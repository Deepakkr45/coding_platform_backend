# import io
# import contextlib
# import base64
# import traceback
# import matplotlib.pyplot as plt
# import pandas as pd
# from utils.code_utils import validate_code
# from utils.update_path_utils import modify_read_paths
# from utils.file_utils import fetch_user_id

# def execute_user_code(code,token):
#     """Executes user-submitted Python code securely and returns output and plots."""
#     user_id = fetch_user_id(token)
#     print(user_id)
#     if not user_id:
#         return {'output': '', 'plot': None, 'error': 'Session ended, Please login again'}, 400
    
#     is_valid, message = validate_code(code)
#     if not is_valid:
#         return {'output': '', 'plot': None, 'error': message}, 400
    
#     modified_code = modify_read_paths(code,user_id)
#     print("DEBUG: Modified Code to be Executed:\n", modified_code)
#     output = io.StringIO()
#     plot_data = None
#     error = None
#     plot_data = None
    
#     try:
#         with contextlib.redirect_stdout(output):
#             exec(modified_code, {'pd': pd, 'plt': plt})

#             if plt.get_fignums():
#                 buf = io.BytesIO()
#                 plt.savefig(buf, format='png')
#                 buf.seek(0)
#                 plot_data = base64.b64encode(buf.read()).decode('utf-8')
#                 plt.close()
#     except Exception as e:
#         return {'error': str(e)}, 500

#     return {'output': output.getvalue(), 'plot': plot_data, 'error': error}, 200


import io
import contextlib
import base64
import traceback
import re
import matplotlib.pyplot as plt
import pandas as pd
from utils.code_utils import validate_code
from utils.update_path_utils import modify_read_paths
from utils.file_utils import fetch_user_id

def execute_user_code(code, token):
    """Executes user-submitted Python code securely and returns output and plots, showing only relevant error lines."""
    
    user_id = fetch_user_id(token)
    if not user_id:
        return {'output': '', 'plot': None, 'error': 'Session ended. Please log in again.'}, 400

    is_valid, message = validate_code(code)
    if not is_valid:
        return {'output': '', 'plot': None, 'error': message}, 400

    modified_code = modify_read_paths(code, user_id)
    output = io.StringIO()
    plot_data = None

    # Convert code to a list of lines to track line numbers
    # code_lines = modified_code.strip().split("\n")
    
    try:
        with contextlib.redirect_stdout(output):
            exec(modified_code, {'pd': pd, 'plt': plt})

            # Handle Matplotlib plots
            if plt.get_fignums():
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plot_data = base64.b64encode(buf.read()).decode('utf-8')
                plt.close()

    except Exception as e:
        error_type = e.__class__.__name__  # Get error type (e.g., FileNotFoundError, IndexError)
        error_msg = str(e)  # Get the error message
        tb = traceback.extract_tb(e.__traceback__)  # Extract traceback

        # Extract correct line number **inside user code**
        user_code_line_number = None
        for frame in tb:
            if "<string>" in frame.filename:  # Errors inside exec() show as "<string>"
                user_code_line_number = frame.lineno  # Get the user code line number

        # Remove file paths from error messages
        sanitized_error_msg = re.sub(r"(/\S+)+", "[hidden path]", error_msg)

        # Special handling for FileNotFoundError
        if error_type == "FileNotFoundError":
            sanitized_error_msg = "File not found."

        # Show line number only if it's inside user code
        if user_code_line_number:
            error_message = f"Error on line {user_code_line_number}: {error_type} - {sanitized_error_msg}"
        else:
            error_message = f"{error_type} - {sanitized_error_msg}"

        return {'output': '', 'plot': None, 'error': error_message}, 400

    return {'output': output.getvalue(), 'plot': plot_data, 'error': None}, 200
