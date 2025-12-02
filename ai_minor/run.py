# run.py
from app import app

if __name__ == '__main__':
    # Use threaded=False if encountering issues with models across requests
    # Ensure debug=False for deployment
    app.run(debug=True, threaded=False)