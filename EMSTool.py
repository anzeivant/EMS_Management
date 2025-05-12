# -*- coding: utf-8 -*-
import asyncio
import time
from bleak import BleakClient, BleakScanner
from typing import List, Tuple, Dict

CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"


class EMSController:
    def __init__(self, device_address: str):
        self.device_address = device_address
        self.client: BleakClient = None

    async def connect(self):
        device = await BleakScanner.find_device_by_address(self.device_address)
        if device is None:
            raise Exception(f"Device {self.device_address} not found")
        self.client = BleakClient(device)
        await self.client.connect()

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

    async def send_command(self, command: str):
        command += '\n'
        if not self.client or not self.client.is_connected:
            await self.connect()
        await self.client.write_gatt_char(CHARACTERISTIC_UUID, command.encode('ascii'))
        print(f"[{self.device_address}] Sent command: {command.strip()}")

    async def stimulate(self, channel: int = 0, intensity: int = 225, time_ms: int = 500):
        command = f'G C{channel} I{intensity} T{time_ms}'
        await self.send_command(command)


class ActionUnit:
    def __init__(self, duration: float):
        self.duration = duration
        self.timeline: List[Tuple[float, int, str]] = []  # (time_point, index, command)

    def add_action(self, time_point: float, index: int, command: str):
        self.timeline.append((time_point, index, command))
        self.timeline.sort()

    def add_stimulate(self, time_point: float, index: int, channel: int, intensity: int, time_ms: int):
        command = f'G C{channel} I{intensity} T{time_ms}'
        self.add_action(time_point, index, command)

    async def execute(self, ems_controllers: Dict[int, EMSController]):
        start_time = time.time()
        executed_indices = set()

        while True:
            now = time.time()
            elapsed_time = now - start_time

            for idx, (time_point, index, command) in enumerate(self.timeline):
                if idx in executed_indices:
                    continue
                if elapsed_time >= time_point:
                    if index in ems_controllers:
                        await ems_controllers[index].send_command(command)
                        print(f"Executed action at {elapsed_time:.2f}s: index={index}, command={command}")
                    else:
                        print(f"No controller for channel {index}")
                    executed_indices.add(idx)

            if elapsed_time >= self.duration:
                break

            # 加一点微小 sleep 保护CPU
            await asyncio.sleep(0.001)


class EMSManagement:
    def __init__(self):
        self.controllers: Dict[int, EMSController] = {}
        self.action_sequence: List[ActionUnit] = []

    def register_controller(self, index: int, controller: EMSController):
        self.controllers[index] = controller

    def add_action_unit(self, action_unit: ActionUnit):
        self.action_sequence.append(action_unit)

    async def execute_all(self):
        # 先连接全部
        # for controller in self.controllers.values():
        #     await controller.connect()

        for action_unit in self.action_sequence:
            await action_unit.execute(self.controllers)

        # # 全部断开
        # for controller in self.controllers.values():
        #     await controller.disconnect()


async def main():
    management = EMSManagement()

    # 注册控制器
    management.register_controller(0, EMSController("c5:b2:02:10:53:5c"))
    management.register_controller(1, EMSController("93:b0:02:10:53:5c"))
    management.register_controller(2, EMSController("d8:b1:02:10:53:5c"))
    management.register_controller(3, EMSController("81:b2:02:10:53:5c"))

    # 💡 等待所有蓝牙连接完成
    print("Connecting to all EMS controllers...")
    for controller in management.controllers.values():
        await controller.connect()
    print("All controllers connected.")


    action_test = ActionUnit(duration=10.0)
    for i in range(1):
        action_test.add_action(0.1 + i * 0.5, 0, "G C0 I1 T2000")
        action_test.add_action(0.1 + i * 0.5, 0, "G C1 I1 T2000")
        action_test.add_action(0.1 + i * 0.5, 1, "G C0 I1 T2000")
        action_test.add_action(0.1 + i * 0.5, 1, "G C1 I1 T2000")
        action_test.add_action(0.1 + i * 0.5, 2, "G C0 I1 T2000")

        action_test.add_action(3, 0, "G C1 I1 T500")
        action_test.add_action(4, 0, "G C1 I1 T500")
    management.add_action_unit(action_test)

    # 执行
    while True:
        # 🔵 用户输入前蓝牙已连接好，输入后立即执行
        input(">>> Press Enter to start execution...")
        await management.execute_all()



if __name__ == "__main__":
    asyncio.run(main())
