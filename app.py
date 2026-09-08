import os
from app.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    print(f"\n==================================================")
    print(f"  RaktDaan Blood Bank Management System Server")
    print(f"  Website Link: http://127.0.0.1:{port}")
    print(f"==================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
