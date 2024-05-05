# Smart Dashcam
A dashcam with smart features


## Installation
Run the setup.sh file present in the setup folder.
cd setup
sudo chmod +x setup.sh
sh setup.sh

Install the wireless hotspot
git clone https://github.com/idev1/rpihotspot.git
cd rpihotspot
sudo chmod +x setup-network.sh 
sudo ./setup-network.sh --install --ap-ssid="abc-1" --ap-password="password@1" --ap-password-encrypt 
--ap-country-code="IN" --ap-ip-address="10.0.0.1" --wifi-interface="wlan0"

Setup the dashcam launcher

sudo nano /lib/systemd/system/dashcam.service

Add the following lines in that file:

 [Unit]
 Description=Dashcam Service
 After=multi-user.target

 [Service]
 Type=idle
 ExecStart=/usr/bin/python /home/madhukar/Desktop/dashcam/dashcam_launcher.sh

 [Install]
 WantedBy=multi-user.target

Then add the file to systemctl daemon
sudo systemctl daemon-reload
sudo systemctl enable dashcam.service


Done!
