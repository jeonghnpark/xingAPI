import win32com.client
client=win32com.client.Dispatch("XA_Session.XASession")
client.ConnectServer("demo.ebestsec.co.kr", 20001)
# client.DisconnectServer()
