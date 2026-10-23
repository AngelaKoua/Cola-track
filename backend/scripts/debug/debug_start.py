import sys
import traceback

try:
    from app.main import app
    print("app loaded successfully")
except Exception as e:
    print("FATAL ERROR LOADING APP:")
    traceback.print_exc()
