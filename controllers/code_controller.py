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
        return {'output': '', 'plots': [], 'error': 'Session ended. Please log in again.'}, 400

    is_valid, message = validate_code(code)
    if not is_valid:
        return {'output': '', 'plots': [], 'error': message}, 400

    modified_code = modify_read_paths(code, user_id)
    output = io.StringIO()
    plot_data_list = []

    try:
        with contextlib.redirect_stdout(output):
            exec(modified_code, {'pd': pd, 'plt': plt, '__name__': '__main__'})

            # Handle multiple Matplotlib plots
            for fig_num in plt.get_fignums():
                buf = io.BytesIO()
                plt.figure(fig_num)
                plt.savefig(buf, format='png')
                buf.seek(0)
                plot_data_list.append(base64.b64encode(buf.read()).decode('utf-8'))
                plt.close(fig_num)

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        user_code_line_number = None

        for frame in tb:
            if "<string>" in frame.filename:
                user_code_line_number = frame.lineno
                break  

        error_type = e.__class__.__name__
        error_msg = str(e)
        sanitized_error_msg = re.sub(r"(/\S+)+", "[hidden path]", error_msg)

        if error_type == "FileNotFoundError":
            sanitized_error_msg = "File not found."
        elif error_type == "ModuleNotFoundError":
            sanitized_error_msg = "Module not found. Check your import statements."

        if user_code_line_number:
            error_message = f"Error on line {user_code_line_number}: {error_type} - {sanitized_error_msg}"
        else:
            error_message = f"{error_type} - {sanitized_error_msg}"

        return {'output': '', 'plots': [], 'error': error_message}, 400

    return {'output': output.getvalue(), 'plots': plot_data_list, 'error': None}, 200
