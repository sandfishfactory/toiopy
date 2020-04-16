from abc import ABC, abstractmethod

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.interfaces.device import Device

from toiopy.cube import Cube
from toiopy.data import ToioException, ToioEventEmitter


class Scanner(ABC):
    DEFAULT_TIMEOUT_MS: int = 0

    def __init__(self, provider, timeout_ms: int = DEFAULT_TIMEOUT_MS):
        self.__timout_ms = timeout_ms
        self.__event_emitter: ToioEventEmitter = ToioEventEmitter()

        self.__provider = provider
        self.__devices = None

    @classmethod
    def get_provider(cls):
        provider = Adafruit_BluefruitLE.get_provider()
        provider.initialize()
        return provider

    def start(self):
        self.__provider.clear_cached_data()
        adapter = self.__provider.get_default_adapter()
        adapter.power_on()

        self.__provider.disconnect_devices([Cube.TOIO_SERVICE_ID])

        try:
            adapter.start_scan()
            self.__devices = [self.__provider.find_device()]
            if self.__devices is None:
                raise ToioException("Failed to find device")
        finally:
            adapter.stop_scan()

        return [Cube(device) for device in self.__devices]

    def stop(self):
        if self.__devices:
            for device in self.__devices:
                device.disconnect()

    def on(self, event, listener):
        self.__event_emitter.on(event, listener)

    def off(self, event, listener):
        self.__event_emitter.remove_listener(event, listener)

    @abstractmethod
    def on_discover(self, peripheral: Device):
        pass

    @abstractmethod
    def executor(self, peripheral: Device):
        pass


class NearestScanner(Scanner):

    SCAN_WINDOW_MS: int = 1

    def __init__(
        self,
        provider,
        scan_window_ms: int = SCAN_WINDOW_MS,
        timeout_ms: int = Scanner.DEFAULT_TIMEOUT_MS,
    ):
        super(NearestScanner, self).__init__(provider, timeout_ms)
        self.__scan_window_ms = scan_window_ms

    def on_discover(self, peripheral):
        pass

    def executor(self, peripheral):
        pass
