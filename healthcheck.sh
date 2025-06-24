#!/bin/sh
# healthcheck.sh - Script kiểm tra sức khỏe đơn giản cho container

# Lệnh này sẽ tìm trong danh sách tiến trình một dòng chứa "python main.py".
# `grep -v grep` dùng để loại bỏ chính tiến trình grep khỏi kết quả tìm kiếm.
# Nếu tìm thấy, ps sẽ trả về exit code 0 (thành công).
# Nếu không tìm thấy, exit code sẽ khác 0 (thất bại).
if ps -ef | grep -v grep | grep "python main.py"; then
  exit 0 # Trả về 0 -> Báo cho Docker là container đang "Healthy"
else
  exit 1 # Trả về 1 -> Báo cho Docker là container đang "Unhealthy"
fi
