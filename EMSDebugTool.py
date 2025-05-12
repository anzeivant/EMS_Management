import asyncio
from bleak import BleakClient, BleakScanner
from typing import List, Tuple, Dict
from EMSTool import EMSController


async def ems_debug_tool():
    """
    交互式调试 EMS 刺激效果的工具
    """
    device_address1 = "c5:b2:02:10:53:5c"
    device_address2 = "93:b0:02:10:53:5c"
    device_address3 = "d8:b1:02:10:53:5c"
    device_address4 = "81:b2:02:10:53:5c"

    controller1 = EMSController(device_address1)
    controller2 = EMSController(device_address2)
    controller3 = EMSController(device_address3)
    controller4 = EMSController(device_address4)
    await controller1.connect()
    await controller2.connect()
    await controller3.connect()
    await controller4.connect()

    controllers = [controller1, controller2, controller3, controller4]
    controller = controllers[0]

    print("\n--- EMS 调试工具 ---")
    index = 1
    channel = 0
    intensity = 1
    duration = 2000

    try:
        while True:
            user_input = input(">>> ").strip()
            if user_input.lower() == 'exit':  # 退出程序
                break
            elif user_input.lower()[0] == 'q':  # 提高强度
                step = 1
                if len(user_input) > 1:
                    try:
                        step = int(user_input[1:])
                    except ValueError:
                        print("格式错误")
                intensity += step
                if intensity <= 0:
                    intensity = 1
                elif intensity > 255:
                    intensity = 255
            elif user_input.lower()[0] == 'w':  # 降低强度
                step = 1
                if len(user_input) > 1:
                    try:
                        step = int(user_input[1:])
                    except ValueError:
                        print("格式错误")
                intensity -= step
                if intensity <= 0:
                    intensity = 1
                elif intensity > 255:
                    intensity = 255
            elif user_input.lower()[0] == 'e':  # 提高持续时间
                step = 200
                if len(user_input) > 1:
                    try:
                        step = int(user_input[1:])
                    except ValueError:
                        print("格式错误")
                duration += step
                if duration <= 200:
                    duration = 200
            elif user_input.lower()[0] == 'r':  # 降低持续时间
                step = 200
                if len(user_input) > 1:
                    try:
                        step = int(user_input[1:])
                    except ValueError:
                        print("格式错误")
                duration -= step
                if duration <= 200:
                    duration = 200
            elif user_input.lower()[0] == 't':  # 切换通道
                if channel == 0:
                    channel = 1
                else:
                    channel = 0
            elif user_input.lower()[0] == '1':  # 切换ems设备
                index = 1
                controller = controllers[0]
            elif user_input.lower()[0] == '2':
                index = 2
                controller = controllers[1]
            elif user_input.lower()[0] == '3':
                index = 3
                controller = controllers[2]
            elif user_input.lower()[0] == '4':
                index = 4
                controller = controllers[3]
            elif user_input.lower()[0] == 's':
                await controller.stimulate(channel=channel, intensity=intensity, time_ms=duration)

            print('当前ems设备：' + str(index) + ' 通道：' + str(channel) + ' 强度：' + str(intensity) + ' 持续时间：' + str(duration))
    finally:
        await controller.disconnect()
        print("已断开 EMS 设备连接。")


if __name__ == "__main__":
    asyncio.run(ems_debug_tool())
