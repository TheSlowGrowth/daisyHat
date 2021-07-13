#pragma once
#include <daisy.h>

namespace daisyhat
{
    /** Interface for a serial communication object that speaks to the host computer
     *  via a serial interface.
    */
    class SerialComms
    {
    public:
        virtual ~SerialComms() {}

        /** Transmits a zero terminated string synchronously */
        void Transmit(const char* zeroTerminatedString);

        /** Transmits a buffer of ASCII characters synchronously */
        virtual void Transmit(const char* buffer, size_t size) = 0;

        /** A LineListener receives lines of strings that were received
         *  from the host computer. */
        class LineListener
        {
        public:
            virtual ~LineListener() {}
            virtual void OnLineReceived(const char* line) = 0;
        };

        void AddListener(LineListener* listener);
        void RemoveListener(LineListener* listener);

    protected:
        /** Call this from your im,plementation to send a received line to all listeners. */
        void SendLineToListeners(const char* line);

    private:
        static constexpr size_t maxNumListeners_ = 16;
        daisy::Stack<LineListener*, maxNumListeners_> listeners_;
    };

    /** A SerialComms class with an internal RX line buffer. */
    class SerialCommsWithLineBuffer : public SerialComms
    {
    public:
        virtual ~SerialCommsWithLineBuffer() {}

    protected:
        /** Call this from the child class Rx callback to fill the receive buffer and
         *  send out the received lines to the listeners when required. */
        void RxCallback(const char* receivedBytes, size_t size);

    private:
        static constexpr size_t receiveBufferSize_ = 1024;
        daisy::FIFO<char, receiveBufferSize_> receiveBuffer_;
    };

    /** SerialComms over a USB CDC interface using the Daisy Seeds internal or external
     *  USB port. */
    class UsbSerialComms : public SerialCommsWithLineBuffer
    {
    public:
        UsbSerialComms(daisy::UsbHandle::UsbPeriph peripheral = daisy::UsbHandle::FS_INTERNAL);
        virtual ~UsbSerialComms() {}

        void Transmit(const char* data, size_t size) override;

    private:
        static UsbSerialComms* instance_;
        static void UsbRxCallback(uint8_t* buff, uint32_t* len);
        const daisy::UsbHandle::UsbPeriph peripheral_;
        daisy::UsbHandle usbHandle_;
    };
} // namespace daisyhat