#!/bin/bash



home="$(realpath ~)"
install_pcm () {
    cd $home
    git clone --recursive https://github.com/intel/pcm
    cd pcm
    mkdir build
    cd build
    cmake ..
    cmake --build .

    cmake --build . --parallel

    ls bin
    # sudo apt install libasan11 
}

install_mlc () {
    cd $home
    wget https://downloadmirror.intel.com/834254/mlc_v3.11b.tgz
    mkdir -p mlc
    mv mlc_v3.11b.tgz mlc
    cd mlc
    tar -xvf mlc_v3.11b.tgz

    ls Linux
}

install_rdt () {
    cd $home
    git clone https://github.com/intel/intel-cmt-cat.git
    cd intel-cmt-cat/
    make
    sudo make install
    
    sudo modprobe msr
}

install_iperf3 () {
    cd $home
    git clone https://github.com/esnet/iperf.git
    cd iperf
    git checkout 3.18
    ./bootstrap.sh
    ./configure; make; sudo make install
    sudo ldconfig
}

install_netperf () {
    cd $home
    git clone https://github.com/HewlettPackard/netperf.git
    cd netperf
    cp $home/Fast-and-Safe-IO-Memory-Protection/utils/tcp/netperf-logging.diff .
    git apply netperf-logging.diff
    make CFLAGS=-fcommon
    sudo make install
}



cd $home
git clone https://github.com/Terabit-Ethernet/Understanding-network-stack-overheads-SIGCOMM-2021
git clone https://github.com/aliireza/ddio-bench.git

sudo utils/setup-envir.sh --home /users/schai \
    --intf enp202s0f0np0 \
    --addr 10.10.1.2

install_pcm
install_mlc
install_rdt
install_iperf3
install_netperf