from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout

from localization import _

# Gossip
import os
from pprint import pprint
#import sys
#sys.path.append(os.getcwd())
#from lib_later.sip2.wrapper import Sip2Wrapper
from sip2.wrapper import Sip2Wrapper

class Selfcheck(Screen):

    def __init__(self, **kwargs):
        super(Selfcheck, self).__init__(**kwargs)
        self.app = App.get_running_app()

        self.ids.sip2_btn_autologin.active = self.app.config.getint('myAppSettings', 'autologin')

        if (self.app.config.getint('myAppSettings', 'autologin') == 1):
            self.connect()
        
    def connect(self):
        """
        Should be a better way like 
            self.sip2Params = dict(app.config._sections['sip2Params'])
            from pprint import pprint
            pprint (self.sip2Params)
            # for key,value in dict(app.config._sections['sip2Params'].items()):
                # print ("'%s' with value '%s'" % (key, value))
        """
        
        """
        Hmpf, does NOT WORK too
        # In combination with kivy configs I don't know a better way; this is
        # probably really bad...
        def unescape(terminated_str):
            return {
                '\\r': "\r",
                '\\n': "\n",
                '\\r\\n': "\r\n",
            }.get(terminated_str, "\r")
        terminator_unescaped = unescape(self.app.config.get('sip2Params', 'msgTerminator'))
        """

        sip2Params = {
            'hostName'       : self.app.config.get('sip2Params', 'hostName'),
            'hostPort'       : self.app.config.getint('sip2Params', 'hostPort'),
            'maxretry'       : self.app.config.getint('sip2Params', 'maxretry'),
            'socketTimeout'  : self.app.config.getint('sip2Params', 'socket_timeout'),
            'tlsEnable'      : self.app.config.getint('sip2Params', 'tlsEnable'),
            'tlsAcceptSelfsigned' : self.app.config.getint('sip2Params', 'tlsAcceptSelfsigned'),
            'hostEncoding'   : self.app.config.get('sip2Params', 'hostEncoding'),
            'fldTerminator'  : self.app.config.get('sip2Params', 'fldTerminator'),
            #'msgTerminator'  : terminator_unescaped,
            'withCrc'        : self.app.config.getint('sip2Params', 'withCrc'),
            'withSeq'        : self.app.config.getint('sip2Params', 'withSeq'),
            'UIDalgorithm'   : self.app.config.getint('sip2Params', 'UIDalgorithm'),
            'PWDalgorithm'   : self.app.config.getint('sip2Params', 'PWDalgorithm'),
            'language'       : self.app.config.get('sip2Params', 'language'),
            'institutionId'  : self.app.config.get('sip2Params', 'institutionId'),
            'terminalPassword': self.app.config.get('sip2Params', 'terminalPassword'),
            'scLocation'     : self.app.config.get('sip2Params', 'scLocation')
            #'patron'         : '12345',
            #'patronpwd'      : 'secret',
        }    
        
        # Create instance, but don't connect yet
        # @todo: if config changed, we probably need a new instance (or even 
        #        better, map config values to sip2 properties)
        if not hasattr(self, 'wrapper'):
            self.wrapper = Sip2Wrapper(sip2Params, False, self.app.config.get('sip2Params', 'version'))
        
        # Now connect
        try:
            self.wrapper.connect()
            # green indicator: self.ids.balbalb 
            #pprint (self.wrapper.return_sc_status())
        except Exception as ex:
            print(ex)
            print(_("Connection failed. Please check log and config"))
            myAction = 'error'
            return False
        except SystemExit as ex:
            # Real connection problem - set pretty (too?) hard with sys.exit in sip2 class
            print(ex)        
            self.ids.scr_selfcheck_left.text = _("Cannot connect to server")
            return False
        
        # Now Login
        try:
            self.wrapper.login_device(self.app.config.get('sip2Params', 'ils_user'), self.app.config.get('sip2Params', 'ils_pass'))
            print (self.wrapper.return_log())
        except Exception as ex:
            print(ex)
            print(_("Login failed. Please check config"))
            return False

        # Get possible commands
        # @todo: make _command_available public or add get method in Sip2;
        #        also refactor logging ("Server does not support command ...") 
        #        for such checks
        # @note: convert to int because configuration does not accept True/False
        # @note: the _supported_ commands may be disabled by policy; check below
        for msg_id in range(0, 15):
            # Don't turn something user override option on if set to off
            can_override = [1,2,9,14,15]
            msg_val = int(self.wrapper._command_available(msg_id))
            if self.app.config.get('sip2Rules', str(msg_id)) == 1 and msg_id in can_override:
                self.app.config.set('sip2Rules', str(msg_id), msg_val)
            else:
                self.app.config.set('sip2Rules', str(msg_id), msg_val)
                
        # Apply SIP2 policies (that may be more restrictive than what's supported)
        if (self.wrapper.return_sc_status()['fixed']['AcsRenewalPolicy'] == 'N'):
            self.app.config.set('sip2Rules', '14', 0)
            self.app.config.set('sip2Rules', '15', 0)
        if (self.wrapper.return_sc_status()['fixed']['CheckinOk'] == 'N'):
            self.app.config.set('sip2Rules', '2', 0)
        if (self.wrapper.return_sc_status()['fixed']['CheckoutOk'] == 'N'):
            self.app.config.set('sip2Rules', '1', 0)
        if (self.wrapper.return_sc_status()['fixed']['StatusUpdateOk'] == 'N'):
            self.app.config.set('sip2Rules', '3', 0)
            self.app.config.set('sip2Rules', '12', 0)
        if (self.wrapper.return_sc_status()['fixed']['OfflineOk'] == 'N'):
            self.app.config.set('sip2Rules', 'OfflineOk', 0)
        #if (self.app.config.get('sip2Params', 'socketTimeout') > int(self.wrapper._scStatus['fixed']['TimeoutPeriod'])):
        #    self.app.config.set('sip2Params', 'socketTimeout', int(self.wrapper._scStatus['fixed']['TimeoutPeriod']))
        if (int(self.app.config.get('sip2Params', 'maxretry')) > int(self.wrapper.return_sc_status()['fixed']['RetriesAllowed'])):
            self.app.config.set('sip2Params', 'maxretry', int(self.wrapper.return_sc_status()['fixed']['RetriesAllowed']))
        

        # Adjust special Gossip policies. Disable what logically cannot be true.
        # int() feels more true than '0'... hmm
        current_version = self.app.config.get('sip2Params', 'version')
        if (current_version != 'Gossip' or self.app.config.getint('sip2Rules', '2') == 0):
            # No isn't exactly right, but keep in mind, that these settings are only Gossip specific. No means it is disabled.
            self.app.config.set('sip2RulesGossip', 'commitReservation', 0)
            # @note immer vorm ausleihen checken, ob reserviert (wie Bibliotheca) 
            self.app.config.set('sip2RulesGossip', 'alertReservation', 0)
        if (current_version != 'Gossip' or self.app.config.getint('sip2Rules', '14') == 0 or self.app.config.getint('sip2Rules', '15') == 0):
            self.app.config.set('sip2RulesGossip', 'thirdPartyRenewal', 0)
        if (current_version != 'Gossip' or self.app.config.getint('sip2Rules', '9') == 0):
            self.app.config.set('sip2RulesGossip', 'subtotalPayment', 0)
            self.app.config.set('sip2RulesGossip', 'partialFeePayment', 0)
        if (current_version != 'Gossip'):
            self.app.config.set('sip2RulesGossip', 'languageSwitch', 0)
        if (current_version != 'Gossip' or self.app.config.getint('sip2Rules', '10') == 0):
            self.app.config.set('sip2RulesGossip', 'provideItemProperties', 0)

        pprint (self.wrapper._scStatus)
            
        # save the config, otherwise it will be reset to defaults on next app start
        self.app.config.write()  
        # Destroy setting, so the new settings are actually shown (before an app restart)
        # Might result in ignored exception on app exit (if config is not opened before again)...
        self.app.destroy_settings()
        
        # Got all the way down here? Return True
        return True

    def disconnect(self):
        self.wrapper.disconnect()
        print (self.wrapper._connected)
        print (self.wrapper.return_log())
        # red indicator: self.ids.balbalb

    def btn_get_item_information(self):
        try:
            blub = self.wrapper.sip_item_information('830$28479309')
            pprint (blub)
        except Exception as ex:
            print(self.wrapper.return_log())
                
    def status_toggle_btn(self, btn, id):
        """
        Curently only used for connect/disconnect togglebutton, but might useful
        for more buttons
        """
        if id == 'tgl_btn_connection' and btn.state == 'down':
            #self.ids.tgl_btn_connection.text = 'Disconnect' if self.connect() else 'Connect'
            status = self.connect()
            self.ids.tgl_btn_connection.text = _('Disconnect') if status == True else _('Connect')
            if status == False:
                btn.state = 'normal'
        elif id == 'tgl_btn_connection' and btn.state == 'normal':
            self.disconnect()
            self.ids.tgl_btn_connection.text = _('Connect')
            
        #print('button state is: {state}'.format(state=btn.state))
        #print('text input text is: {txt}'.format(txt=self.ids.tgl_btn_connection.text))
        

class xxx(Screen):
    def goLogin(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'login'
        self.manager.get_screen('login').resetForm()
