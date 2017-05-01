"""
interesting stuff

LANGUAGE
a) https://github.com/kivy/kivy/issues/1664
b1) http://blog.fossasia.org/awesome-kivy-revelations/
b2) https://github.com/tito/kivy-gettext-example
c) http://pythonhosted.org/flufl.i18n/
d) http://wiki.maemo.org/Internationalize_a_Python_application

- directories: https://kivy.org/docs/_modules/kivy/app.html
"""

# default kivy stuff
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.logger import Logger
from kivy.lang import Builder
import sys
import os, os.path

# My custom kivy stuff (screens)
from connected import Connected, Error
from login import Login
from selfcheck import Selfcheck

# My custom kivy stuff: settings; required for new objectproperty SettingOptionMapping
from settings import AppSettings

# language
import json
from localization import _, list_languages, change_language_to, \
    current_language, language_code_to_translation

LANGUAGE_CODE = "current"  #: the language code name
LANGUAGE_SECTION = "language"  #: the language section name



"""
# Gossip
import importlib.util
spec = importlib.util.spec_from_file_location("module.name", os.path.join(os.getcwd(), "lib_later", "sip2", "sip2.py")
foo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foo)
foo.MyClass()

my_module_file = os.path.join(os.getcwd(), "lib_later", "sip2")
sys.path.append(my_module_file)
print (my_module_file)
import sip2.Sip2
import wrapper
"""

# This JSON defines entries we want to appear in our App configuration screen
# Inline example
json_app = '''
[
    { "type": "title",
      "title": "This App" },

      { "type": "bool",
      "title": "Autologin",
      "desc": "Autologin when app starts?",
      "section": "myAppSettings",
      "key": "autologin"
    }
]
'''

"""
library.lms.EndPatronSession.enabled
reader.session.checkoutallowed.check
circulation.task.borrow.allowReservedItems
circulation.task.borrow.auto
circulation.task.return.enabled
circulation.account.load.auto
"""

class SelfcheckApp(App):
    # https://kivy.org/docs/api-kivy.app.html
    username = StringProperty(None)
    password = StringProperty(None)

    def build(self):
        """ Initialize App
        @ notes: custom window title: self.title = 'Gossip Client'
        """
        config = self.config
        
        # Load custom style (for info section)
        Builder.load_file('style-override.kv') 

        # The line below is optional. You could leave it out or use one of the
        # standard options, such as SettingsWithSidebar, SettingsWithSpinner
        # etc.
        self.settings_cls = AppSettings
        self.update_language_from_config()
     
        manager = ScreenManager()
        manager.add_widget(Selfcheck(name='selfcheck'))
        manager.add_widget(Login(name='login'))
        manager.add_widget(Connected(name='connected'))
        manager.add_widget(Error(name='error'))

        return manager
        
    def get_application_config(self):
        """ Get location of configuration file(s)
        @todo Do it as intended
        """
        # https://kivy.org/docs/api-kivy.app.html#kivy.app.App.get_application_config
        if(not self.username):
            return super(SelfcheckApp, self).get_application_config()

        conf_directory = self.user_data_dir + '/' + self.username

        if(not os.path.exists(conf_directory)):
            os.makedirs(conf_directory)

        return super(SelfcheckApp, self).get_application_config(
            #'%s/config.cfg' % (conf_directory)
            '%(appdir)s/%(appname)s.ini' % (conf_directory)
        )

    def build_config(self, config):
        """ Set default configuration values
        @note:    settings.add_json_panel only accepts 1/0 for boolean, not 
                  True/False. These setting are really boolean for 
                  config.setdefaults: tlsEnable, tlsAcceptSelfsigned, withCrc, 
                  withSeq; autologin
        @todo:    Same stuff is repeatedly written (here, in the json files,
                  in the sip2/sip2wrapper classes and in message_lookup.py...).
                  Maybe everything could be mapped to each other better. 
        """
        config.setdefaults('sip2Params', {
            'hostName'          : 'xhar.gbv.de',
            'hostPort'          : 1294,
            'maxretry'          : 0,
            'socketTimeout'     : 3,
            'tlsEnable'         : 1,
            'tlsAcceptSelfsigned' : 1,
            'hostEncoding'      : 'utf-8', 
            'fldTerminator'     : '|',
            'msgTerminator'     : "\\r",
            'withCrc'           : 1,
            'withSeq'           : 1,
            'UIDalgorithm'      : 0,
            'PWDalgorithm'      : 0,
            'language'          : '000',
            'institutionId'     : 'My Test Institute',
            'terminalPassword'  : '',
            'scLocation'        : 'My Test SC Location',
#            'patron'           : '12345',
#            'patronpwd'        : 'secret',
            'version'           : 'Gossip',
            'ils_user'          : '',
            'ils_pass'          : ''
        })
        config.setdefaults('sip2Rules', {
            '0'  : 1, '1'  : 1, '2'  : 1, '3'  : 1, '4'  : 1, '5'  : 1, 
            '6'  : 1, '7'  : 1, '8'  : 1, '9'  : 1, '10' : 1, '11' : 1,
            '12' : 1, '13' : 1, '14' : 1, '15' : 1,
            'OfflineOk': 1
        })
        config.setdefaults('myAppSettings', {
            'autologin'         : 0
        })
        
        config.setdefaults(LANGUAGE_SECTION, {
            LANGUAGE_CODE: current_language()
        })

    def build_settings(self, settings):
        settings.add_json_panel('SIP2 (Server)', self.config, os.path.join(self.directory, 'config', 'settings.sip2_server.json'))
        settings.add_json_panel('SIP2 (Device)', self.config, os.path.join(self.directory, 'config', 'settings.sip2_device.json'))
        settings.add_json_panel('SIP2 (Rules)', self.config, os.path.join(self.directory, 'config', 'settings.sip2_rules.json'))
        settings.add_json_panel('MyApp', self.config, data=json_app)
        settings.add_json_panel(_('Language'), self.config, data=self.settings_specification)

    def update_language_from_config(self):
        """Set the current language of the application from the configuration.
        """
        config_language = self.config.get(LANGUAGE_SECTION, LANGUAGE_CODE)
        change_language_to(config_language)

    @property
    def settings_specification(self):
        """The settings specification as JSON string.

        :rtype: str
        :return: a JSON string
        """
        settings = [
            {"type": "optionmapping",
             "title": _("Language"),
             "desc": _("Choose your language"),
             "section": LANGUAGE_SECTION,
             "key": LANGUAGE_CODE,
             "options": {code: language_code_to_translation(code)
                         for code in list_languages()}}
        ]
        return json.dumps(settings)
        
    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        Logger.info("main.py: App.on_config_change: {0}, {1}, {2}, {3}".format(
            config, section, key, value))
        
        if section == 'sip2Params':
            print ("How to do a Selfcheck.disconnect() from here???")
            #super(Selfcheck, self).disconnect()

        if section == "My Label":
            if key == "text":
                self.root.ids.label.text = value
            elif key == 'font_size':
                self.root.ids.label.font_size = float(value)
        """
        Impementation for language as by knittingpattern
        When this method is called, it issued calls to change methods if they
        exist in this order:

        - ``config_change_in_section_{section}_key_{key}(value)``
        - ``config_change_in_section_{section}(key, value)``
        """
        section_call = "config_change_in_section_{}".format(section)
        key_call = "{}_key_{}".format(section_call, key)
        if hasattr(self, key_call):
            getattr(self, key_call)(value)
        elif hasattr(self, section_call):
            getattr(self, section_call)(key, value)

    def config_change_in_section_language_key_current(self, new_language):
        """Set the new language of the application.

        Same as :func:`kniteditor.localization.change_language_to`
        """
        change_language_to(new_language)
        #tobi: Reload (close, destroy settings cache to reload language, open again)
        self.close_settings()
        self.destroy_settings()
        self.open_settings()

    def close_settings(self, settings=None):
        """
        The settings panel has been closed.
        """
        Logger.info("main.py: App.close_settings: {0}".format(settings))
        super(SelfcheckApp, self).close_settings(settings)
      
if __name__ == '__main__':       
    SelfcheckApp().run()