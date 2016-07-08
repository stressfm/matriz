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

curl https://raw.githubusercontent.com/stressfm/matriz/master/config/etc-dbus-1-system.d-matriz_jackd.conf > /etc/dbus-1/system.d/matriz_jackd.conf
curl https://raw.githubusercontent.com/stressfm/matriz/master/config/boot-config.txt > /boot/config.txt
curl https://raw.githubusercontent.com/stressfm/matriz/master/config/boot-cmdline.txt > /boot/cmdline.txt
curl https://raw.githubusercontent.com/stressfm/matriz/master/config/supervisord.conf > /etc/supervisord.conf
pip install supervisor
sed -i "$(wc -l /etc/rc.local | cut -d' ' -f1)i for cpu in /sys/devices/system/cpu/cpu[0-9]*; do echo -n performance > $cpu/cpufreq/scaling_governor; done" /etc/rc.local
sed -i "$(wc -l /etc/rc.local | cut -d' ' -f1)i sudo mount -o remount,size=256M /dev/shm" /etc/rc.local
sed -i "$(wc -l /etc/rc.local | cut -d' ' -f1)i supervisord -c /etc/supervisord.conf" /etc/rc.local
pip install matriz
reboot
