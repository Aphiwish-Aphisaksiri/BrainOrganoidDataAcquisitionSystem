import dearpygui.dearpygui as dpg

class UiSettings:
    def __init__(self, app):
        """Initialize the settings UI with a reference to the App instance."""
        self.__app = app

    def render(self):
        """Render the settings UI."""
        with dpg.window(label="Settings", tag="tag_window_settings", width=400, height=300):
            dpg.add_text("|Application Control|")
            dpg.add_button(label="Exit", callback=self.exitApplication, tag="btn_Exit", width=126)

    def exitApplication(self):
        """Callback to exit the application."""
        dpg.set_value("daq_setting_feedback", "Exiting application...")
        self.__app.stopApp()  # Call the App's stop method to terminate all processes and threads
        dpg.stop_dearpygui()  # Stop the Dear PyGui event loop