import serial
import threading
import time

class SerialDevice():
    _maxNameLength = 0

    def __init__(self, name, serialDevicePath):
        self._serialDevicePath = serialDevicePath
        self._name = name
        self._rxBuf = ""
        self._rxBufClearable = ""
        self._port = self._openSerialPort(serialDevicePath)
        self._receivedSignals = []

        # store longest name to align console printing
        if len(name) > SerialDevice._maxNameLength:
            _maxNameLength = len(name)

        # start receiver thread 
        self._shouldThreadStop = False
        self._lock = threading.Lock()
        self._rxThread = threading.Thread(target=SerialDevice._rxHandler, args=(self,), daemon=True)
        self._rxThread.start()

        print("SerialDevice: Connection created for " + name)

    def close(self):
        """ Closes the serial transport """
        self._shouldThreadStop = True
        self._rxThread.join()
        self._port.close()
        print("SerialDevice: Connection closed for " + self._name)
    
    def getEntireDataReceived(self):
        """ Returns the entire data that was received since the connection was opened """
        with self._lock:      
            return self._rxBuf
    
    def getDataReceived(self):
        """ Returns the data that was received since last call or since the connection was opened """
        with self._lock:
            result = self._rxBufClearable
            self._rxBufClearable = ""
            return result

    def sendSynchronous(self, message):
        """ Send a message synchronously 
            :param message: A bytes() object to send 
        """
        self._port.write(message)
        self._port.flush()

    def sendSignal(self, identifier):
        """ Sends a signal synchronously. Signals can be used to synchronize host and device.
            :param identifier: string of length < 32
        """
        if not isinstance(identifier, str):
            raise TypeError("Expected a string")
        if len(identifier) < 1 or len(identifier) > 32:
            raise ValueError("Signal identifier must have 1..32 characters")
        self.sendSynchronous(str.encode("!!>> Signal:{}\n".format(identifier)))

    def wasSignalReceived(self, identifier):
        """ Returns True if the requested signal was received from the device 
            :param identifier: string of length < 32
        """
        with self._lock:
            return identifier in self._receivedSignals
    
    def awaitSignal(self, identifier, timeoutInMs = 10000):
        """ Blocks until the requested signal was received from the device 
            :param identifier: string of length < 32
            :param timeoutInMs: a timeout in ms before an Exception is thrown; 
                                or 0 if signal should be awaited forever
        """
        startTimeMs = time.time() * 1000
        while not self.wasSignalReceived(identifier):
            now = time.time() * 1000
            if timeoutInMs > 0 and now - startTimeMs > timeoutInMs:
                raise Exception(f"Timeout waiting for signal '{identifier}' on device '{self._name}'")
    
    def _openSerialPort(self, serialDevicePath):
        numAttemps = 0
        timeoutInMs = 5000
        handle = None
        startTimeMs = time.time() * 1000
        while not handle:
            try:
                handle = serial.Serial(serialDevicePath, timeout=10)
            except serial.SerialException as e:
                numAttemps = numAttemps + 1
                now = time.time() * 1000
                if timeoutInMs > 0 and now - startTimeMs > timeoutInMs:
                    raise Exception(f"Failed to connect to serial port '{serialDevicePath}' after {numAttemps} attempts")
                time.sleep(0.25)
            except Exception as e:
                raise Exception(f"Exception while opening serial port '{serialDevicePath}': " + str(e))
        handle.flushInput()
        return handle
    
    def _rxHandler(parent):
        while not parent._shouldThreadStop:
            line = parent._port.readline()
            if not line:
                raise Exception("Timeout reading serial device: " + str(parent._serialDevicePath))

            # print the received line to the console
            decodedLine = line.decode().rstrip()
            alignedDeviceName = parent._name.rjust(SerialDevice._maxNameLength)
            print(f"{alignedDeviceName} # {decodedLine}")

            # append the received line to the parents buffers
            with parent._lock:
                parent._rxBuf = parent._rxBuf + decodedLine + "\n"
                parent._rxBufClearable = parent._rxBufClearable + decodedLine + "\n"

            # read signals from the device
            if decodedLine.startswith("!!>> Signal:"):
                signalIdentifier = decodedLine.removeprefix("!!>> Signal:")
                with parent._lock:
                    if signalIdentifier not in parent._receivedSignals:
                        parent._receivedSignals.append(signalIdentifier)

