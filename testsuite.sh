#!/bin/sh

for f in `find -name test.py`;
do
	dir=`dirname $f`
	echo 'Executing tests in' $dir
	cd $dir
	nosetests --with-nosexunit test.py
	cd ..

done
