# This simply clears the .tmp folder of any crap left in it.
sleep 5 # Give the system enough time to rest
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
rm -rf $SCRIPT_DIR/.tmp/*
