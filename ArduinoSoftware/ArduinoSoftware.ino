#include "ArduinoSoftware.h"
#include "AltSoftSerial.h"
#include "Wire.h"
#include "AD5252.h"
#include "EMSSystem.h"
#include "EMSChannel.h"
#include "Debug.h"

// Setup for accepting commands via USB (ACCEPT_USB_COMMANDS = 1)
#define ACCEPT_USB_COMMANDS 1

// Initialization of control objects
AD5252 digitalPot(0);
EMSChannel emsChannel1(5, 4, A2, &digitalPot, 1);
EMSChannel emsChannel2(6, 7, A3, &digitalPot, 3);
EMSSystem emsSystem(2);

String serialCommandBuffer = "";

void setup() {
    Serial.begin(115200);  // 初始化串口

    debug_println(F("\nSETUP:"));

    // 这里不再初始化蓝牙模块，直接处理串口命令
    debug_println(F("\tBT: SKIPPED"));
    
    // Add the EMS channels and start the control
    debug_println(F("\tEMS: INITIALIZING CHANNELS"));
    emsSystem.addChannelToSystem(&emsChannel1);
    emsSystem.addChannelToSystem(&emsChannel2);
    EMSSystem::start();
    debug_println(F("\tEMS: INITIALIZED"));
    debug_println(F("\tEMS: STARTED"));
    debug_println(F("SETUP DONE (LED 13 WILL BE ON)"));

    emsSystem.shutDown();

    serialCommandBuffer.reserve(21);  // 预留空间给接收的命令

    pinMode(13, OUTPUT);
    digitalWrite(13, HIGH);  // 启动后点亮LED13
}

String hexCommandString;
const String BTLE_DISCONNECT = "Connection End";

void loop() {

    // 监听EMS系统是否有需要停止的信号
    if (emsSystem.check() > 0) {
        // 可以在这里添加更多的逻辑，例如停止某些信号等
    }

    // 从 Serial（包括USB串口和BLE串口）读取整行命令
    while (Serial.available()) {
        char c = Serial.read();

        if (c == '\n' || c == '\r') {
            if (serialCommandBuffer.length() > 0) {
                emsSystem.doCommand(&serialCommandBuffer);// 命令执行逻辑请查看emsSystem或文档
                serialCommandBuffer = "";
            }
        } else {
            serialCommandBuffer += c;
        }
    }
}

// 原来的代码中提供的测试工具
void debug_Toolkit(char c) {
    if (c == '1') {
        if (emsChannel1.isActivated()) {
            emsChannel1.deactivate();
            debug_println(F("\tEMS: Channel 1 inactive"));
        } else {
            emsChannel1.activate();
            debug_println(F("\tEMS: Channel 1 active"));
        }
    } else if (c == '2') {
        if (emsChannel2.isActivated()) {
            emsChannel2.deactivate();
            debug_println(F("\tEMS: Channel 2 inactive"));
        } else {
            emsChannel2.activate();
            debug_println(F("\tEMS: Channel 2 active"));
        }
    } else if (c == 'q') {
        digitalPot.setPosition(1, digitalPot.getPosition(1) + 1);
        debug_println(
                String(F("\tEMS: Intensity Channel 1: "))
                        + String(digitalPot.getPosition(1)));
    } else if (c == 'w') {
        digitalPot.setPosition(1, digitalPot.getPosition(1) - 1);
        debug_println(
                String(F("\tEMS: Intensity Channel 1: "))
                        + String(digitalPot.getPosition(1)));
    } else if (c == 'e') {
        // Note that this is channel 3 on Digipot but EMS channel 2
        digitalPot.setPosition(3, digitalPot.getPosition(3) + 1);
        debug_println(
                String(F("\tEMS: Intensity Channel 2: "))
                        + String(digitalPot.getPosition(3)));
    } else if (c == 'r') {
        // Note that this is channel 3 on Digipot but EMS channel 2
        digitalPot.setPosition(3, digitalPot.getPosition(3) - 1);
        debug_println(
                String(F("\tEMS: Intensity Channel 2: "))
                        + String(digitalPot.getPosition(3)));
    }
}
