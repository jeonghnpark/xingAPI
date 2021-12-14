

class XASession:
    login_state=0


    def OnLogin(self, code, msg):
        if code=="0000":
            print(code, msg)
            XASession.login_state=1
        else:
            print(code, msg)


    def OnDisconnect(self):
        print("Session disconnected")
        XASession.login_state=0