#!/bin/bash
if [[ ! -e /home/live/pids/st$1.pid ]]; then
    touch /home/live/pids/st$1.pid
fi
line=$(tail -n 1 /home/live/pids/st$1.pid)
linelen=${#line}
ovropt="overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2"
#ovropt="overlay=x=(main_w-overlay_w):y=(main_h-overlay_h)/(main_h-overlay_h)"
ovr="-i /home/live/wahyu.insta.png -filter_complex $ovropt"
cmd="ffmpeg -rtsp_transport tcp -i $2 -an -pix_fmt yuv420p -profile:v baseline -s 640x360 -bufsize 2048k -vb 400k -maxrate 800k -deinterlace -vcodec libx264 -preset ultrafast -tune zerolatency -an -f flv rtmp://$5:1935/cctv/$1?token=$4"
#cmd="ffmpeg -rtsp_transport tcp -i $2 -acodec libmp3lame  -ar 44100 -b:a 128k -pix_fmt yuv420p -profile:v baseline -s 640x360 -bufsize 2048k -vb 400k -maxrate 800k -deinterlace -vcodec libx264 -preset medium -g 30 -r 30 -threads 8 -f flv rtmp://stream2.banjarkab.go.id:1935/cctv/$1?token=$4"
#cmd="ffmpeg -rtsp_transport tcp -i $2 -an -preset ultrafast -vcodec libx264 -tune zerolatency -b 900k -f flv rtmp://103.133.56.188:1935/cctv/$1?token=$4"
#cmd="ffmpeg -rtsp_transport tcp -i $2 -an -preset ultrafast -vcodec libx264 -tune zerolatency -b 900k -f flv rtmp://stream2.banjarkab.go.id:1935/cctv/$1?token=$4"
#cmd="ffmpeg -y -loglevel debug -rtsp_transport tcp -i $2 -acodec libmp3lame  -ar 44100 -b:a 128k -pix_fmt yuv420p -profile:v baseline -s 640x360 -bufsize 2048k -vb 400k -maxrate 800k -deinterlace -vcodec libx264 -preset medium -g 30 -r 30 -threads 8 -f flv rtmp://103.133.56.188:1935/cctv/$1?token=$4"
#cmd="ffmpeg -rtsp_transport tcp -i $2 -c copy -f flv rtmp://localhost:1935/streaming/$1"
#cmd="ffmpeg -rtsp_transport tcp -i $2 -c copy -f flv rtmp://103.133.56.188:1935/cctv/$1?token=$4"
if [[ $line ]]
then
	echo "cek pid $line"
	if ps -p $line > /dev/null
	then
		echo "$1 Already Running at pid $line."
	else 
		$cmd &
		echo $! > /home/live/pids/st$1.pid
	fi
else
	$cmd &
	echo $! > /home/live/pids/st$1.pid
fi
