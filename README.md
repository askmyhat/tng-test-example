# tng-test-example

This repository contains an example of test for deployed on Sonata Emulator VNF

## Instruction

### Requirements

- git
- ansible

### Prerequisites

First, we need to install [son-emu](https://github.com/sonata-nfv/son-emu):

```shell
cd
git clone https://github.com/containernet/containernet.git
cd ~/containernet/ansible
sudo ansible-playbook -i "localhost," -c local install.yml

cd
git clone https://github.com/sonata-nfv/son-emu
cd ~/son-emu/ansible
git checkout v3.1
sudo ansible-playbook -i "localhost," -c local install.yml

```

and [son-cli](https://github.com/sonata-nfv/son-cli)

```shell
git clone http://github.com/sonata-nfv/son-cli
cd son-cli
sudo python3 setup.py install
```

After that we need to create and configure development workspace:

```shell
# Create workspace in $HOME/.son-workspace
son-workspace --init --workspace

# Add Emulator to the list of target platforms
son-access config --platform_id emu --new --url http://127.0.0.1:5000 --default
```

### Creation of network service

The service is located in `snort/`. It is almost the same as `sonata_snort_ids_vnf` with the difference in snort rules.

### Preparing test

We need two extra instances to trigger snort rules.

Server image is almost the same as `sonata_apache_server_vnf` with added static content.

Client image can be any image which supports required functions for testing purposes. For example, if your requests are written in python, you can create your image as follows:
- use base image `python:onbuild`
- add your code to the source directory
- generate `requirements.txt` with `pipreqs <source directory>`
- build image

Now we need to write test itself. You can see an example in `test_snort.py`. It executes curl command on client using Docker SDK and compares Snort Alerts with expected.


### Running test

Run Emulator:
```shell
sudo python topology.py
```

Open new terminal window and deploy all instances:

```shell
# Build docker images
docker build -t client_vnf -f ./client/docker/Dockerfile ./client/docker
docker build -t server_vnf -f ./server/docker/Dockerfile ./server/docker
docker build -t snort_vnf -f ./snort/docker/Dockerfile ./snort/docker

# create Snort VNF package
son-package --project snort/ns -n snort/snort-service

# upload and deploy Snort VNF
son-access --platform emu push --upload ./snort/snort-service.son
son-access --platform emu push --deploy latest

# Add links
son-emu-cli compute start -d dc1 -n client -i client_vnf
son-emu-cli compute start -d dc2 -n server -i server_vnf
son-emu-cli network add -b -src client:client-eth0 -dst snort_vnf:input
son-emu-cli network add -b -src snort_vnf:output -dst server:server-eth0
```

Run test:

```shell
python3 -W ignore test_snort.py
```
