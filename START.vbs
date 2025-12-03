Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get script directory
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Start backend in hidden window
backendCmd = "python """ & scriptDir & "\backend\api_server.py"""
WshShell.Run backendCmd, 0, False

' Wait 3 seconds for backend to start
WScript.Sleep 3000

' Start frontend in hidden window  
WshShell.CurrentDirectory = scriptDir
frontendCmd = "cmd /c npm run dev"
WshShell.Run frontendCmd, 0, False

' Wait 5 seconds for frontend to start
WScript.Sleep 5000

' Open browser
WshShell.Run "http://localhost:8080", 1, False

' Show success message
MsgBox "✅ AI Video Generator Started!" & vbCrLf & vbCrLf & _
       "Frontend: http://localhost:8080" & vbCrLf & _
       "Backend: http://localhost:5000" & vbCrLf & vbCrLf & _
       "Services are running in the background." & vbCrLf & _
       "Check Task Manager to stop them.", 64, "AI Video Generator"
