# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "base"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

$requirements = <<END
sudo apt-get update -qq
sudo apt-get install -y git-core
sudo apt-get install -y python-dev python-numpy
sudo apt-get install -y python-scipy
sudo apt-get install -y python-nose python-pip python-matplotlib
END
  config.vm.provision :shell, :inline => $requirements

  pipinstall = "/usr/bin/pip install Polygon2"
  config.vm.provision :shell, :inline => pipinstall

end
