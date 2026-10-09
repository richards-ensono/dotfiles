#!/bin/bash
# shellcheck disable=SC1091
set -e # Exit immediately if a command exits with a non-zero status

# Function to check and install Ansible
install_ansible() {
  if command -v ansible >/dev/null 2>&1; then
    echo "Ansible is already installed."
    return
  fi

  echo "Installing Ansible..."
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    case "$ID" in
    ubuntu | debian)
      if [[ ("$ID" == "ubuntu" && "$VERSION_ID" == "24.04") || ("$ID" == "debian" && "$VERSION" == *"trixie"*) ]]; then
        echo "Running on $ID $VERSION_ID; using distribution-provided Python and Ansible packages."
      fi

      sudo apt update
      sudo apt install -y --fix-broken wget curl git python3-debian ansible
      ;;
    fedora)
      sudo dnf install -y wget curl git ansible
      ;;
    centos | rhel)
      sudo yum install -y wget
      sudo yum install -y curl
      sudo yum install -y epel-release
      sudo yum install -y ansible
      ;;
    arch)
      sudo pacman -Syu --noconfirm ansible
      ;;
    *)
      echo "Unsupported Linux distribution: $ID"
      exit 1
      ;;
    esac
  else
    echo "Could not detect the Linux distribution."
    exit 1
  fi
}

# Function to install with ansible-galaxy
install_roles() {
  REQUIREMENTS="${HOME}/.local/share/chezmoi/scripts/ansible/requirements.yml"
  if [ ! -f "$REQUIREMENTS" ]; then
    echo "Error: Playbook '$REQUIREMENTS' not found!"
    exit 1
  fi

  echo "Installing requirements"
  ansible-galaxy install -r "$REQUIREMENTS"
}

# Function to run the playbook
run_playbook() {
  PLAYBOOK="${HOME}/.local/share/chezmoi/scripts/ansible/playbook.yml"
  if [ ! -f "$PLAYBOOK" ]; then
    echo "Error: Playbook '$PLAYBOOK' not found!"
    exit 1
  fi

  echo "Running Ansible playbook: $PLAYBOOK"
  ansible-playbook "$PLAYBOOK" -i ./inventory/hosts.yml --ask-become-pass
}

# Main Execution
install_ansible
install_roles
run_playbook
