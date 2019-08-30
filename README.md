# ssbft-template
This repository contains a foundation for building a distributed system based on the SSPBFT structure within minutes. It The underlying network model of the system is that of a fully connected graph and lots of functionality comes modelled with this repo such as communication, testing framework, a web API for exposing various endpoints, metric infrastructure and various other things. This repository is intended to be used together with [Thor](https://github.com/sspbft/thor), which is used to boot up the system with all intended configuration.

## Set up
First, make sure that you have [Python 3.7.2](https://www.python.org/downloads/release/python-372/) installed. Then, follow the commands below.

```
// create your own repo with this repo as template and clone into it and then run the following commands
python3.7 -m venv env
source ./env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
chmod +x ./scripts/*
```

Instructions for how to run this application without using [Thor](https://github.com/practicalbft/thor) (which you should not, since Thor was built for this exact use case) will be added later.

### Linting
The code base is linted using [flake8](https://pypi.org/project/flake8/) with [pydocstyle](https://github.com/PyCQA/pydocstyle), so make sure to lint the code by running `flake8` before pushing any code.

### Testing
[unittest](https://docs.python.org/2/library/unittest.html) is setup so add appropriate unit tests in the `tests/unit_tests` folder (make sure the file starts with `test_`) and appropriate integration tests in the `tests/integration_tests` folder. Tests can run as seen below.

```
./scripts/test              # runs all tests
./scripts/test unit         # runs only unit tests
./scripts/test it           # runs only integration tests
./scripts/test <pattern>    # runs all test files with a filename matching pattern
```

### Travis integration
Both linting and testing is setup to be run for all Pull Requests and on each push to master by Travis.

## System description

### Ports
Each running node uses three ports: one for the API (default to `400{node_id}`), one for the main communication channel running over TCP with other nodes (`500{node_id}`), one for exposing metrics to the Prometheus scraper (`300{node_id}`) and lastly one for the self-stabilizing UDP communication channel (`700{node_id}`). Node with id `1` would therefore be using ports `3001`, `4001`, `5001` and `7001` for example. Note that port ranges `7000-->` was selected rather than `6000-->` since many firewalls on PlanetLab block port `6000` from being used.

| Port number   | Service                       | 
| ------------- |:-----------------------------:|
| 300{ID}       | Prometheus metrics endpoint   |
| 400{ID}       | REST API                      |
| 500{ID}       | Inter-node communication      |
| 700{ID}       | Inter-node communication      |