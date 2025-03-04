import io
import contextlib
import base64
import matplotlib.pyplot as plt
import pandas as pd
from utils.code_utils import validate_code, modify_read_csv_paths


def execute_user_code(code,user_id):
    """Executes user-submitted Python code securely and returns output and plots."""

    if not user_id:
        return {'output': '', 'plot': None, 'error': 'User ID is required'}, 400
    
    is_valid, message = validate_code(code)
    if not is_valid:
        return {'output': '', 'plot': None, 'error': message}, 400

    modified_code = modify_read_csv_paths(code,user_id)
    output = io.StringIO()
    plot_data = None
    error = None
    plot_data = None
    
    try:
        with contextlib.redirect_stdout(output):
            exec(modified_code, {'pd': pd, 'plt': plt})

            if plt.get_fignums():
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plot_data = base64.b64encode(buf.read()).decode('utf-8')
                plt.close()
    except Exception as e:
        return {'error': str(e)}, 500

    return {'output': output.getvalue(), 'plot': plot_data, 'error': None}, 200
