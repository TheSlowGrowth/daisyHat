import serial
import threading
import time

class SerialDevice():
    _max_name_length = 0

    def __init__(self, name, serial_device_path):
        self._serial_device_path = serial_device_path
        self._name = name
        self._rx_buf = ""
        self._rx_buf_clearable = ""
        self._port = self._open_serial_port(serial_device_path)
        self._received_signals = []

        # store longest name to align console printing
        if len(name) > SerialDevice._max_name_length:
            SerialDevice._max_name_length = len(name)

        # start receiver thread
        self._should_thread_stop = False
        self._lock = threading.Lock()
        self._rx_thread = threading.Thread(target=self._rx_handler, daemon=True)
        self._rx_thread.start()

        print("SerialDevice: Connection created for " + name)

    def close(self):
        """ Closes the serial transport """
        self._should_thread_stop = True
        self._rx_thread.join(timeout=5)
        try:
            self._port.close()
        except Exception:
            pass
        print("SerialDevice: Connection closed for " + self._name)

    def get_entire_data_received(self):
        """ Returns the entire data that was received since the connection was opened """
        with self._lock:
            return self._rx_buf

    def get_data_received(self):
        """ Returns the data that was received since last call or since the connection was opened """
        with self._lock:
            result = self._rx_buf_clearable
            self._rx_buf_clearable = ""
            return result

    def send_synchronous(self, message):
        """ Send a message synchronously
            :param message: A bytes() object to send
        """
        self._port.write(message)
        self._port.flush()

    def send_signal(self, identifier):
        """ Sends a signal synchronously. Signals can be used to synchronize host and device.
            :param identifier: string of length < 32
        """
        if not isinstance(identifier, str):
            raise TypeError("Expected a string")
        if len(identifier) < 1 or len(identifier) > 32:
            raise ValueError("Signal identifier must have 1..32 characters")
        self.send_synchronous(str.encode("!!>> Signal:{}\n".format(identifier)))

    def was_signal_received(self, identifier):
        """ Returns True if the requested signal was received from the device
            :param identifier: string of length < 32
        """
        with self._lock:
            return identifier in self._received_signals

    def await_signal(self, identifier, timeout_ms=10000):
        """ Blocks until the requested signal was received from the device
            :param identifier: string of length < 32
            :param timeout_ms: a timeout in ms before an Exception is thrown;
                                or 0 if signal should be awaited forever
        """
        start_time_ms = time.time() * 1000
        while not self.was_signal_received(identifier):
            now = time.time() * 1000
            if timeout_ms > 0 and now - start_time_ms > timeout_ms:
                raise Exception(f"Timeout waiting for signal '{identifier}' on device '{self._name}'")
            time.sleep(0.01)

    def _open_serial_port(self, serial_device_path):
        num_attempts = 0
        timeout_ms = 5000
        handle = None
        start_time_ms = time.time() * 1000
        while not handle:
            try:
                # short read timeout: the reader thread checks the stop flag
                # frequently, so close() stays responsive
                handle = serial.Serial(serial_device_path, timeout=0.2)
            except serial.SerialException as e:
                num_attempts = num_attempts + 1
                now = time.time() * 1000
                if timeout_ms > 0 and now - start_time_ms > timeout_ms:
                    raise Exception(f"Failed to connect to serial port '{serial_device_path}' after {num_attempts} attempts")
                time.sleep(0.25)
            except Exception as e:
                raise Exception(f"Exception while opening serial port '{serial_device_path}': " + str(e))
        handle.flushInput()
        return handle

    def _rx_handler(self):
        while not self._should_thread_stop:
            try:
                line = self._port.readline()
            except Exception:
                # port was closed (cf. close()) - stop reading
                break
            if not line:
                # read timeout: the device is legitimately silent
                # (e.g. held at a checkpoint) - keep waiting
                continue

            # print the received line to the console
            decoded_line = line.decode().rstrip()
            aligned_device_name = self._name.rjust(SerialDevice._max_name_length)
            print(f"{aligned_device_name} # {decoded_line}")

            # append the received line to the rx buffers
            with self._lock:
                self._rx_buf = self._rx_buf + decoded_line + "\n"
                self._rx_buf_clearable = self._rx_buf_clearable + decoded_line + "\n"

            # read signals from the device
            if decoded_line.startswith("!!>> Signal:"):
                signal_identifier = decoded_line.removeprefix("!!>> Signal:")
                with self._lock:
                    if signal_identifier not in self._received_signals:
                        self._received_signals.append(signal_identifier)
