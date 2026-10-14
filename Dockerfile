FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 PORT=8765 VNC_PORT=6080 \
    AUTOTEST_DATA=/data GECKODRIVER=/usr/local/bin/geckodriver

RUN apt-get update \
 && apt-get install -y --no-install-recommends firefox-esr curl ca-certificates fonts-liberation fonts-noto-core \
      xvfb x11vnc novnc websockify \
 && rm -rf /var/lib/apt/lists/*

# geckodriver (chọn đúng kiến trúc)
ARG GECKO_VERSION=0.36.0
RUN set -eux; \
    case "$(dpkg --print-architecture)" in amd64) A=linux64;; arm64) A=linux-aarch64;; esac; \
    curl -fsSL "https://github.com/mozilla/geckodriver/releases/download/v${GECKO_VERSION}/geckodriver-v${GECKO_VERSION}-${A}.tar.gz" \
      | tar -xz -C /usr/local/bin; \
    chmod +x /usr/local/bin/geckodriver

WORKDIR /srv
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
COPY testcases ./testcases
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

VOLUME ["/data"]
EXPOSE 8765 6080
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "-m", "app"]
