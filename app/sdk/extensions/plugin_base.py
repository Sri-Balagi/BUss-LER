from abc import ABC, abstractmethod


class BizOSPlugin(ABC):
    """
    Base class for defining an extension/plugin to BizOS.
    Plugins can register tools, middleware, or commands into the system.
    """

    @abstractmethod
    def on_load(self) -> None:
        """Called when the plugin is loaded into the registry."""
        pass

    @abstractmethod
    def on_unload(self) -> None:
        """Called when the plugin is unloaded."""
        pass
