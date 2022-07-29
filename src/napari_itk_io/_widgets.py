import napari.viewer
from qtpy.QtWidgets import QWidget, QDialog, QFormLayout, QVBoxLayout, QPushButton, QLineEdit, QCheckBox, QDialogButtonBox, QLabel, QComboBox

from ._config import _settings, _ini

__all__ = ['ITK_IO_SettingsManager', 'CopyMetaDialog']


class OptionLE(QLineEdit):
    def __init__(self, *args, text=None, **kwargs):
        super().__init__(*args, **kwargs)
        if text:
            self.setText(text)

    def __repr__(self):
        return self.text()


class OptionCB(QCheckBox):
    def __init__(self, *args, state='False', **kwargs):
        super().__init__(*args, **kwargs)
        if state == 'True':
            self.setChecked(True)
        self.setText('')

    def __repr__(self):
        return str(self.isChecked())


class ITK_IO_SettingsManager(QWidget):
    def __init__(self):
        super().__init__()
        self._ini = _ini
        self._settings = _settings
        self._init_ui()

    def _init_ui(self):
        reset = QPushButton('Reset')
        reset.clicked.connect(self.reset_to_default)

        self.layout = QFormLayout()
        for option, value in self._settings['CURRENT'].items():
            if value == 'True' or value == 'False':
                exec(
                    f'self.{option} = OptionCB(state=value)\n'
                    f'self.{option}.stateChanged.connect(self.settings_changed)'
                )
            else:
                exec(
                    f'self.{option} = OptionLE(text=value)\n'
                    f'self.{option}.textChanged.connect(self.settings_changed)'
                )
            exec(f'self.layout.addRow("{option}:", self.{option})')
        self.layout.addWidget(reset)
        self.setLayout(self.layout)

    def reset_to_default(self):
        self._settings['CURRENT'] = self._settings['DEFAULT']
        for option, value in self._settings['CURRENT'].items():
            exec(f'self.{option}.setText(value)')

    def settings_changed(self):
        for option in self._settings['CURRENT'].keys():
            self._settings["CURRENT"][option] = str(eval(f'self.{option}'))
        with open(self._ini, 'w') as cf:
            self._settings.write(cf)


class CopyMetaDialog(QDialog):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.viewer = napari.viewer.current_viewer()

        self.setWindowTitle('CopyMetaInfo')

        QBtn = QDialogButtonBox.Yes | QDialogButtonBox.No
        self.buttonbox = QDialogButtonBox(QBtn)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

        self.combobox = QComboBox()
        for layer in self.viewer.layers:
            self.combobox.addItem(layer.name)

        self.layout = QVBoxLayout()
        message = QLabel(f'Layer {self.target} missing itk metadata, '
                         f'do you want to copy meta information from another layer?')
        self.layout.addWidget(message)
        self.layout.addWidget(self.combobox)
        self.layout.addWidget(self.buttonbox)
        self.setLayout(self.layout)
