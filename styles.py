console_style = """
    QTextEdit {
        background-color: black; 
        color: white; 
        font-family: Consolas; 
        font-size: 12px;
    }
    QScrollBar:vertical {
        border: none;
        background: #2A2A2A;
        width: 10px;
        border-radius: 2px;
        padding-bottom:15px;
    }
    QScrollBar::handle:vertical {
        padding-bottom:15px;
        background: #5B5B5B;
        min-height: 20px;
        border-radius: 2px;
    }
    QScrollBar::add-line:vertical {
        border: none;
        background: none;
        height: 0px;
    }
    QScrollBar::sub-line:vertical {
        border: none;
        background: none;
        height: 0px;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    QPushButton {
        background-color: #333333;
        color: white;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #555555;
    }
    QLabel {
        color: white;
        font-weight: bold;
    }
"""

# styles.py update
dark_theme_style = """
    #main {
        background-color: #2b2d30;
        border-radius: 10px;
        border: 1px solid #404040;
        border-top-left-radius:0;
        border-top-right-radius:0;
        border-top-width:0px;
    }
    #test{    
        background-color: red;
        border: 5px solid yellow; 
    }
    #header {
        background-color: #2b2d30;
        border-radius: 10px;
        border: 1px solid #404040;
        border-bottom-left-radius:0;
        border-bottom-right-radius:0;
        border-bottom-width:0px;
    }
    QLabel{
        color: white;
    }
    QLineEdit{
        padding: 5px;
        margin:2px;
        color:white;
        background: #505354; 
        border: 0px solid darkgray;
        selection-background-color: lightgray;
        border-radius: 3px;
    }
    QPushButton {
        background-color: #505354;
        color: white;
        border-radius: 3px;
        padding: 5px;
        margin: 2px;
    }
    QPushButton:hover {
        background-color: #777777;
    }
    QComboBox {
        background-color: #505354;
        color: white;
        border-radius: 3px;
        padding: 5px;
        margin: 2px;
    }
    QComboBox:hover {
        background-color: #777777;
    }
    QListView{
        color:white;
    }
    QComboBox:editable {
        color:white;
        background-color: #000000;
        border: 2px solid darkgray;
        selection-background-color: lightgray;
    }
    QComboBox::items{
        color:white;
    }
    QComboBox::drop-down {
        color:white;
        width: 20px; 
        border-left-width: 1px;
        border-left-color: #777777;
        border-left-style: solid;
    }
    QComboBox QAbstractItemView {
        background-color: #505354;
        color: white;
        selection-background-color: #777777;
        selection-color: black;
        border-radius: 3px;
        margin: 0px;
    }
    QTextEdit {
        border: none;
        border-radius:5px;
    }
    #banner{
        border-radius:3px;
        color: white;
        background-color: #4e8752; 
    }
    #banner > * {
        padding-left:5px;
        color: white;
    }
    #dismiss-update{
        width: 10px;
    }
    #btn_close,#btn_minimize{
        border-radius:0;
        margin:0;
        background-color: #2b2d30;
        font-weight: bold;
    }
    #btn_minimize{
        border: 1px solid #404040;
        border-bottom-width:0px;
        border-left-width:0px;
        border-right-width:0px;
    }
    #btn_close{
        border-radius: 10px;
        border: 1px solid #404040;
        border-bottom-left-radius:0;
        border-top-left-radius:0;
        border-bottom-right-radius:0;
        border-bottom-width:0px;
        border-left-width:0px;
    }
    #btn_close:hover{
        
    }
    #btn_close:hover {
        background-color: #F44336;
    }
    #btn_minimize:hover {
        background-color: #777777;
        color: white;
        font-weight: bold;
    }
    #title {
        color: white;
        font-size: 14px;
        font-weight: bold;
        padding-left:5px;
    }
    QPushButton:disabled {
        color: #999;
    }
    QComboBox:disabled {
        color: #999;
    }
    #scroll-to-bottom{
        color: white;
        border-radius: 2px;
        padding: 0px;
        margin: 0px;
        font-size:8px;
    }
"""
