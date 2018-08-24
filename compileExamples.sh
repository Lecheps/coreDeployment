#!/bin/bash

declare -a arr=("INCA-N_Classic"
                "persist"
                "Snow_melt_model"
                "Soil_temperature_model"
                "Water_temperature_model")

BASEDIR=${HOME}

export baseInclude=$(cat Makelib | grep ^INCLUDE)
export persistDir="-I${BASEDIR}/INCA/examples/persist"
export waterTempDir="-I${BASEDIR}/INCA/examples/Water_temperature_model"
export soilTempDir="-I${BASEDIR}/INCA/examples/Soil_temperature_model"
export snowDir="-I${BASEDIR}/INCA/examples/Snow_melt_model"


for i in "${arr[@]}"
do
	echo "$i"
	cd ${BASEDIR}/INCA/examples/"$i"
	cp ${HOME}/Makelib Makefile
	if [ "$i" = "INCA-N_Classic" ]
	then
		INCSTR="$baseInclude\ $persistDir\ $waterTempDir\ $soilTempDir\ $snowDir"
		NAMELIB=incan-classic
		CPPFILE=INCA-N_Classic.cpp
	elif  [ "$i" = "persist" ]
	then
        INCSTR="$baseInclude\ $waterTempDir\ $soilTempDir\ $snowDir"
		NAMELIB=persist
		CPPFILE=PersistModel.cpp
	elif  [ "$i" = "Snow_melt_model" ]
	then
        INCSTR="$baseInclude"
		NAMELIB=snowmelt
		CPPFILE=SnowMeltModel.cpp
	elif  [ "$i" = "Soil_temperature_model" ]
	then
        INCSTR="$baseInclude\ $snowDir"
		NAMELIB=soiltemperature
		CPPFILE=SoilTemperatureModel.cpp
	elif  [ "$i" = "Water_temperature_model" ]
	then
        INCSTR="$baseInclude"
		NAMELIB=watertemperature
		CPPFILE=WaterTemperatureModel.cpp  
	fi
	sed -i "s~^INCLUDE=.*~$INCLUDE\ $INCSTR~" Makefile
	sed -i s~^LIBRARY=.*~LIBRARY=$NAMELIB~ Makefile
	sed -i s~^\$\(OBJECTFILES\):.*~$\(OBJECTFILES\):\ $CPPFILE~ Makefile
	sed -i s/^CND_DLIB_EXT=.*/CND_DLIB_EXT=so/ Makefile
	make
	make install
	sed -i s/^CND_DLIB_EXT=.*/CND_DLIB_EXT=a/ Makefile
    make clean
	make
	make install
done
