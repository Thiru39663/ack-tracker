# ============================================
# ack-tracker_v1.py
# Cloud Run Flask app to record acknowledgements
# ============================================

from flask import Flask, request, render_template_string
from datetime import datetime
import pandas as pd
import os
from pathlib import Path

# Base directory for storing logs
BASE_DIR = Path("/app")  # Works in Cloud Run container
ACK_LOG = BASE_DIR / "ack_log.csv"

app = Flask(__name__)

# HTML confirmation page template
ACK_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Acknowledgement Recorded</title>
  <style>
    body {{
      background-color: #f4f8fb;
      font-family: Arial, sans-serif;
      color: #333;
      text-align: center;
      padding-top: 10%;
    }}
    .card {{
      background: #fff;
      display: inline-block;
      padding: 30px 50px;
      border-radius: 12px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    h2 {{ color: #2d6cdf; }}
    .small {{ font-size: 0.9em; color: #777; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>✅ Acknowledgement Recorded Successfully</h2>
    <p>Thank you for confirming receipt of this awareness message.</p>
    <p class="small">Timestamp: {{timestamp}}</p>
    <p class="small">IP Address: {{ip}}</p>
  </div>
</body>
</html>
"""


def log_acknowledgement(token, ip_address):
    """Append acknowledgement info into CSV log file."""
    ts = datetime.utcnow().isoformat() + "Z"
    record = pd.DataFrame([{"timestamp_utc": ts, "ip_address": ip_address, "token": token}])
    header = not ACK_LOG.exists()
    record.to_csv(ACK_LOG, mode="a", header=header, index=False)


@app.route("/ack/<token>", methods=["GET"])
def acknowledge(token):
    """Endpoint for acknowledgement link."""
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    try:
        log_acknowledgement(token, ip)
    except Exception as e:
        return f"Error recording acknowledgement: {e}", 500
    return render_template_string(ACK_PAGE, timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), ip=ip)


@app.route("/", methods=["GET"])
def home():
    """Simple root endpoint for Cloud Run health check."""
    return "ACK Tracker v1 is running ✅"


if __name__ == "__main__":
    # For local testing before Cloud Run deploy
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
