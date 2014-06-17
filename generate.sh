#!/bin/sh
FILES=./img/*

all=0
success=0
for f in $FILES
do
	if [ -f "$f" ]; then
		echo "Processing $f..."
		python ./sudoku_generate.py $f

		if [ $? -eq 0 ]; then
			success=$(($success+1))
		fi
		all=$(($all+1))
	fi
done

echo "Processed $((all)) images."
echo "Successfull: $(($success))"