#!/bin/bash
# usage (dari WSL): HBASE_HOME=/root/hbase-2.6.7-hadoop3 ./hbase/run.sh s3 s4 s5g s7
# menjalankan hbase/<nama>.rb dan menyimpan outputnya ke hbase/output/<nama>.out
D=$(cd "$(dirname "$0")" && pwd)
for s in "$@"; do "${HBASE_HOME:-/root/hbase-2.6.7-hadoop3}/bin/hbase" shell -n "$D/$s.rb" > "$D/output/$s.out" 2>&1; done
