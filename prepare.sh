#@IgnoreInspection BashAddShebang
sudo apt-get update
sudo apt-get install virtualenv -y
sudo apt-get install python3-pip -y

pip3 install --upgrade pip

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo service mongod start

virtualenv env
source env/bin/activate

pip3 install certifi==2017.4.17
pip3 install chardet==3.0.4
pip3 install idna==2.5
pip3 install requests==2.18.1
pip3 install retrying==1.3.3
pip3 install six==1.10.0
pip3 install urllib3==1.21.1
pip3 install nose==1.3.7
pip3 install simplejson==3.11.1
pip3 install cachetools==2.0.0
pip3 install pymongo==3.4.0
pip3 install tensorflow=1.2.1
pip3 install Keras==2.0.6
pip3 install tensorflow==1.2.1
pip3 install pandas==0.20.3
pip3 install matplotlib==2.0.2
pip3 install sklearn==0.18.2

pip3 install git+https://github.com/tms1337/python3-krakenex.git
pip3 install git+https://github.com/s4w3d0ff/python-poloniex
pip3 install git+https://github.com/ericsomdahl/python-bittrex.git
pip3 install git+https://github.com/tms1337/bitfinex.git
