#
# A simple radio script to get started
# Filenames need to be edited in playlist() and single() sources
#
# icecast host
host = "localhost"
host = "matriz.stress.fm"
# bitrate
#mp3fmt = %mp3(bitrate=192)
mp3fmt = %mp3(bitrate=96)

#lisboa = "192.168.111.121"
lisboa = "192.168.3.45"
porto = "192.168.3.43"
montemor = "192.168.3.44"
file_lisboa = "pi1_brassens.mp3"
file_porto = "pi2_reinhardt.mp3"
file_montemor = "pi3_satie.mp3"

password = "stream$7r355"
set("log.file.path", "/tmp/liquidsoap.log")
set("log.level", 5)

set("server.telnet", true)
set("server.telnet.port", 1234)


#message =
#  "The Savonet team thanks you for using liquidsoap, " ^
#  "and we hope you'll enjoy it!"

# Then we setup our icecast output function.
# Possible options and values are bitrate=64, samplerate=11025, ...
out1 = output.icecast(mp3fmt,host=host,port=8000,password=password)
out2 = output.icecast(mp3fmt,host=host,port=8000,password=password)
out3 = output.icecast(mp3fmt,host=host,port=8000,password=password)
#default = amplify(id="silence_src", 0.00001, noise())
default_lisboa = single(file_lisboa)
default_porto = single(file_porto)
default_montemor = single(file_montemor)
# mp3 stream works
#inlisboa = input.gstreamer.audio(id="lisboain", pipeline="rtspsrc location=\"rtsp://#{lisboa}:8552/stream\" ! rtpmpadepay")
# opus stream not working
inlisboa = input.gstreamer.audio(id="lisboain", pipeline="rtspsrc location=\"rtsp://#{lisboa}:8550/stream\" ! rtpopusdepay")
inporto = input.gstreamer.audio(id="portoin", pipeline="rtspsrc location=\"rtsp://#{porto}:8551/stream\" ! rtpopusdepay")
inmontemor = input.gstreamer.audio(id="montemorin", pipeline="rtspsrc location=\"rtsp://#{montemor}:8552/stream\" ! rtpopusdepay")
#inporto = input.gstreamer.audio(id="portoin", pipeline="rtspsrc location='rtsp://#{porto}:8552/stream' ! rtpmpadepay")
#inporto = input.gstreamer.audio(id="portoin", max=40., pipeline="rtspsrc location=\"rtsp://#{porto}:8554/stream\" latency=4000 ! rtpopusdepay")
#inmontemor = input.gstreamer.audio(id="montemorin", pipeline="rtspsrc location='rtsp://#{montemor}:8552/stream' ! rtpmpadepay")
#log("ooooo#{lisboa}")

out1(mount="lisboa.mp3",
  # The scheduler plays a randomized playlist, or the .ogg file
  # if the playlist fails to stream anything. The playlist can be made
  # of remote URIs.
  fallback(track_sensitive=false, [inlisboa,default_lisboa])
  )
out2(mount="porto.mp3",
  # The scheduler plays a randomized playlist, or the .ogg file
  # if the playlist fails to stream anything. The playlist can be made
  # of remote URIs.
  fallback(track_sensitive=false, [inporto,default_porto])
  #fallback(track_sensitive=false, [inporto,default])
  )
out3(mount="montemor.mp3",
  # The scheduler plays a randomized playlist, or the .ogg file
  # if the playlist fails to stream anything. The playlist can be made
  # of remote URIs.
  fallback(track_sensitive=false, [inmontemor,default_montemor])
  )
