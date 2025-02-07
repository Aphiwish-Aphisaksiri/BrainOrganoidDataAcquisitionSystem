import dearpygui.dearpygui as dpg
import os

DEFAULT_UI_WIDTH = 1280
DEFAULT_UI_HEIGHT = 720

def initUiRender(*, APPS_UI_INIT_FILE_PATH=None):
    dpg.create_context()
    dpg.configure_app(init_file=APPS_UI_INIT_FILE_PATH)
    if APPS_UI_INIT_FILE_PATH == None:
        APPS_UI_INIT_FILE_PATH = os.path.join(os.path.dirname(__file__), 'ui', 'ui_init.ini')
    dpg.create_viewport(title='System In Package', width=DEFAULT_UI_WIDTH, height=DEFAULT_UI_HEIGHT)
    dpg.setup_dearpygui()

def renderUi():
    dpg.show_viewport()
    dpg.maximize_viewport()  # Maximize the viewport to the screen size
    dpg.start_dearpygui()
    dpg.destroy_context()