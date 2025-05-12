import asyncio
import threading
import tkinter as tk
from tkinter import ttk
from EMSTool import EMSController


class EMSGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EMS 调试工具")

        self.device_addresses = [
            "c5:b2:02:10:53:5c",
            "93:b0:02:10:53:5c",
            "d8:b1:02:10:53:5c",
            "81:b2:02:10:53:5c"
        ]

        self.controllers = []
        self.controller = None
        self.index = 0
        self.channel = 0
        self.intensity = 1
        self.duration = 2000

        self.setup_ui()
        threading.Thread(target=self.init_ble_controllers).start()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid()

        # 设备选择
        ttk.Label(frame, text="设备选择：").grid(column=0, row=0, sticky="w")
        for i in range(4):
            ttk.Button(frame, text=f"EMS{i+1}", command=lambda idx=i: self.set_device(idx)).grid(column=i+1, row=0)

        # 通道切换
        ttk.Label(frame, text="通道：").grid(column=0, row=1, sticky="w")
        self.channel_label = ttk.Label(frame, text="通道 0")
        self.channel_label.grid(column=1, row=1)
        ttk.Button(frame, text="切换通道", command=self.toggle_channel).grid(column=2, row=1)

        # 强度控制
        ttk.Label(frame, text="强度：").grid(column=0, row=2, sticky="w")
        ttk.Button(frame, text="-", command=lambda: self.change_intensity(-1)).grid(column=1, row=2)
        self.intensity_label = ttk.Label(frame, text=str(self.intensity))
        self.intensity_label.grid(column=2, row=2)
        ttk.Button(frame, text="+", command=lambda: self.change_intensity(1)).grid(column=3, row=2)

        # 持续时间控制
        ttk.Label(frame, text="持续时间(ms)：").grid(column=0, row=3, sticky="w")
        ttk.Button(frame, text="-", command=lambda: self.change_duration(-200)).grid(column=1, row=3)
        self.duration_label = ttk.Label(frame, text=str(self.duration))
        self.duration_label.grid(column=2, row=3)
        ttk.Button(frame, text="+", command=lambda: self.change_duration(200)).grid(column=3, row=3)

        # 刺激按钮
        ttk.Button(frame, text="施加刺激", command=self.trigger_stimulate).grid(column=0, row=4, columnspan=4, pady=10)

        self.status_label = ttk.Label(frame, text="初始化中...")
        self.status_label.grid(column=0, row=5, columnspan=4)

    def set_device(self, index):
        self.index = index
        self.controller = self.controllers[index]
        self.status_label.config(text=f"当前设备：EMS{index + 1}")

    def toggle_channel(self):
        self.channel = 1 - self.channel
        self.channel_label.config(text=f"通道 {self.channel}")

    def change_intensity(self, delta):
        self.intensity = max(1, min(255, self.intensity + delta))
        self.intensity_label.config(text=str(self.intensity))

    def change_duration(self, delta):
        self.duration = max(200, self.duration + delta)
        self.duration_label.config(text=str(self.duration))

    def init_ble_controllers(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._connect_controllers())

    async def _connect_controllers(self):
        self.controllers = [EMSController(addr) for addr in self.device_addresses]
        for i, ctrl in enumerate(self.controllers):
            try:
                await ctrl.connect()
                print(f"EMS{i+1} 已连接")
            except Exception as e:
                print(f"连接 EMS{i+1} 失败: {e}")
        self.controller = self.controllers[0]
        self.status_label.config(text="连接成功，默认 EMS1")

    def trigger_stimulate(self):
        if not self.controller:
            self.status_label.config(text="未连接设备")
            return

        async def send():
            await self.controller.stimulate(
                channel=self.channel,
                intensity=self.intensity,
                time_ms=self.duration
            )
            self.status_label.config(
                text=f"发送成功：EMS{self.index + 1} 通道{self.channel} 强度{self.intensity} 时间{self.duration}ms"
            )

        asyncio.run(send())


def main():
    root = tk.Tk()
    app = EMSGuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
