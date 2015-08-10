#!/usr/bin/bash

# this file should be sourced for shell to export project's environment

usage() {
    printf "Usage: $0 [path to sandbox]\n"
    printf "Description:\n"
    printf "  Source project environment from path to sandbox.\n"
    printf "  Current working directory is used if path is not provided.\n"
}

myfault=0

if [ $# -gt 1 ]; then
    myfault=1;
    printf "Error: only a single sandbox path is expected.\n";
    usage;
fi

if [ $# -eq 1 ]; then
    sbox=$1
    if [ ! -d $sbox ]; then
	printf "Error: provided path is not a sandbox directory\n"
	usage
	myfault=1
    fi
else
    sbox='.'
fi

if [ $myfault -eq 0 ]; then
    tempfoo="export_env.sh"
    TMPFILE=`mktemp /tmp/${tempfoo}.XXXXXX`
    if [ $? -eq 0 ]; then
	vars=$(export_env.py -s $sbox 2>$TMPFILE)
	if [ $? -eq 0 ]; then
            echo $vars > $TMPFILE
	    . $TMPFILE
	    for d in $(find $AC_PROJ_LOC -type d | grep -v '__$'); do
	       b=$(basename $d) 
	       if [ ${b:0:1} != '.' ]; then
	           pyadds=${d}${pyadds:+:}${pyadds}
	       fi
	    done
	    export PYTHONPATH=${pyadds}${PYTHONPATH:+:}$PYTHONPATH
	    rm $TMPFILE
	else
	    printf "Error: failed to create environment for project\n"
	    printf "Message:\n"
	    cat $TMPFILE
	    rm $TMPFILE
	fi
    else
        printf "Error: failed to create temporary environment file.\n"
	printf "Possible correction:\n"
	printf "  1. Make sure $TMPDIR is defined\n"
	printf "  2. Make sure writing permissions to $TMPDIR\n"
    fi
fi

