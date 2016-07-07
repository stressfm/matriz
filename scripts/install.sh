echo "deb http://matriz.stress.fm/deb_repo jessie main" | tee /etc/apt/sources.list.d/matriz.list
curl http://matriz.stress.fm/deb_repo/matriz_deb.gpg.asc | apt-key add -
apt-get update
apt-get install -y python-pip\
                   jackd2 \
                   python-gst-1.0 \
                   python-gi \
                   libgstrtspserver-1.0-0 \
                   gstreamer1.0-plugins-bad \
                   libgstreamer-plugins-bad1.0 \
                   gir1.2-gst-rtsp-server-1.0 \
                   python-dev \
                   libffi-dev

curl https://raw.githubusercontent.com/stressfm/matriz/master/config/etc-dbus-1-system.d-matriz-jackd.conf | tee /etc/dbus-1/system.d/matriz_jackd.conf >/dev/null
curl https://raw.githubusercontent.com/stressfm/matriz/master/config/boot-config.txt | tee /boot/config.txt > /dev/null
curl https://raw.githubusercontent.com/stressfm/matriz/master/config/boot-cmdline.txt | tee /boot/cmdline.txt >/dev/null
curl https://raw.githubusercontent.com/stressfm/matriz/master/config/supervisord.conf | tee /etc/supervisord.conf >/dev/null
pip install supervisor
sed -i "$(wc -l /etc/rc.local | cut -d' ' -f1)i supervisord -c /etc/supervisord.conf" /etc/rc.local
pip install matriz
reboot
