#!/bin/sh
FILES=./img/*

success=0
for f in $FILES
do
	if [ -f "$f" ]; then
		echo "Processing $f..."
		./sudoku.py $f

		if [ $? -eq 0 ]; then
			success=$(($success+1))
		fi
	fi
done

echo "$((($success / 45) * 100))% of the data, successfully completed"