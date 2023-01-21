for timfile in ./tests/*
do 
	echo $timfile
	python3 ./TimingDiagrammer.py $timfile
	read val
done
