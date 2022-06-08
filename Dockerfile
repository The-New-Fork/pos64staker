FROM ubuntu:18.04
RUN apt-get update && \
  apt-get install -y libevent-dev libboost-system-dev libboost-filesystem-dev libboost-chrono-dev libboost-program-options-dev libboost-test-dev libboost-thread-dev build-essential pkg-config libc6-dev m4 g++-multilib autoconf libtool ncurses-dev python-zmq zlib1g-dev wget curl bsdmainutils automake cmake clang libsodium-dev libcurl4-gnutls-dev libssl-dev git unzip python python3-pip python3-venv python3-dev python3-wheel gcc libpq-dev libgnutls28-dev jq htop

WORKDIR /opt

RUN git clone https://github.com/komodoplatform/komodo.git && \
  cd komodo && \
  git checkout master && \
  ./zcutil/build.sh && \
  ./zcutil/fetch-params.sh

ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
  echo $TZ > /etc/timezone

RUN mkdir -p /var/data/komodo/coindata/

COPY ./ /opt/pos64staker
RUN ["chmod", "+x", "/opt/pos64staker/entrypoint.sh"]

# RUN cd pos64staker && \
#   pip3 install virtualenv && \
#   python3 -m venv venv && \
#   . venv/bin/activate && \
#   pip3 install wheel && \
#   apt-cache depends python-pycurl && \
#   pip3 install setuptools base58 slick-bitcoinrpc

RUN cd pos64staker && \
  pip3 install wheel && \
  apt-cache depends python-pycurl && \
  pip3 install setuptools base58 slick-bitcoinrpc

CMD ["/bin/bash", "/opt/pos64staker/entrypoint.sh"]