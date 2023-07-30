## Development environment Setup


### Install Vagrant
https://developer.hashicorp.com/vagrant/downloads

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vagrant
```

### Install Virtualbox
https://www.virtualbox.org/wiki/Linux_Downloads

sudo dpkg -i ~/Downloads/virtualbox-7.0_7.0.10-158379~Ubuntu~jammy_amd64.deb
sudo apt --fix-broken install

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/oracle-virtualbox-2016.gpg] https://download.virtualbox.org/virtualbox/debian jammy contrib" | sudo tee /etc/apt/sources.list.d/virtualbox.list

wget -O- https://www.virtualbox.org/download/oracle_vbox_2016.asc | sudo gpg --dearmor -o /usr/share/keyrings/oracle-virtualbox-2016.gpg

sudo apt-get update && sudo apt-get install virtualbox-7.0

### Install Ansible
https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html

curl https://bootstrap.pypa.io/get-pip.py -o ~/Downloads/get-pip.py

python3 ~/Downloads/get-pip.py --user

python3 -m pip install --user ansible

python3 -m pip install --user argcomplete

activate-global-python-argcomplete --user
source ~/.bash_completion