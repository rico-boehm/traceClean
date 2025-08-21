<pre>
<h1>Groundstation Software for REXUS project 'TRACER' of Space Team Aachen</h1>

This is the software package we use for our TRACER project. It is based on the Yamcs framework with our own packages and processors. For controlling we use Yamcs Studio with our self-designed GUI.

## Setup Tutorial

-To install simply clone the repo into a directory
-To start the Yamcs server, navigate to __C:\...\tracer_groundstation\yamcsServer__ in the command line and execute __mvn yamcs:run__
-If you get an error while building, on windows open the task manager, search 'java' and kill the __Java(TM) Platform SE binary__ task 
-The web interface of the server will be available at __localhost:8090__
-To start the script for serial communication navigate to __C:\...\tracer_groundstation\serialScript__ in a new command line window, write __python pcm.py__ and hit enter
-You may have to change the COM Port in __PCM.py__ (you can find the right COM Port in the Device Manager under __Ports (COM & LPT)__) to get it to work correctly
-After the script is started you should see two green links under the __Links__ tab in the web interface and the 'In' counter should tick up
-You can download the latest version of the Yamcs Studio software at __https://github.com/yamcs/yamcs-studio/releases/__
-Extract the zip file and open Yamcs Studio
-Navigate to __File__ -> __Open Projects from File System...__ and choose __C:\...\tracer_groundstation\gui__ as the path
-After importing the directory, dropdown the __tracer__ folder on the left side and open __data.opi__
-When the screen has loaded press on the green arrow button to open the GUI
-In the top bar select __Yamcs__->__Connect...__
-In the window that pops up enter __http://localhost:8090__ as the __Server URL__ and __tracer__ as the __Instance__ on the right side
-Click __Connect__ and if everything works correctly, you should now have a functioning GUI
</pre>

