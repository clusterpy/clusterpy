# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "base"
  requirements = [ "git-core", "python-dev", "python-numpy", "python-scipy", "python-nose","python-pip", "python-matplotlib"]
  _apt_get = ["sudo apt-get update;"]
  _apt_get += ["sudo apt-get install -y", requirements.join(" ")]
  config.vm.provision :shell, :inline => _apt_get.join(" ")

  _apt_get = ["/usr/bin/pip", "install", "Polygon2"]
  config.vm.provision :shell, :inline => _apt_get.join(" ")

end
