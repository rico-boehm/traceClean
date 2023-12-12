Groundstation Software for TRACE Rexus project of Space Team Aachen

-To install simply clone the repo into a directory
-To start the Yamcs server, navigate to C:\...\Code\traceClean\yamcsServer in the command line and execute mvn yamcs:run
-If you get an error while building, on windows open the task manager, search 'java' and kill the task 
-The web interface of the server will be available at localhost:8090
-To start the script for serial communication navigate to C:\...\traceClean\serialScript in the command line and execute 'python pcm.py'
-You may have to change the COM Port in PCM.py (you can find the right COM Port in the Device Manager) to get it to work correctly
-After the script is started you should see two green links under the 'Links' tab in the web interface and the 'In' counter should tick up
-You can clone the latest version of the Yamcs Studio repo at https://github.com/yamcs/yamcs-studio.git
-Extract the zip file and open Yamcs Studio
-Navigate to 'File' -> 'Open Projects from File System...' and choose C:\...\traceClean\gui as the path
-After importing the directory, dropdown the trace folder on the left side and open data.opi
-When the screen has loaded press on the green arrow button to open the GUI
-If everything works correctly, you should now have a functioning GUI
