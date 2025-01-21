# SPDX-License-Identifier: Apache-2.0
#!/bin/bash

cd /app

# Wait for 5 seconds to allow services to initialize
sleep 5
echo "Starting server..."

# Start the FastAPI server with uvicorn using the virtual environment's Python
echo "Running uvicorn with uv..."
uv run python -m uvicorn GraphCap.server.app:app \
    --host "0.0.0.0" \
    --port 32100 \
    --reload \
    --reload-dir /app/GraphCap
