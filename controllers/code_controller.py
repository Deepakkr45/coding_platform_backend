import io
import contextlib
import base64
import matplotlib.pyplot as plt
import pandas as pd
from utils.code_utils import validate_code
from utils.update_path_utils import modify_read_csv_paths
from utils.file_utils import fetch_user_id

def execute_user_code(code,token):
    """Executes user-submitted Python code securely and returns output and plots."""
    user_id = fetch_user_id(token)
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

    return {'output': output.getvalue(), 'plot': plot_data, 'error': error}, 200


