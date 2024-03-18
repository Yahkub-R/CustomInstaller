import os
from datetime import datetime
import sys


class StreamRedirector:
    def __init__(self, widget, filename = None):
        self.widget = widget
        self.filename = filename

    def write(self, text):
        self.widget.insertPlainText(text)
        if self.filename is not None:
            with open(self.filename, 'a') as file:
                file.write(text)

    def flush(self):
        pass