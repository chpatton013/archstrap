mirrorlist_url = "https://www.archlinux.org/mirrorlist"
mirrorlist_params = "country=US&protocol=https&use_mirror_status=on"
$provision = <<-PROVISION
curl --silent '#{mirrorlist_url}/?#{mirrorlist_params}' |
  sed --expression 's/^#Server/Server/' >/etc/pacman.d/mirrorlist
pacman --sync --refresh --noconfirm arch-install-scripts binutils make python python-pip

cat <<PROFILE >/etc/profile.d/archstrap.sh
export PYTHONDONTWRITEBYTECODE=1
PROFILE
PROVISION

Vagrant.configure("2") do |config|
  config.vm.box = "archlinux/archlinux"
  config.vm.provision "shell", inline: $provision
end
