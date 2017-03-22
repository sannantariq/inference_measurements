#!/bin/bash
for i in {0..16}
do
	python kubernetes_average.py exp33
	# echo "Hellslepp.."
	sleep 5
done