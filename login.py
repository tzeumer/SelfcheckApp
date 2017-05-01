from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition

class Login(Screen):
    def do_login(self, loginText, passwordText):
        app = App.get_running_app()
        #myAction = 'connected'

        app.username = loginText
        app.password = passwordText

        self.manager.transition = SlideTransition(direction="left")

        # TOBI start
        # Test
        print (app.config.get('sip2Params', 'hostName'))
        print (app.config.getint('sip2Params', 'UIDalgorithm'))

        try:
            # Login with device and automatically do a self check
            wrapper.login_device(loginText, passwordText, True)
            #wrapper.login_device('2010', 'test16', True)
            myAction = 'connected'
        except Exception as ex:
            print(ex)
            myAction = 'error'
        # TOBI end

        self.manager.current = myAction

        app.config.read(app.get_application_config())
        app.config.write()

    def resetForm(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""