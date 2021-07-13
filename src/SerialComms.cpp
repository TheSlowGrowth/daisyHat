#include "SerialComms.h"
#include <cstring>

namespace daisyhat
{
    void SerialComms::Transmit(const char* zeroTerminatedString)
    {
        const auto len = strlen(zeroTerminatedString);
        Transmit(zeroTerminatedString, len);
    }

    void SerialComms::AddListener(LineListener* listener)
    {
        listeners_.PushBack(listener);
    }

    void SerialComms::RemoveListener(LineListener* listener)
    {
        listeners_.RemoveAllEqualTo(listener);
    }

    void SerialComms::SendLineToListeners(const char* line)
    {
        for (size_t i = 0; i < listeners_.GetNumElements(); i++)
            listeners_[i]->OnLineReceived(line);
    }

    // ========================================================================

    // ========================================================================

    void SerialCommsWithLineBuffer::RxCallback(const char* receivedBytes, size_t size)
    {
        for (size_t i = 0; i < size; i++)
        {
            bool sendBufferContentsNow = false;
            // newline received - line is complete
            sendBufferContentsNow |= receivedBytes[i] == '\n';
            // buffer can only hold this character before it's full
            sendBufferContentsNow |= receiveBuffer_.GetNumElements() == receiveBuffer_.GetCapacity() - 2; /* one more character + '\0' */

            if (sendBufferContentsNow)
            {
                // add terminating zero, send to listeners, clear.
                receiveBuffer_.PushBack('\0');
                SendLineToListeners(&receiveBuffer_[0]);
                receiveBuffer_.Clear();
            }
            else
                receiveBuffer_.PushBack(receivedBytes[i]);
        }
    }

    // ========================================================================

    // ========================================================================

    UsbSerialComms* UsbSerialComms::instance_ = nullptr;

    void UsbSerialComms::UsbRxCallback(uint8_t* buff, uint32_t* len)
    {
        if (instance_)
            instance_->RxCallback(reinterpret_cast<char*>(buff), *len);
    }

    UsbSerialComms::UsbSerialComms(daisy::UsbHandle::UsbPeriph peripheral) :
        peripheral_(peripheral)
    {
        usbHandle_.Init(peripheral);

        assert(instance_ == nullptr);
        instance_ = this;
        usbHandle_.SetReceiveCallback(&UsbRxCallback, peripheral);
    }

    void UsbSerialComms::Transmit(const char* text, size_t size)
    {
        // TransmitInternal/TransmitExternal want a non-const pointer to the data....
        daisy::FixedCapStr<256> modifyableBuffer(text, size);

        if (peripheral_ == daisy::UsbHandle::FS_INTERNAL
            || peripheral_ == daisy::UsbHandle::FS_BOTH)
            while (usbHandle_.TransmitInternal(
                       reinterpret_cast<uint8_t*>(modifyableBuffer.Data()), size)
                   != daisy::UsbHandle::Result::OK)
            {
            }

        if (peripheral_ == daisy::UsbHandle::FS_EXTERNAL
            || peripheral_ == daisy::UsbHandle::FS_BOTH)
            while (usbHandle_.TransmitExternal(
                       reinterpret_cast<uint8_t*>(modifyableBuffer.Data()), size)
                   != daisy::UsbHandle::Result::OK)
            {
            }
    }

} // namespace daisyhat