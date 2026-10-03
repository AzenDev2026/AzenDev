# sysfetch
sysfetch is a terminal tools to show the system info and custom ascii logo
<img width="2560" height="1600" alt="Screenshot_20261003_111146" src="https://github.com/user-attachments/assets/695ee0cb-e9a8-4ede-89d2-f61cff33b43b" />

## install
install the whole folder to your path
example ~/Desktop
## run
cd ~/Desktop/sysfetch 
chmod +x sysfetch.py
./sysfetch.py

## requirment
python 3.12 +

## others
small tux ascii logo to use （turn into the code mode not preview)
     .--. 
    |o_o |
    |:_/ |
   //   \ \
  (|     | )
 /'\_   _/`\
 \___)=(___/ 
 ## rules
 1.the ascii.txt maxium limit is 100 lines of logo
 2.only replace the path in conf.txt

 ## customize
 1.change the path in conf.txt {ascii-logo},remember it must be a .txt,example:
 "
 {ascii-logo} : lightblue
 /path/you/want/to/put/ascii.txt

 {sys-info}
 /etc/os-release
 "
 
