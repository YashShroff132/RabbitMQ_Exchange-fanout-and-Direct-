import pika
import sys

binding_keys = ['sensor.india.*']  # Or ['sensor.#'] to receive all

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

# Declare a temporary queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind the queue to the exchange using binding keys
for key in binding_keys:
    channel.queue_bind(exchange='topic_logs', queue=queue_name, routing_key=key)

print(f"[*] Waiting for logs with keys: {binding_keys}")

def callback(ch, method, properties, body):
    print(f"[x] Received {method.routing_key}: {body.decode()}")

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
