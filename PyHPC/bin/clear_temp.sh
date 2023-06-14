# This simply clears the .tmp folder of any crap left in it.
sleep 5 # Give the system enough time to rest
setenv ROOTDIR  `dirname $0`
setenv SCRIPT_DIR `cd $ROOTDIR && pwd`
rm -rf $SCRIPT_DIR/.tmp/*
