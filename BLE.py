# -*- coding: utf-8 -*-
import asyncio
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

# 设备的Characteristic UUID (使用你提供的相同UUID)
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
# 设备的MAC地址 (替换为你实际的从机BLE地址)
DEVICE_ADDRESS = "c5:b2:02:10:53:5c"  # 示例地址，请替换为你的从机地址

# 控制命令 (直接使用ASCII字符串，不需要HEX形式)
LED_ON_CMD = "on"
LED_OFF_CMD = "off"


async def control_led(state: bool):
    """控制LED状态"""
    device = await BleakScanner.find_device_by_address(DEVICE_ADDRESS)
    if device is None:
        print(f"Could not find device with address {DEVICE_ADDRESS}")
        return

    async with BleakClient(device) as client:
        print("Connected to device")
        command = LED_ON_CMD if state else LED_OFF_CMD
        await client.write_gatt_char(CHARACTERISTIC_UUID, command.encode('ascii'))
        print(f"Sent command: {command}")


async def main():
    """主控制循环"""
    while True:
        user_input = input("Enter command (on/off/quit): ").strip().lower()

        if user_input == "quit":
            break
        elif user_input == "on":
            await control_led(True)
        elif user_input == "off":
            await control_led(False)
        else:
            print("Invalid command. Please enter 'on', 'off' or 'quit'.")


if __name__ == "__main__":
    asyncio.run(main())

