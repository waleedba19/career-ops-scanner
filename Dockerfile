# CareerOps Scanner — immortal agent image.
# All Python deps + Chromium are baked in; workflow runs with zero installs.
FROM python:3.12-slim

WORKDIR /app

# System deps: Chromium runtime libs (Playwright), git, curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libnspr4 libnss3 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 libxshmfence1 \
    curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && python -m playwright install chromium --with-deps \
    && rm -rf /root/.cache/ms-playwright/.links 2>/dev/null || true

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV SCAN_MODE=adaptive
ENV CAREEROPS_TIER_CAP=3

CMD ["python", "scanner.py"]
