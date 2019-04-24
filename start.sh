#!/bin/sh

resp=`ps -ef | grep python | wc -l`
echo $resp

bash << EOF

cd /Users/shenwei/Python-dir/ai_home

if [ "$resp" -eq "1" ]
then
	echo "starting ..."
	nohup python ser.py 2>&1 &
	echo "Done."
else
	echo "started!"
fi
EOF

