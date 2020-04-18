from abc import ABC, abstractmethod
from typing import Union, List

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.interfaces.device import Device

from toiopy.cube import Cube
from toiopy.data import ToioException, ToioEventEmitter
from toiopy.util import set_timeout


class Scanner(ABC):
    DEFAULT_TIMEOUT_MS: int = 0

    def __init__(self, provider, timeout_ms: int = DEFAULT_TIMEOUT_MS):
        self.__timout_ms = timeout_ms
        self.__event_emitter: ToioEventEmitter = ToioEventEmitter()

        self.__provider = provider
        self.__peripherals: Union[Device, List[Device]] = None

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
            self.discover(self.__provider)
        finally:
            adapter.stop_scan()
        return self.executor()

    def on(self, event, listener):
        self.__event_emitter.on(event, listener)

    def off(self, event, listener):
        self.__event_emitter.remove_listener(event, listener)

    @abstractmethod
    def discover(self):
        pass

    @abstractmethod
    def executor(self) -> Union[Cube, List[Cube]]:
        pass


class NearestScanner(Scanner):

    SCAN_WINDOW_MS: int = 1000

    def __init__(
        self,
        provider,
        scan_window_ms: int = SCAN_WINDOW_MS,
        timeout_ms: int = Scanner.DEFAULT_TIMEOUT_MS,
    ):
        super(NearestScanner, self).__init__(provider, timeout_ms)
        self.__scan_window_ms = scan_window_ms
        self.__nearest_peripheral = None

    def discover(self, provider):
        set_timeout(lambda: None, NearestScanner.SCAN_WINDOW_MS)
        peripherals = provider.find_devices([Cube.TOIO_SERVICE_ID])
        if peripherals is None:
            raise ToioException("Failed to find device")

        peripherals = peripherals if type(peripherals) is list else [peripherals]
        print("{0} device discover".format(len(peripherals)))
        for peripheral in peripherals:
            if "toio" in peripheral.name:
                peripheral.connect()
                set_timeout(lambda: None, NearestScanner.SCAN_WINDOW_MS)
                peripheral._peripheral.readRSSI()
                if not peripheral._rssi_read.wait(NearestScanner.SCAN_WINDOW_MS / 1000):
                    raise RuntimeError("Exceeded timeout waiting for RSSI value!")
                if (
                    self.__nearest_peripheral is None
                    or peripheral._rssi > self.__nearest_peripheral._rssi
                ):
                    self.__nearest_peripheral = peripheral
                set_timeout(lambda: None, NearestScanner.SCAN_WINDOW_MS)
        print("discovered")

    def executor(self) -> Cube:
        if self.__nearest_peripheral is None:
            raise ToioException("Failed to find device")
        return Cube(self.__nearest_peripheral)
