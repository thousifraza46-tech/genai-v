' VBScript to run Python backend server in background (no window)
' This keeps the server running even if you close terminals

Set WshShell = CreateObject("WScript.Shell")

' Change to backend directory and run the server
WshShell.CurrentDirectory = "C:\Gen\backend"

' Run Python server in background (no window, independent process)
WshShell.Run "python stable_server.py", 0, False

' Show notification that server started
MsgBox "Backend server started in background!" & vbCrLf & vbCrLf & _
       "URL: http://localhost:5000" & vbCrLf & _
       "The server is now running invisibly." & vbCrLf & vbCrLf & _
       "To stop: Run STOP_BACKEND.bat", vbInformation, "Backend Server"

Set WshShell = Nothing

' Open the test_connection.html file in the default web browser
Dim objShell
Set objShell = CreateObject("Shell.Application")
objShell.Open "file:///C:/Gen/test_connection.html"
Set objShell = Nothing
