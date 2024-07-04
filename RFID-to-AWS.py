import serial
import RPi.GPIO as GPIO
import time
import string
from datetime import datetime
from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import threading
import json
from utils.command_line_utils import CommandLineUtils

# Configuration
SERIAL_PORT = '/dev/serial0'  # Using GPIO ports on Raspberry Pi
BAUD_RATE = 2400

# AWS MQTT Configuration
cmdData = CommandLineUtils.parse_sample_input_pubsub()

received_count = 0
received_all_event = threading.Event()

def read_endpoint_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

endpoint = read_endpoint_from_file(cmdData.input_endpoint)

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")

# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"Connection resumed. return_code: {return_code}, session_present: {session_present}")

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()
        
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe results: {resubscribe_results}")

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=endpoint,
    port=cmdData.input_port,
    cert_filepath=cmdData.input_cert,
    pri_key_filepath=cmdData.input_key,
    ca_filepath=cmdData.input_ca,
    on_connection_interrupted=on_connection_interrupted,
    on_connection_resumed=on_connection_resumed,
    client_id=cmdData.input_clientId,
    clean_session=False,
    keep_alive_secs=30)

print(f"Connecting to {endpoint} with client ID '{cmdData.input_clientId}'...")
connect_future = mqtt_connection.connect()
connect_future.result()
print("Connected!")

def read_rfid():
    try:
        while True:
            try:
                # Initialize serial connection
                ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                start_time = time.time()
                while time.time() - start_time < .75:
                    if ser.in_waiting > 0:
                        data = ser.readline().decode('utf-8', errors='ignore').strip()
                        if len(data) == 10 and all(c in string.ascii_letters + string.digits for c in data) and len(set(data)) > 1:
                            print(f"Valid RFID data: {data}")
                            publish_rfid_data(data)
                        time.sleep(0.25)  # Pause for 250ms after receiving data
            except serial.SerialException as e:
                # Print error only once
                if 'ser' not in locals() or not ser.is_open:
                    print(f"Error: {e}")
            finally:
                if 'ser' in locals() and ser.is_open:
                    ser.close()
            time.sleep(0.2)  # Small delay before reopening the serial connection
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

def publish_rfid_data(data):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = {"rfid_data": data, "timestamp": timestamp}
    message_json = json.dumps(message)
    print(f"Publishing message: {message_json}")  # Debug print
    mqtt_connection.publish(
        topic=cmdData.input_topic,
        payload=message_json,
        qos=mqtt.QoS.AT_LEAST_ONCE)
    print(f"Published: {message_json} to the topic: {cmdData.input_topic}")

if __name__ == "__main__":
    try:
        # Initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # Start reading RFID data
        read_rfid()
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up GPIO
        GPIO.cleanup()
