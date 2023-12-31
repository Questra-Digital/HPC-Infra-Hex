# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 2.3.0"

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.box_version = "20230729.0.0"
  config.ssh.insert_key = false
  config.vm.provider "virtualbox"

  config.vm.provider :virtualbox do |v|
    v.memory = 1536
    v.cpus = 1
    v.linked_clone = true
  end

  # Define three VMs with static private IP addresses.
  boxes = [
    { :name => "master",        :ip => "192.168.56.2" },
    { :name => "node1-non-gpu", :ip => "192.168.56.3" },
    { :name => "node2-gpu",     :ip => "192.168.56.4" },
    { :name => "node3-gpu",     :ip => "192.168.56.5" },
  ]

  # Configure boxes
  boxes.each do |opts|
    config.vm.define opts[:name] do |config|
      config.vm.hostname = opts[:name] + ".k8s.test"
      config.vm.network :private_network, ip: opts[:ip]

      # Provision all the VMs using Ansible after last VM is up.
      if opts[:name] == "node3-gpu"
        config.vm.provision "ansible" do |ansible|
          ansible.playbook = "playbook/main.yml"
          ansible.inventory_path = "playbook/inventory"
          ansible.config_file = "playbook/ansible.cfg"
          ansible.limit = "all"
        end
      end
    end
  end
end