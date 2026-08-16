from app.sdk.decorators.decorators import capability
from app.sdk.extensions.plugin_base import BizOSPlugin


class MathToolsPlugin(BizOSPlugin):
    def on_load(self) -> None:
        print("MathToolsPlugin loaded.")

    def on_unload(self) -> None:
        print("MathToolsPlugin unloaded.")

    @capability(name="add", description="Adds two numbers.")
    def add(self, a: float, b: float) -> float:
        return a + b

    @capability(name="subtract", description="Subtracts b from a.")
    def subtract(self, a: float, b: float) -> float:
        return a - b
