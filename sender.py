import pika
import time
import sys
import order_pb2

# Read command-line arg (number of messages)
if len(sys.argv) != 2:
    print("Usage: python3 sender.py <number_of_messages>")
    sys.exit(1)

num_messages = int(sys.argv[1])

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='chat_direct', exchange_type='direct')
channel.queue_declare(queue='q1')
channel.queue_bind(exchange='chat_direct', queue='q1', routing_key='sender.to.responder')

channel.queue_declare(queue='q2')
channel.queue_bind(exchange='chat_direct', queue='q2', routing_key='responder.to.sender')

def create_order(i):
    order = order_pb2.Order()
    order.ticker = f"STOCK{i}"
    order.volume = 100 + i
    order.price.buy = 120.0 + i
    order.price.sell = 125.0 + i
    return order

# Send messages
for i in range(num_messages):
    order = create_order(i)
    message = order.SerializeToString()
    channel.basic_publish(exchange='chat_direct', routing_key='sender.to.responder', body=message)
    print(f"[x] Sent Order {i+1}: {order}")
    time.sleep(0.25)

print("[x] All messages sent. Waiting for responses...")

# Receive all responses (optional: wait for some or just exit)
def callback(ch, method, properties, body):
    order = order_pb2.Order()
    order.ParseFromString(body)
    print("[x] Received response:", order)

channel.basic_consume(queue='q2', on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    pass
finally:
    connection.close()
