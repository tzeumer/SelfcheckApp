"""
interesting stuff

LANGUAGE
a) https://github.com/kivy/kivy/issues/1664
b1) http://blog.fossasia.org/awesome-kivy-revelations/
b2) https://github.com/tito/kivy-gettext-example
c) http://pythonhosted.org/flufl.i18n/
d) http://wiki.maemo.org/Internationalize_a_Python_application

READING FROM DEVICES
- http://python-evdev.readthedocs.io/en/latest/tutorial.html#reading-events
- https://github.com/AdamLaurie/RFIDIOt

- directories: https://kivy.org/docs/_modules/kivy/app.html
"""

# default kivy stuff
from kivy.app import App
#from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager

import os.path

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


class SelfcheckApp(App):
    # https://kivy.org/docs/api-kivy.app.html
    username = StringProperty(None)
    password = StringProperty(None)
    
    #use_kivy_settings = False

    def build(self):
        """ Initialize App
        @ notes: custom window title: self.title = 'Gossip Client'
        """
        #config = self.config
        #Config.set('graphics', 'width', '1000')
        #Config.set('graphics', 'height', '800')
        Window.size = (1200, 800)

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
    
    def on_start(self):
        """ Open settings panel if app is not set to autologin. A selfcheck app
        only makes sense in online mode (unless an offline mode is forced 
        because of connection errors).
        @todo Probably always switch to the autologin option
        """
        if (self.config.getint('myAppSettings', 'autologin') == 0):
            self.open_settings()



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
        @note:    Gossip internally waits 5 seconds for responses from the ILS.
                  Therefore a socketTimeout of 6 seconds is a very reasonable
                  maximum.
        @todo:    Same stuff is repeatedly written (here, in the json files,
                  in the sip2/sip2wrapper classes and in message_lookup.py...).
                  Maybe everything could be mapped to each other better.
        """
        config.setdefaults('sip2Params', {
            'hostName'          : 'xhar.gbv.de',
            'hostPort'          : 1294,
            'maxretry'          : 0,
            'socketTimeout'     : 6,
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
            'ils_pass'          : '',
            'logfile_path'      : os.path.join(os.getcwd(), 'logs'),
            'loglevel'          : 'WARNING'            
        })
        config.setdefaults('sip2Rules', {
            'require_password': 1,
            '0'  : 1, '1'  : 1, '2'  : 1, '3'  : 1, '4'  : 1, '5'  : 1,
            '6'  : 1, '7'  : 1, '8'  : 1, '9'  : 1, '10' : 1, '11' : 1,
            '12' : 1, '13' : 1, '14' : 1, '15' : 1,
            'OfflineOk': 1
        })
        config.setdefaults('sip2RulesGossip', {
            'commitReservation': 0,
            'thirdPartyRenewal': 0,
            'subtotalPayment': 0,
            'partialFeePayment': 0,
            'languageSwitch': 0,
            'alertReservation': 0,
            'provideItemProperties': 0,
        })
        config.setdefaults('myAppSettings', {
            'autologin'         : 0
        })

        config.setdefaults(LANGUAGE_SECTION, {
            LANGUAGE_CODE: current_language()
        })

    def build_settings(self, settings):
        #https://kivy.org/docs/api-kivy.uix.settings.html#settings-json
        settings.add_json_panel(_('SIP2 (Server)'), self.config, data=self.settings_panel_sip2_server)
        settings.add_json_panel(_('SIP2 (Device)'), self.config, data=self.settings_panel_sip2_device)
        settings.add_json_panel(_('SIP2 (Rules)'), self.config, data=self.settings_panel_sip2_rules)
        settings.add_json_panel(_('SIP2 (Gossip)'), self.config, data=self.settings_panel_sip2_gossip)
        settings.add_json_panel(_('MyApp'), self.config, data=self.settings_panel_app)
        settings.add_json_panel(_('Language'), self.config, data=self.settings_panel_language)

    def update_language_from_config(self):
        """Set the current language of the application from the configuration.
        """
        config_language = self.config.get(LANGUAGE_SECTION, LANGUAGE_CODE)
        change_language_to(config_language)

    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        Logger.info("main.py: App.on_config_change: {0}, {1}, {2}, {3}".format(
            config, section, key, value))

        if section == 'sip2Params':
            print ("How to do a Selfcheck.disconnect() from here???")
            #super(Selfcheck, self).disconnect()
            
        if section == "myAppSettings":
            if key == "autologin":
                if value == 1:
                    print ("How to do a Selfcheck.connect() from here - if not connected already???")

        if section == "My Label":
            if key == "text":
                self.root.ids.label.text = value
            elif key == 'font_size':
                self.root.ids.label.font_size = float(value)
        """
        Implementation for language as by knittingpattern
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

    @property
    def settings_panel_language(self):
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

    @property
    def settings_panel_sip2_server(self):
        """The settings specification as JSON string.

        :rtype: str
        :return: a JSON string
        """
        settings = [
            { "type": "title",
              "title": _("Version")
            },
        
            { "type": "options",
              "title": _("SIP2 Version"),
              "desc": _("SIP2 standard or Gossip?"),
              "section": "sip2Params",
              "key": "version",
              "options": ["Gossip", "Sip2"]
            },
        
            { "type": "title",
              "title": _("Connection Settings")
            },
        
            { "type": "string",
              "title": _("Host Name"),
              "desc": _("Sip2 server name. It MUST be a name if TLS is enabled. Otherwise an IP is ok, too."),
              "section": "sip2Params",
              "key": "hostName"
            },
        
            { "type": "numeric",
              "title": _("Host Port"),
              "desc": _("SIP2-Port"),
              "section": "sip2Params",
              "key": "hostPort"
            },
        
            { "type": "numeric",
              "title": _("Connection Timeout"),
              "desc": _("How many seconds until connection attempt will be aborted. Default 3 (if you set a higher value, it might automatically be reduced to the maximum the server supports)."),
              "section": "sip2Params",
              "key": "socketTimeout"
            },
        
            { "type": "bool",
              "title": _("TLS"),
              "desc": _("Use encrpyted connection"),
              "section": "sip2Params",
              "key": "tlsEnable"
            },
        
            { "type": "bool",
              "title": _("TLS - allow selfsigned"),
              "desc": _("If TLS is enabled, allow selfsigned certificate from server?"),
              "section": "sip2Params",
              "key": "tlsAcceptSelfsigned"
            },
        
            { "type": "string",
              "title": _("Encoding"),
              "desc": _("Which encoding does the server use"),
              "section": "sip2Params",
              "key": "hostEncoding"
            },
        
            { "type": "title",
              "title": _("Expert Setting (highly unlikely any adjustments are required)")
            },
        
            { "type": "numeric",
              "title": _("Maximum Retries For Sending SIP2-Message"),
              "desc": _("Maximum number of resends allowed before we give up. Note: this is pretty much a relict from pre tcp times"),
              "section": "sip2Params",
              "key": "maxretry"
            },
        
            { "type": "string",
              "title": _("Field terminator"),
              "desc": _("SIP2 field terminator"),
              "section": "sip2Params",
              "key": "fldTerminator"
            },
        
            { "type": "options",
              "title": _("Message terminator"),
              "desc": _("SIP2 message terminator"),
              "section": "sip2Params",
              "key": "msgTerminator",
              "options": ["\\r", "\\n", "\\r\\n"]
            },
        
            { "type": "bool",
              "title": _("Set CRC"),
              "desc": _("Toggle crc checking and appending for SIP2 messages."),
              "section": "sip2Params",
              "key": "withCrc"
            },
        
            { "type": "bool",
              "title": _("Set Sequence Numbers"),
              "desc": _("Toggle the use of sequence numbers"),
              "section": "sip2Params",
              "key": "withSeq"
            },
        
            { "type": "string",
              "title": _("Login Encryption Algorithm"),
              "desc": _("Login encryption algorithm type (0 = plain text)"),
              "section": "sip2Params",
              "key": "UIDalgorithm"
            },
        
            { "type": "string",
              "title": _("Password Encryption Algorithm"),
              "desc": _("Password encryption algorithm type (undocumented)"),
              "section": "sip2Params",
              "key": "PWDalgorithm"
            }
        ]
        return json.dumps(settings)

    @property
    def settings_panel_sip2_device(self):
        """The settings specification as JSON string.

        :rtype: str
        :return: a JSON string
        """
        settings = [
            { "type": "title",
              "title": _("Credentials")
            },
        
            { "type": "string",
              "title": _("Login Name"),
              "desc": _("Library system user"),
              "section": "sip2Params",
              "key": "ils_user"
            },
        
            { "type": "string",
              "title": _("Login Password"),
              "desc": _("Library system user password"),
              "section": "sip2Params",
              "key": "ils_pass"
            },
        
            { "type": "title",
              "title": _("Self Check Device (cosmetic settings)")
            },
        
            { "type": "string",
              "title": _("Language"),
              "desc": _("Which is the default language to request from SIP2 Server (and this device)? TODO: USE CODES"),
              "section": "sip2Params",
              "key": "language"
            },
        
            { "type": "string",
              "title": _("Institution Name"),
              "desc": _("The name of your institution"),
              "section": "sip2Params",
              "key": "institutionId"
            },
        
            { "type": "string",
              "title": _("Device Name"),
              "desc": _("The name of this selfcheck device (or its location)"),
              "section": "sip2Params",
              "key": "scLocation"
            },
        
            { "type": "string",
              "title": _("Terminal Password"),
              "desc": _("Pretty unlikely you have to set anything here..."),
              "section": "sip2Params",
              "key": "terminalPassword"
            },
                    
             { "type": "options",
              "title": _("Loglevel"),
              "desc": _("How much to log"),
              "section": "sip2Params",
              "key": "loglevel",
              "options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            },

            { "type": "string",
              "title": _("Logfile"),
              "desc": _("Folder where to save the logfile in"),
              "section": "sip2Params",
              "key": "logfile_path"
            }
        ]
        return json.dumps(settings)

    @property
    def settings_panel_sip2_rules(self):
        """The settings specification as JSON string.

        :rtype: str
        :return: a JSON string
        """
        settings = [
            { "type": "title",
              "title": _("SIP2 Supported Actions (Override possible)")
            },
        
            { "type": "info",
              "title": _("Settings are fetched when the connection to the server is established. You can disable settings, that the server supports (basically and policy) but that you don't want to use. But not vice versa (enable something the server does not support).")
            },
            
            { "type": "bool",
              "title": _("Require Patron Password"),
              "desc": _("If disabled patrons can login without a password, using only their patron id"),
              "section": "sip2Rules",
              "key": "require_password"
            },

            { "type": "bool",
              "title": _("Checkout"),
              "desc": _("Device can checkout items"),
              "section": "sip2Rules",
              "key": "1"
            },
        
            { "type": "bool",
              "title": _("Checkin"),
              "desc": _("Device can checkin items"),
              "section": "sip2Rules",
              "key": "2"
            },
          
            { "type": "bool",
              "title": _("Fee Paid"),
              "desc": _("Fees can be paid on the device, server supports it."),
              "section": "sip2Rules",
              "key": "9"
            },
        
            { "type": "bool",
              "title": _("Renew"),
              "desc": _("Device can renew an single item."),
              "section": "sip2Rules",
              "key": "14"
            },
        
            { "type": "bool",
              "title": _("Renew All"),
              "desc": _("Device can renew all items."),
              "section": "sip2Rules",
              "key": "15"
            },
          
            { "type": "title",
              "title": _("SIP2 Supported Actions (autoconfigured)")
            },
        
            { "type": "info",
              "title": _("These settings cannot be changed, they are fetched from the server. Some settings must be supported by the server, otherwise this (or any) app wouldn't make much sense. Other settings, like Block Patron, are too outlandish to be supported in this app.")
            },
            
            { "type": "bool",
              "title": _("Patron Status Request"),
              "desc": _("Device can request patron status"),
              "section": "sip2Rules",
              "key": "0",
              "disabled": 1
            },
        
            { "type": "bool",
              "title": _("SC/ACS Status"),
              "desc": _("Device can request settings for all these rules. If not, this app will not work."),
              "section": "sip2Rules",
              "key": "4",
              "disabled": 1
            },
        
            { "type": "bool",
              "title": _("Request SC/ACS Resend"),
              "desc": _("Device can requests from servver to re-transmit its last message if the checksum in a received message does not match the value calculated"),
              "section": "sip2Rules",
              "key": "5",
              "disabled": 1
            },
        
            { "type": "bool",
              "title": _("Login"),
              "desc": _("Allow login to server (\"Whether to use this message or to use some other mechanism to login to the ACS is configurable on the SC.\")"),
              "section": "sip2Rules",
              "key": "6",
              "disabled": 1
            },
        
            { "type": "bool",
              "title": _("Patron Information"),
              "desc": _("This message is a superset of the Patron Status Request."),
              "section": "sip2Rules",
              "key": "7",
              "disabled": 1
            },
        
            { "type": "bool",
              "title": _("End Patron Session"),
              "desc": _("Device can send command to end patron session to server."),
              "section": "sip2Rules",
              "key": "8",
              "disabled": 1
            },
        
            { "type": "bool",
              "title": _("Item Information"),
              "desc": _("Device can request item information."),
              "section": "sip2Rules",
              "key": "10",
              "disabled": 1
            },
            
            { "type": "bool",
              "title": _("Item Status Update"),
              "desc": _("Device can update item status without a checkin or checkout action."),
              "section": "sip2Rules",
              "key": "11",
              "disabled": 1
            },
        
            { "type": "bool",
              "title": _("Hold"),
              "desc": _("Device can create, modify, or delete a hold."),
              "section": "sip2Rules",
              "key": "13",
              "disabled": 1
            },
            
            { "type": "title",
              "title": _("SIP2 Supported Actions (autoconfigured special note)")
            },
        
            { "type": "info",
              "title": _("These three settings are real good candidates to circumvent the main problem of offline checkouts (network outage): a blocked user might borrow something. Were this settings available such a patron could be temporarily unblocked to process this checkout anyway when the connection is available again. Unfortunatley this app can't implement such a mechanism, because no available server supports this.")
            },
        
            { "type": "bool",
              "title": _("Offline ok"),
              "desc": _("ILS and SIP2 server support the off-line operation feature. The ILS must also support no block charge requests when it comes back on-line."),
              "section": "sip2Rules",
              "key": "OfflineOk",
              "disabled": 1
            },
        
            { "type": "bool",
              "title": _("Block Patron"),
              "desc": _("Device can block patron account"),
              "section": "sip2Rules",
              "key": "3",
              "disabled": 1
            },
        
            { "type": "bool",
              "title": _("Patron Enable"),
              "desc": _("Device can unblock a patron."),
              "section": "sip2Rules",
              "key": "12",
              "disabled": 1
            }
        ]
        return json.dumps(settings)

    @property
    def settings_panel_sip2_gossip(self):
        """The settings specification as JSON string.

        :rtype: str
        :return: a JSON string
        """
        settings = [
            { "type": "title",
              "title": _("Gossip Supported Actions")
            },
        
            { "type": "info",
              "title": _("These settings are not part of the SIP2 protocol definition. Thus they are not transmitted via a ACS Status Response (98). If you use Gossip, you have to check yourself, what policies are set.")
            },
             
            { "type": "bool",
              "title": _("[NOT IMPLEMENTED] Commit Reservation"),
              "desc": _("Shall reserved items be commited when returned (this usually will inform the next patron immedialtely that his reservation is available). May automatically be set to false if returning of items is not allowed."),
              "section": "sip2RulesGossip",
              "key": "commitReservation"
            },
        
            { "type": "bool",
              "title": _("[NOT IMPLEMENTED] Allow Third Party Renewal"),
              "desc": _("Allow anyone to renew an item, even if it is not held by the current logged in user (don't ask me, what's the point). May automatically be set to false if renewing isn't allowed at all."),
              "section": "sip2RulesGossip",
              "key": "thirdPartyRenewal"
            },
        
            { "type": "bool",
              "title": _("[NOT IMPLEMENTED] Allow Subtotal Payment"),
              "desc": _("Is paying only some fee entries allowed?"),
              "section": "sip2RulesGossip",
              "key": "subtotalPayment"
            },
        
            { "type": "bool",
              "title": _("[NOT IMPLEMENTED] Allow Partial Fee Payment"),
              "desc": _("May even just a part of a fee entry be paid?"),
              "section": "sip2RulesGossip",
              "key": "partialFeePayment"
            },
        
            { "type": "bool",
              "title": _("[NOT IMPLEMENTED] Use additional languages"),
              "desc": _("The default language is set in the SIP2 (Server) part. Is Gossip set to switch to a different language upon request?"),
              "section": "sip2RulesGossip",
              "key": "languageSwitch"
            },
        
            { "type": "bool",
              "title": _("[NOT IMPLEMENTED] Special message for returned reservations"),
              "desc": _("If set to true in Gossip, a custom message is shown when a reserved item is returned."),
              "section": "sip2RulesGossip",
              "key": "alertReservation"
            },
        
            { "type": "bool",
              "title": _("[NOT IMPLEMENTED] Server Provides Special Item Properties"),
              "desc": _("Gossip return addional item information (if currently checked out). Not used in this app."),
              "section": "sip2RulesGossip",
              "key": "provideItemProperties"
            }         
        ]
        return json.dumps(settings)
    
    @property
    def settings_panel_app(self):
        """The settings specification as JSON string.

        :rtype: str
        :return: a JSON string
        """
        
        """
        library.lms.EndPatronSession.enabled
        circulation.task.borrow.allowReservedItems
        circulation.task.borrow.auto
        circulation.account.load.auto
        """

        settings = [
            { "type": "title",
              "title": _("This App") 
            },
        
            { "type": "bool",
              "title": _("Autologin (Mandatory)"),
              "desc": _("Autologin when app starts. When app is configured, this option must always be turned on for productive use (no point using this app offline. The app will throw you into the config screen on start, until it is turned on."),
              "section": "myAppSettings",
              "key": "autologin"
            }        
        ]
        return json.dumps(settings)
    

if __name__ == '__main__':
    SelfcheckApp().run()
