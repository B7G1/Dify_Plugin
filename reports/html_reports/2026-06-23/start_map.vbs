Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d ""E:\Dify_Plugin\db_query_extended_interactive_map\db_query_extended_interactive_map"" && E:\python.exe -m http.server 8088", 0, False
WScript.Sleep 2000
WshShell.Run "http://localhost:8088"