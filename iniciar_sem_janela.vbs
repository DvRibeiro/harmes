Set FSO = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")
currentDir = FSO.GetParentFolderName(WScript.ScriptFullName)

venvPythonw = currentDir & "\venv\Scripts\pythonw.exe"

If FSO.FileExists(venvPythonw) Then
    WshShell.Run """" & venvPythonw & """ main.py", 0, False
Else
    WshShell.Run "pythonw main.py", 0, False
End If
