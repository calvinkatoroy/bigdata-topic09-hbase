cd /root/hbase-2.6.7-hadoop3
for s in s3 s4 s5; do ./bin/hbase shell -n /mnt/c/Users/calvi/Documents/BIG_DATA/6/Topic09_HBase/$s.rb > /mnt/c/Users/calvi/Documents/BIG_DATA/6/Topic09_HBase/$s.out 2>&1; done
