# RFID-to-AWS
Read RFID cards from a serial device and publish them to AWS Iot cloud platform using MQTT

## Introduction

In this demo, I set up a Raspberry Pi to scan RFID (Radio Frequency Identification) cards and tags and send the data to the AWS IoT (Internet of Things) cloud platform. We will use Python to read a Parallax RFID module over serial, check for errors, and publish using MQTT.

## Getting Started with RFID

I picked up this RFID reader over 14 years ago after seeing a HackADay article and have been exploring the underlying technology and applications ever since. The RFID cards and tags operate at 125kHz and contain a 10-character alphanumeric string similar to a barcode. RFID technology has many applications, including security, inventory management, and access control.

## Setting Up the Raspberry Pi

A Raspberry Pi is a single-board computer (SBC) that runs a Linux operating system (OS) and has programmable GPIO (General Purpose Input/Output) pins, making it easy to connect to external sensors and gadgets.

The Parallax RFID module we are using can be read over a serial connection but uses 5V signal logic, which needs to be stepped down to 3.3V to avoid damaging the Raspberry Pi's GPIO interface. We use a simple voltage divider circuit consisting of two resistors for this purpose.

## Configuring AWS IoT

Amazon AWS provides a well-documented IoT SDK. Once the local software environment is configured, we need to generate certificates on AWS to securely authenticate the device and encrypt communications using asymmetrical Public Key Infrastructure (PKI).

## Using MQTT for Communication

MQTT is the protocol of choice because it is lightweight and uses a publish-subscribe model to ensure message delivery, even over slow or high-latency network connections. Capturing and publishing the card data was the easy part. The next logical step is to use the AWS Lambda data transformation service to adapt the scanned card info for storage in an AWS DynamoDB. This transforms a simple “scan and store” operation into the beginnings of a scalable inventory management platform that can be analyzed using AWS EMR tools.

## Future Plans

I plan further updates on this project, including a 3D-printed case and analysis of how card details are exchanged using SDR (Software Defined Radio). Stay tuned for more!

## Conclusion

RFID technology, combined with AWS IoT services, offers powerful solutions for inventory management and security. By leveraging these technologies, we can create scalable and robust systems tailored to various applications.
