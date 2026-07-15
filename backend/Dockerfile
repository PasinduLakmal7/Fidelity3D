FROM python:3.10-slim

WORKDIR /app

# Copy all requirements files
COPY api_gateway/requirements.txt ./api_req.txt
COPY lowpoly_worker/requirements.txt ./lowpoly_req.txt
COPY premium_worker/requirements.txt ./premium_req.txt
COPY animation_worker/requirements.txt ./anim_req.txt

# Install all dependencies
RUN pip install --no-cache-dir -r api_req.txt -r lowpoly_req.txt -r premium_req.txt -r anim_req.txt

# Copy backend code
COPY . .

ENV PYTHONPATH=/app
