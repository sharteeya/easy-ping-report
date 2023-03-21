# EZPing
EZPing is an experimental ping stablility testing tool build by Python.

The target is to make ping testing much more easier and make data visualization.

## Package require
1. matplotlib
2. jinja2 (if not installed by default)
3. requests (if not installed by default)

## Supported OS
- Linux system

## Installation
1. `git clone` this repository.
2. `pip3 install` the packages mention above.
3. `python3 ezping -h` for helping.

## Features
1. Set up ping time by short string or time pattern.
2. Generate HTML report, csv, ping figure after the test.
3. Send brief notification to client.
4. Group loss packets and list informations.

## HTML report
- Use BootStrap 5 theme and jinja2 to build.
