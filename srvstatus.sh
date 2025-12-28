#!/bin/bash
proc=`ps axf | grep hugo | grep server`
echo $proc
