#!/bin/bash

echo "This require admin permissions to Install."
read -p "Do you wish to continue?" -n 1 -r 
if [![ $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborting installation"
else
    echo "----------Installing Ruby 2.6.5----------"
    sudo apt update
    sudo apt install autoconf bison build-essential libssl-dev libyaml-dev libreadline6-dev zlib1g-dev libncurses5-dev libffi-dev libgdbm5 libgdbm-dev
    git clone https://github.com/rbenv/rbenv.git ~/.rbenv
    echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(rbenv init -)"' >> ~/.bashrc
    source ~/.bashrc
    git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build
    rbenv install --verbose 2.6.5
    rbenv global 2.6.5
    echo "gem: --no-document" > ~/.gemrc
    gem install bundler
    gem install rails -v 6.0.1
    rbenv rehash
    echo "----------Installing sqlite----------"
    sudo apt-get install libsqlite-dev
    echo "----------Updating Rails Gems----------"
    bundle
    sudo apt-get install curl
    curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
    echo "----------Installing NodeJS----------"
    sudo apt-get install nodejs
    echo "----------Installing Yarn----------"
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
    sudo apt update
    sudo apt install yarn
    echo "----------Installing Webpacker----------"
    rails webpacker:install
    echo " "
    echo "VIRNST installed!"

fi
