# Groundstation Software for REXUS project 'TRACER' of Space Team Aachen

This is the software package we use for our TRACER project. It is based on the Yamcs framework with our own packages and processors. For controlling we use Yamcs Studio with our self-designed GUI.

## Setup Tutorial

-To install simply clone the repo into a directory   
-To start the Yamcs server, navigate to <b>C:\...\tracer_groundstation\yamcsServer</b> in the command line and execute <b>'mvn yamcs:run'</b>   
-If you get an error while building, on windows open the task manager, search 'java' and kill the <b>'Java(TM) Platform SE binary'</b> task   
-The web interface of the server will be available at <b>http://localhost:8090</b>   
-To start the script for serial communication navigate to <b>C:\...\tracer_groundstation\serialScript</b> in a new command line window, write <b>python pcm.py</b> and hit enter   
-You may have to change the COM Port in <b>'PCM.py'</b> (you can find the right COM Port in the Device Manager under <b>'Ports (COM & LPT)'</b>) to get it to work correctly   
-After the script is started you should see two green links under the <b>'Links'</b> tab in the web interface and the <b>'In'</b> counter should tick up   
-You can download the latest version of the Yamcs Studio software [here](https://github.com/yamcs/yamcs-studio/releases/)   
-Extract the zip file and open Yamcs Studio   
-Navigate to <b>'File'</b> -> <b>'Open Projects from File System...'</b> and choose <b>C:\...\tracer_groundstation\gui</b> as the path   
-After importing the directory, dropdown the <b>'tracer'</b> folder on the left side and open <b>'data.opi'</b>   
-When the screen has loaded press on the green arrow button to open the GUI   
-In the top bar select <b>'Yamcs'</b>-><b>'Connect...'</b>   
-In the window that pops up enter <b>http://localhost:8090</b> as the <b>'Server URL'</b> and <b>'tracer'</b> as the <b>'Instance'</b> on the right side   
-Click <b>'Connect'</b> and if everything works correctly, you should now have a functioning GUI

