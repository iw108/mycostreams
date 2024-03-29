#!/bin/bash

dir=$(dirname "$0")

cd "$dir/.."

if [ ! -d Fiji.app ]
then
  echo "Installing Fiji"
  wget https://downloads.imagej.net/fiji/latest/fiji-nojre.zip \
      && unzip fiji-nojre.zip \
      && rm fiji-nojre.zip \
      && echo "Installation complete"
else
  echo "Fiji already installed"
fi
