#!/bin/sh
# Màn hình ảo + VNC/noVNC để xem Firefox khi chọn "Hiện cửa sổ" (chạy trong container không có màn hình thật).
set -e
export DISPLAY=:99
Xvfb :99 -screen 0 1440x960x24 -nolisten tcp >/dev/null 2>&1 &
sleep 1
if [ -n "$VNC_PASSWORD" ]; then
  x11vnc -storepasswd "$VNC_PASSWORD" /tmp/vncpass >/dev/null 2>&1
  AUTH="-rfbauth /tmp/vncpass"
else
  AUTH="-nopw"
fi
x11vnc -display :99 -forever -shared -rfbport 5900 -localhost $AUTH -quiet >/dev/null 2>&1 &
websockify --web /usr/share/novnc 6080 localhost:5900 >/dev/null 2>&1 &
echo "noVNC: http://<host>:6080/vnc.html"
exec "$@"
