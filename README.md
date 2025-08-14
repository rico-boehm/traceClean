<pre>
<h1>Groundstation Software for TRACE Rexus project of Space Team Aachen</h1>

-To install simply clone the repo into a directory
-To start the Yamcs server, navigate to C:\...\traceClean\yamcsServer in the command line and execute mvn yamcs:run
-If you get an error while building, on windows open the task manager, search 'java' and kill the 'Java(TM) Platform SE binary' task 
-The web interface of the server will be available at localhost:8090
-To start the script for serial communication navigate to C:\...\traceClean\serialScript in a new command line window and execute 'python pcm.py'
-You may have to change the COM Port in PCM.py (you can find the right COM Port in the Device Manager under 'Ports (COM & LPT)') to get it to work correctly
-After the script is started you should see two green links under the 'Links' tab in the web interface and the 'In' counter should tick up
-You can download the latest version of the Yamcs Studio software at https://github.com/yamcs/yamcs-studio/releases/
-Extract the zip file and open Yamcs Studio
-Navigate to 'File' -> 'Open Projects from File System...' and choose C:\...\traceClean\gui as the path
-After importing the directory, dropdown the trace folder on the left side and open data.opi
-When the screen has loaded press on the green arrow button to open the GUI
-In the top bar select Yamcs->Connect...
-In the window that pops up enter http://localhost:8090 as the 'Server URL' and 'tracer' as the 'Instance' on the right side
-Click 'Connect' and if everything works correctly, you should now have a functioning GUI
</pre>

