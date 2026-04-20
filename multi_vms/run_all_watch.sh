#!/bin/bash

# Then run the main script

./run_all.sh &
main_pid=$!

# We need to wait some seconds to allow the SRIOV functions to take effect

sleep 20

# Start the watcher script

./watch-nic-drops.sh > watcher.log &
watcher_pid=$!

# Wait for the main script to finish

wait "$main_pid"

# Finally, kill the watcher script

kill "$watcher_pid"
