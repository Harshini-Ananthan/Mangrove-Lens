import os
import joblib
import pickle
import numpy as np
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base directory setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
MODEL_FILENAME = 'ndvi_random_forest_model.pkl'
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_FILENAME)

# Global variables to hold model and metadata
_model = None
_preprocessor = None
_feature_names = ['CO', 'month', 'year', 'dayofyear']
_expected_features_count = 4

def load_model():
    """
    Loads the machine learning model and any available preprocessors once during startup.
    """
    global _model, _preprocessor

    if not os.path.exists(MODEL_PATH):
        logger.error(f"Missing model file: The model could not be found at {MODEL_PATH}. "
                     "Please ensure the .pkl file is placed in the models/ directory.")
        return False

    try:
        # 2. Detect whether it should be loaded using joblib or pickle
        try:
            _model = joblib.load(MODEL_PATH)
            loader_used = "joblib"
        except Exception:
            with open(MODEL_PATH, 'rb') as f:
                _model = pickle.load(f)
            loader_used = "pickle"

        # 4. Inspect the model
        model_type = type(_model).__name__
        
        global _expected_features_count, _feature_names
        if hasattr(_model, 'n_features_in_'):
            _expected_features_count = _model.n_features_in_
        if hasattr(_model, 'feature_names_in_'):
            _feature_names = list(_model.feature_names_in_)
            
        classes = getattr(_model, 'classes_', 'N/A (Regressor)')

        # 7. Detect and load preprocessing objects if they exist
        scaler_path = os.path.join(MODELS_DIR, 'scaler.pkl')
        if os.path.exists(scaler_path):
            try:
                _preprocessor = joblib.load(scaler_path)
                logger.info("Successfully loaded preprocessing object (scaler.pkl).")
            except Exception:
                with open(scaler_path, 'rb') as f:
                    _preprocessor = pickle.load(f)
                logger.info("Successfully loaded preprocessing object (scaler.pkl) with pickle.")

        # 10. Print startup message
        logger.info(f"✅ Model loaded successfully using {loader_used}.")
        logger.info(f"--- Model Inspection ---")
        logger.info(f"Type: {model_type}")
        logger.info(f"Input Features Count: {_expected_features_count}")
        logger.info(f"Feature Names: {_feature_names}")
        logger.info(f"Classes/Labels: {classes}")
        logger.info(f"------------------------")
        
        # 6. Disable retraining
        logger.info("Retraining module has been permanently disabled. All predictions will use this existing model.")
        
        return True

    except Exception as e:
        logger.error(f"Corrupted model or failed to load: {str(e)}.\n"
                     "Fix: Ensure the file is a valid scikit-learn model saved with joblib or pickle and dependencies match.")
        return False

# 3. Load the model once during application startup
load_model()

def predict_ndvi(input_data):
    """
    5. Prediction pipeline using the loaded existing model.
    Validates incoming prediction data and returns predictions.
    
    :param input_data: dict, list of lists, or pandas DataFrame
    :return: list of predictions or error dictionary
    """
    global _model, _preprocessor, _feature_names, _expected_features_count
    
    if _model is None:
        return {"error": "Model is not loaded. Please check server logs."}
        
    # Convert input to DataFrame for easy validation
    try:
        if isinstance(input_data, dict):
            # Single prediction
            df = pd.DataFrame([input_data])
        elif isinstance(input_data, list):
            # Assuming list of dicts or list of lists
            if len(input_data) > 0 and isinstance(input_data[0], dict):
                df = pd.DataFrame(input_data)
            else:
                df = pd.DataFrame(input_data, columns=_feature_names)
        elif isinstance(input_data, pd.DataFrame):
            df = input_data.copy()
        else:
            return {"error": "Unsupported input data type. Expected dict, list, or DataFrame."}
    except Exception as e:
        return {"error": f"Failed to parse input data: {str(e)}"}

    # 8. Validate incoming prediction data
    if len(df.columns) != _expected_features_count:
        return {"error": f"Incorrect input dimensions. Expected {_expected_features_count} features, but got {len(df.columns)}."}
        
    # Reorder columns to match model's expected order if names match
    missing_features = [f for f in _feature_names if f not in df.columns]
    if missing_features:
        return {"error": f"Missing expected features: {missing_features}"}
        
    # Ensure correct feature order
    df = df[_feature_names]
    
    # 9. Error handling during prediction
    try:
        # Preprocessing if detected
        X = df.values
        if _preprocessor is not None:
            X = _preprocessor.transform(X)
            
        predictions = _model.predict(X)
        return {"predictions": predictions.tolist()}
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return {"error": f"Prediction failed due to model error: {str(e)}"}

# Example dummy function that previously retrained the model
def train_model():
    """
    This function used to retrain the model.
    It has been disabled as per requirements.
    """
    logger.warning("train_model() was called but retraining is disabled. Using existing model instead.")
    pass
