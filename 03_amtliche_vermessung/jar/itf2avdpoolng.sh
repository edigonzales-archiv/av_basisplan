#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/java-6-oracle/
echo "Java Home is $JAVA_HOME"

export CLASSPATH=:/home/stefan/Projekte/av_basisplan/03_amtliche_vermessung/jar/itf2avdpoolng.jar:$CLASSPATH
echo "CLASSPATH is $CLASSPATH"

$JAVA_HOME/bin/java -Xms128m -Xmx2048m org.catais.Basisplan /home/stefan/Projekte/av_basisplan/03_amtliche_vermessung/jar/itf2avdpoolng.properties


