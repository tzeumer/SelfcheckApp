"""These options allow to show a different value than the value.

Most of this file is copied from :class:`kivy.uix.settings.SettingOptions`.
"""
from kivy.properties import DictProperty, ObjectProperty
from kivy.uix.settings import Label, SettingItem, SettingTitle, SettingsWithSidebar
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import dp
from kivy.uix.button import Button

from kivy.logger import Logger

class AppSettings(SettingsWithSidebar):
    """
    It is not usually necessary to create subclass of a settings panel. There
    are many built-in types that you can use out of the box
    (SettingsWithSidebar, SettingsWithSpinner etc.).

    You would only want to create a Settings subclass like this if you want to
    change the behavior or appearance of an existing Settings class.
    """
    def __init__(self, *args, **kargs):
        super(AppSettings, self).__init__(*args, **kargs)
        self.register_type('info', SettingInfo)    
        self.register_type("optionmapping", SettingOptionMapping)

    def on_close(self):
        Logger.info("main.py: AppSettings.on_close")

    def on_config_change(self, config, section, key, value):
        Logger.info(
            "main.py: AppSettings.on_config_change: "
            "{0}, {1}, {2}, {3}".format(config, section, key, value))


class SettingInfo(SettingTitle):
    """ custom setting type 'info' (@see AppSettings())
    A block with some info text within a configuration screen
    @todo: Move the style definition somewhere else than C:\ProgrammePortable\_Development\WinPython-64bit-3.5.3.1Qt5\python-3.5.3.amd64\Lib\site-packages\kivy\data\style.kv
    """
    title = Label.text
    pass

class SettingOptionMapping(SettingItem):
    ''' http://pythonhosted.org/kniteditor/_modules/kniteditor/settings.html
    Implementation of an option list on top of a :class:`SettingItem`.
    It is visualized with a :class:`~kivy.uix.label.Label` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    list of options from which the user can select.
    '''

    options = DictProperty({})
    '''A mapping of key strings to value strings.
    The values are displayed to the user.
    The keys can be found in the value attribute.

    :attr:`options` is a :class:`~kivy.properties.DictProperty` and defaults
    to ``{}``.
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it is shown.

    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    def on_panel(self, instance, value):
        """The panel is set. Bind to open a popup when it is clicked."""
        if value is None:
            return
        self.fbind('on_release', self._create_popup)


    def _set_option(self, value):
        self.value = value
        self.popup.dismiss()

    def _create_popup(self, instance):
        # create the popup
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            content=content, title=self.title, size_hint=(None, None),
            size=(popup_width, '400dp'))
        popup.height = len(self.options) * dp(55) + dp(150)

        # add all the options
        content.add_widget(Widget(size_hint_y=None, height=1))
        uid = str(self.uid)
        for option, text in sorted(self.options.items(), key=lambda t: t[1]):
            state = 'down' if option == self.value else 'normal'
            btn = ToggleButton(text=text, state=state, group=uid)
            btn.bind(on_release=lambda instance,
                     option=option: self._set_option(option))
            content.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        content.add_widget(Widget())  # SettingSpacer
        btn = Button(text='Cancel', size_hint_y=None, height=dp(50))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)

        # and open the popup !
        popup.open()
