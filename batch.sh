#!/bin/sh
FILES=./img/*

all=0
success=0
for f in $FILES
do
	if [ -f "$f" ]; then
		echo "Processing $f..."
		./sudoku.py $f

		if [ $? -eq 0 ]; then
			success=$(($success+1))
		fi
		all=$(($all+1))
	fi
done

echo "$((($success / $all) * 100))% of the data, successfully completed"