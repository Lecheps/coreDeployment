#!/bin/bash

declare -a arr=("Test_SnowMeltModel"
                "Test_WaterTemperatureModel"
                "Test_SoilTemperatureModel"
                "persist"
                "Test_INCA-N_Classic")

INCADIR=${HOME}/INCA
BASELIBS="-lcore -lboost_date_time -lboost_filesystem -lboost_system -ltinyxml2 -lpthread -ldl"

for i in "${arr[@]}"
do
	echo "$i"
	cd ${INCADIR}/tests/"$i"
	cp ${HOME}/Maketests Makefile
    CPPFILE=main.cpp
	if [ "$i" = "Test_SnowMeltModel" ]
	then
		NAMEBIN=snowModel
		LIBS=$(eval "echo \$BASELIBS | awk '{\$2=\"-lsnowmelt\" OFS \$2} 1'")
	elif [ "$i" = "Test_WaterTemperatureModel" ]
	then
		NAMEBIN=waterTemperatureModel
		LIBS=$(eval "echo \$BASELIBS | awk '{\$2=\"-lwatertemperature\" OFS \$2} 1'")
	elif [ "$i" = "Test_SoilTemperatureModel" ]
	then
		NAMEBIN=soilTemperatureModel
		LIBS=$(eval "echo \$BASELIBS | awk '{\$2=\"-lsoiltemperature -lsnowmelt \" OFS \$2} 1'") 
	elif [ "$i" = "persist" ]
	then
		NAMEBIN=persistModel
		CPPFILE=test_persist.cpp
		LIBS=$(eval "echo \$BASELIBS | awk '{\$2=\"-lpersist\" OFS \$2} 1'") 
	elif [ "$i" = "Test_INCA-N_Classic" ]
	then
		NAMEBIN=inca-nModel
		LIBS=$(eval "echo \$BASELIBS | awk '{\$2=\"-lincan-classic -lwatertemperature -lsoiltemperature -lsnowmelt\" OFS \$2} 1'") 
	fi
	sed -i "s~^LDLIBSOPTIONS=.*~LDLIBSOPTIONS=$LIBS~" Makefile
	sed -i s~^MODELINC=.*~MODELINC=$PWD~ Makefile
	sed -i s~^OBJECTFILES=.*~OBJECTFILES=$NAMEBIN.o~ Makefile
	sed -i s~^\$\(OBJECTFILES\):.*~$\(OBJECTFILES\):\ $CPPFILE~ Makefile
	sed -i s~^NAMEBIN=.*~NAMEBIN=$NAMEBIN~ Makefile
	sed -i s/^CND_DLIB_EXT=.*/CND_DLIB_EXT=a/ Makefile
	make
	make install
    

done


