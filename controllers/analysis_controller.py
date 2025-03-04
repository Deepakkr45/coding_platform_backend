import numpy as np
import pandas as pd
from flask import jsonify
from utils.data_cleaning import clean_data

def perform_analysis(data, analysis_type):
    try:
        if analysis_type == 'average':
            return {"average": data['value'].mean()}
        elif analysis_type == 'median':
            return {"median": data['value'].median()}
        elif analysis_type == 'mode':
            try:
                mode_value = data['value'].mode().iloc[0]
                return {"mode": mode_value}
            except IndexError:
                raise ValueError("Mode cannot be computed due to insufficient data.")
        elif analysis_type == 'std_dev':
            return {"std_dev": data['value'].std()}
        elif analysis_type == 'variance':
            return {"variance": data['value'].var()}
        elif analysis_type == 'quartiles':
            quartiles = np.percentile(data['value'], [25, 50, 75])
            return {
                "Q1": quartiles[0],
                "Q2 (Median)": quartiles[1],
                "Q3": quartiles[2]
            }
        elif analysis_type == 'max':
            return {"max": data['value'].max()}
        elif analysis_type == 'min':
            return {"min": data['value'].min()}
        elif analysis_type == 'overview':
            return {
                "average": data['value'].mean(),
                "median": data['value'].median(),
                "mode": data['value'].mode().tolist() if not data['value'].mode().empty else None,
                "max": data['value'].max(),
                "min": data['value'].min()
            }
        else:
            raise ValueError("Invalid analysis type: {}".format(analysis_type))
    except Exception as e:
        raise ValueError("Error performing analysis: {}".format(str(e)))
