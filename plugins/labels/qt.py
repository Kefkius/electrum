from functools import partial

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from electrum.plugins import hook
from electrum.i18n import _
from electrum_gui.qt import EnterButton
from electrum_gui.qt.util import ThreadedButton, Buttons, CancelButton
from electrum_gui.qt.util import WindowModalDialog, OkButton

from labels import LabelsPlugin


class Plugin(LabelsPlugin):

    def __init__(self, *args):
        LabelsPlugin.__init__(self, *args)
        self.obj = QObject()

    def requires_settings(self):
        return True

    def settings_widget(self, window):
        return EnterButton(_('Settings'),
                           partial(self.settings_dialog, window))

    def settings_dialog(self, window):
        wallet = window.parent().wallet
        d = WindowModalDialog(window, _("Label Settings"))
        vbox = QVBoxLayout(d)
        layout = QGridLayout()
        vbox.addLayout(layout)
        layout.addWidget(QLabel("Label sync options: "), 2, 0)
        self.upload = ThreadedButton("Force upload",
                                     partial(self.push_thread, wallet),
                                     self.done_processing)
        layout.addWidget(self.upload, 2, 1)
        self.download = ThreadedButton("Force download",
                                       partial(self.pull_thread, wallet, True),
                                       self.done_processing)
        layout.addWidget(self.download, 2, 2)
        self.accept = OkButton(d, _("Done"))
        vbox.addLayout(Buttons(CancelButton(d), self.accept))
        return bool(d.exec_())

    def on_pulled(self, wallet):
        self.obj.emit(SIGNAL('labels_changed'), wallet)

    def done_processing(self):
        QMessageBox.information(None, _("Labels synchronised"),
                                _("Your labels have been synchronised."))

    @hook
    def on_new_window(self, window):
        window.connect(window.app, SIGNAL('labels_changed'), window.update_tabs)
        self.start_wallet(window.wallet)

    @hook
    def on_close_window(self, window):
        self.stop_wallet(window.wallet)
