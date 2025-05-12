/**
 * ArduinoSoftware_Arduino_IDE
 *
 *  Copyright 2016 by Tim Duente <tim.duente@hci.uni-hannover.de>
 *  Copyright 2016 by Max Pfeiffer <max.pfeiffer@hci.uni-hannover.de>
 *
 *  Licensed under "The MIT License (MIT) - military use of this product is forbidden - V 0.2".
 *  Some rights reserved. See LICENSE.
 *
 * @license "The MIT License (MIT) - military use of this product is forbidden - V 0.2"
 * <https://bitbucket.org/MaxPfeiffer/letyourbodymove/wiki/Home/License>
 */

/*
 * EMSSystem.cpp
 *
 *  Created on: 26.05.2014
 *  Author: Tim Duente
 *  Edit by: Max Pfeiffer - 13.06.2015
 */

#include "EMSSystem.h"

EMSSystem::EMSSystem(uint8_t channels) {
	emsChannels = (EMSChannel**) malloc(channels * sizeof(EMSChannel*));
	maximum_channel_count = channels;
	current_channel_count = 0;
}

EMSSystem::~EMSSystem() {
	free(emsChannels);
}

void EMSSystem::addChannelToSystem(EMSChannel *emsChannel) {
	if (current_channel_count < maximum_channel_count) {
		emsChannels[current_channel_count] = emsChannel;
		current_channel_count++;
	}
}

// get the next number out of a String object and return it
int EMSSystem::getNextNumberOfString(String *command, uint8_t startIndex) {
	int value = 0;
	bool valid = false;
	// Select the number in the string
	for (uint8_t i = startIndex + 1; i < command->length(); i++) {
		char tmp = command->charAt(i);
		if (tmp >= '0' && tmp <= '9') {
			value = value * 10 + (tmp - '0');
			valid = true;
		} else {
			break;
		}
	}
	if (valid)
		return value;
	else
		return -1;
}

void EMSSystem::doActionCommand(String *command) {
	if (command->length() == 0) {
		debug_println(F("[EMS] Error: Command is empty."));
		return;
	}

	debug_print(F("[EMS] Command Received:"));
	debug_println(*command);

	int currentChannel = -1;
	int signalLength = -1;
	int signalIntensity = -1;

	// Channel
	int idxChannel = command->indexOf(CHANNEL);
	if (idxChannel != -1) {
		currentChannel = getNextNumberOfString(command, idxChannel);
		debug_print(F("[EMS] Channel:"));
		debug_println(String(currentChannel));
	} else {
		debug_println(F("[EMS] Channel not found."));
	}

	// Signal Length
	int idxTime = command->indexOf(TIME);
	if (idxTime != -1) {
		signalLength = getNextNumberOfString(command, idxTime);
		if (signalLength > 5000) {
			debug_println(F("[EMS] Signal length too long, clamped to 5000"));
			signalLength = 5000;
		}
		debug_print(F("[EMS] Signal Length:"));
		debug_println(String(signalLength));
		if (currentChannel >= 0 && currentChannel < current_channel_count) {
			emsChannels[currentChannel]->setSignalLength(signalLength);
		}
	} else {
		debug_println(F("[EMS] Signal length not found."));
	}

	// Intensity
	int idxIntensity = command->indexOf(INTENSITY);
	if (idxIntensity != -1) {
		signalIntensity = getNextNumberOfString(command, idxIntensity);
		debug_print(F("[EMS] Intensity:"));
		debug_println(String(signalIntensity));
		if (currentChannel >= 0 && currentChannel < current_channel_count) {
			emsChannels[currentChannel]->setIntensity(signalIntensity - 1);
		}
	} else {
		debug_println(F("[EMS] Intensity not found."));
	}

	// Activate Channel
	if (currentChannel >= 0 && currentChannel < current_channel_count) {
		debug_print(F("[EMS] Activating channel:"));
		debug_println(String(currentChannel));
		emsChannels[currentChannel]->activate();
		emsChannels[currentChannel]->applySignal();
	} else {
		debug_println(F("[EMS] Invalid channel, shutting down all."));
		shutDown();
	}
}



void EMSSystem::shutDown() {
	for (int i = 0; i < current_channel_count; i++) {
		emsChannels[i]->deactivate();
	}
}

/* TODO change to set commands */

void EMSSystem::setOption(String *option) {
	if (option->length() == 0) {
		debug_println(F("[EMS] Error: Option is empty."));
		return;
	}

	debug_print(F("[EMS] Option Received:"));
	debug_println(*option);

	char secChar = option->charAt(3);
	int channel = -1;
	int value = -1;

	switch (option->charAt(2)) {
	case 'C':
		if (secChar == 'T' && getChannelAndValue(option, &channel, &value)) {
			debug_println(F("[EMS] Set Channel Change Time"));
			debug_print(F("[EMS] Channel:"));
			debug_println(String(channel));
			debug_print(F("[EMS] Change Time:"));
			debug_println(String(value));
			// emsChannels[channel]->setIncreaseDecreaseTime(value);
		} else {
			debug_println(F("[EMS] Invalid Change Time Option"));
		}
		break;

	case 'M':
		if (secChar == 'A' && getChannelAndValue(option, &channel, &value)) {
			debug_println(F("[EMS] Set Max Intensity"));
			debug_print(F("[EMS] Channel:"));
			debug_println(String(channel));
			debug_print(F("[EMS] Max Intensity:"));
			debug_println(String(value));
			emsChannels[channel]->setMaxIntensity(value);
		} else if (secChar == 'I' && getChannelAndValue(option, &channel, &value)) {
			debug_println(F("[EMS] Set Min Intensity"));
			debug_print(F("[EMS] Channel:"));
			debug_println(String(channel));
			debug_print(F("[EMS] Min Intensity:"));
			debug_println(String(value));
			emsChannels[channel]->setMinIntensity(value);
		} else {
			debug_println(F("[EMS] Invalid Min/Max Option"));
		}
		break;

	default:
		debug_println(F("[EMS] Unknown Option Type"));
		break;
	}
}



bool EMSSystem::getChannelAndValue(String *option, int *channel, int *value) {
	int left = option->indexOf('[');
	int right = option->lastIndexOf(']');
	int seperator = option->indexOf(',', left + 1);

	if (left < seperator && seperator < right && left != -1 && right != -1
			&& seperator != -1) {
		String help = option->substring(left + 1, seperator);
		(*channel) = help.toInt();
		help = option->substring(seperator + 1, right);
		(*value) = help.toInt();

		//Parsing successful
		//Check whether channel exists
		return isInRange((*channel));
	}
//Parsing not successful
	return false;
}

bool EMSSystem::isInRange(int channel) {
	return (channel >= 0 && channel < current_channel_count);
}

uint8_t EMSSystem::check() {
	uint8_t stopCount = 0;
	for (uint8_t i = 0; i < current_channel_count; i++) {
		stopCount = stopCount + emsChannels[i]->check();
	}
	return stopCount;
}

void EMSSystem::doCommand(String *command) {
	if (command->length() > 0) {
		if (command->indexOf(ACTION) != -1) {
			doActionCommand(command);
		} else if (command->charAt(0) == OPTION) {
			setOption(command);
		} else {
			debug_print("EMS SYSTEM: Unknown command: ");
			debug_println((*command));
		}
	}
}

void EMSSystem::start() {
	EMSChannel::start();
}
