from app.sdk.decorators.decorators import capability
from app.sdk.extensions.plugin_base import BizOSPlugin


class MyPlugin(BizOSPlugin):
    def on_load(self) -> None:
        print("Plugin loaded successfully.")

    def on_unload(self) -> None:
        print("Plugin unloaded successfully.")

    @capability(name="hello_world", description="Prints hello world")
    def hello(self) -> str:
        return "Hello World"
