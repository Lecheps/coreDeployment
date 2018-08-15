#----------------------------------------------------------------------
# Environment
MKDIR=mkdir
CP=cp
GREP=grep
NM=nm
CCADMIN=CCadmin
CC=gcc
CCC=g++
CXX=g++
FC=gfortran
AS=as
RM=rm
AR=ar
RANLIB=ranlib
#----------------------------------------------------------------------
# Macros
CND_PLATFORM=Linux
CND_DLIB_EXT=so
CND_CONF=Release
CND_DISTDIR=dist
CND_BUILDDIR=build
#----------------------------------------------------------------------
# SOURCE FOLDERS
BASEDIR=/home/jose-luis
BOOSTDIR=$(BASEDIR)/boost_1_68_0
TINYXMLDIR=$(BASEDIR)/tinyxml2
INCASRC=${BASEDIR}/INCA/src
INCAINC=${BASEDIR}/INCA/include
SQLITEDIR=$(BASEDIR)/sqlite
#----------------------------------------------------------------------
# Projects to be built

LIBBASE=core
LIBNAME=$(DISTDIR)/lib$(LIBBASE).$(CND_DLIB_EXT)

#----------------------------------------------------------------------
# SETTINGS FOR THE COMPILATION OF THE CORE
# Object Directory
OBJECTDIR=${BASEDIR}/INCA/Core/${CND_BUILDDIR}/${CND_CONF}/${CND_PLATFORM}
DISTDIR=${BASEDIR}/INCA/Core/${CND_DISTDIR}/${CND_CONF}/${CND_PLATFORM}
#Object files
OBJECTFILES= \
	ContainerAccessWrapperBase.o \
	Dascru.o \
	DataGroup.o \
	DataSet.o \
	Equation.o \
	EquationCumulative.o \
	EquationInitialValue.o \
	EquationInverse.o \
	EquationOde.o \
	EquationPre.o \
	File.o \
	FormatInput.o \
	FormatOutput.o \
	IncaModel.o \
	IndexerObserverObject.o \
	IndexerReach.o \
	IndexerStream.o \
	Model.o \
	ModelObject.o \
	ObserverSubject.o \
	ParameterBase.o \
	ParameterGroup.o \
	ParameterSet.o \
	SolverBase.o \
	SolverClassicInca.o \
	Units.o

# CC Compiler Flags
CCFLAGS=-Wall -O3 -std=c++11

ifeq ($(CND_DLIB_EXT), so)
	CXXFLAGS=-fPIC -std=c++11 -O3
else ifeq ($(CND_DLIB_EXT), a)
	CXXFLAGS=-std=c++11 -O3
endif


#COMPILE
COMPILE=$(CXX) -c $(CXXFLAGS)

#Specifying the name of the library:
LIBSO=$(DISTDIR)/lib$(LIBNAME).so
LIBA=$(DISTDIR)/lib$(LIBNAME).a

vpath %.o $(OBJECTDIR)
vpath %.cpp $(INCASRC)

.PHONY: make_dir
all: make_dir $(OBJECTDIR)/sqlite.o lib

#Creating directory for object files
make_dir:
	$(MKDIR) -p $(OBJECTDIR)
	$(MKDIR) -p $(DISTDIR)

#Compiling listed object files
$(OBJECTFILES):
	$(COMPILE) -I${INCAINC} -I${INCASRC} -I${TINYXMLDIR} -I${SQLITEDIR} -I${BOOSTDIR} $(INCASRC)/$(subst .o,.cpp,$@) -o $(OBJECTDIR)/$@

#Adding compilation unit for sqlite3

$(OBJECTDIR)/sqlite.o: $(SQLITEDIR)/sqlite3.c
	gcc $(CXXFLAGS) -c $(SQLITEDIR)/sqlite3.c -o $@

lib: $(LIBNAME)


$(LIBNAME): $(OBJECTFILES) $(OBJECTDIR)/sqlite.o
	$(RM) -f $(LIBNAME)
ifeq ($(CND_DLIB_EXT), so)
	$(CC) $(CXXFLAGS) -shared -o $(LIBNAME)  $(patsubst %,$(OBJECTDIR)/%,$(OBJECTFILES)) $(OBJECTDIR)/sqlite.o
else ifeq ($(CND_DLIB_EXT), a)
	$(AR) -rv $(LIBNAME) $(patsubst %,$(OBJECTDIR)/%,$(OBJECTFILES)) $(OBJECTDIR)/sqlite.o
	$(RANLIB) $(LIBNAME)
endif

#Install and clean
PREFIX=/usr/local

.PHONY : install
install: $(LIBNAME)
	${MKDIR} -p ${PREFIX}/lib
	${CP} $(LIBNAME) ${PREFIX}/lib

.PHONY : clean
clean :
	${RM} -rf ${OBJECTDIR}
	${RM} -f ${DISTDIR}/$(LIBNAME)

