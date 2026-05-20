# run.py
from app import app

if __name__ == '__main__':
    # debug=True for development, threaded=True for background status polling
    app.run(debug=True, threaded=True)