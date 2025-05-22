import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare topic exchange
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

# Sample routing keys
routing_keys = ['sensor.india.temp', 'sensor.india.pressure', 'sensor.usa.humidity']

for key in routing_keys:
    message = f"Message for {key}"
    channel.basic_publish(exchange='topic_logs', routing_key=key, body=message)
    print(f"[x] Sent {key}: {message}")

connection.close()
