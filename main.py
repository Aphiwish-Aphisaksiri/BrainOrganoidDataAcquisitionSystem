# TODO: Find a way to make it run faster (Multi-processing?)

import os
from app import App
from util.uirender import initUiRender, renderUi

def main():
    app = App()
    app.initializeThreads()

    ui_init_file_path = os.path.join(os.path.dirname(__file__), 'ui.ini')
    initUiRender(APPS_UI_INIT_FILE_PATH=ui_init_file_path)
    
    app.renderApp()
    
    renderUi()

    app.stopApp()

if __name__ == '__main__':
    main()