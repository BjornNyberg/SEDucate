# SEDucate

SEDucate are a set of scripts designed to create tailored sedimentary log exercises and assessments for an active-learning environment. 

## User Guide

The SEDucate are based on two simple scripts [Create Logs](https://github.com/BjornNyberg/SEDucate/blob/main/CreateLogs.py) and [Create Logs from Maps](https://github.com/BjornNyberg/SEDucate/blob/main/CreateLogs_Map.py). To use the scripts use the following steps:
1. Download the repository and extract the contents into a working directory. 
2. Open the CreateLogs.py in an [IDE](https://en.wikipedia.org/wiki/Integrated_development_environment) and navigate to the end of the script.
3. The essential parameters to change of the script are:
    a) outDir = output directory file
    b) cNum = number of individual pdf files to create
    c) fNum = number of facies/facies associations to assign per log
    d) lNum = number of logs to create per pdf
 4. To add or remove facies or facies associations, navigate to the [Images](https://github.com/BjornNyberg/SEDucate/tree/main/Images) folder and create a new directory (or remove) for each new facies or facies associations. Within each directory place one of more image files that correspond to that facies/facies associations as defined in a sedimentary log. For each new facies/facies associations make sure to edit the probabilityMatrix.xlsx excel file to correspond with the new probabilities between each facies or facies assocaitions. 
 5. To create a sedimentary log based on a custom paleogeographic map use the CreateLogs_Map.py script and repeat steps 3 and 4. Edit the paleoMap = 'os.path.join(dirname,'maps\map.png')' statement in line 135 to point to the RGB paleogeographic image file. 
 6. Edit line 17 "sEnv = {colors[0]:'delta',colors[1]:'floodplain',colors[2]:'shoreface',colors[3]:'channel'}" with the new colors that corresponds to the paleoMap in step #5 and corresponding facies/facies associations and probabilityMatrix in step #4.


