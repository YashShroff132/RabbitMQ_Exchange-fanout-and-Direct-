import pika
import order_pb2
import threading
import time

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='chat_direct', exchange_type='direct')
channel.queue_declare(queue='q1')
channel.queue_bind(exchange='chat_direct', queue='q1', routing_key='sender.to.responder')

channel.queue_declare(queue='q2')
channel.queue_bind(exchange='chat_direct', queue='q2', routing_key='responder.to.sender')

# Shutdown timer
shutdown_timer = None

def reset_shutdown_timer():
    global shutdown_timer
    if shutdown_timer:
        shutdown_timer.cancel()
    shutdown_timer = threading.Timer(10.0, shutdown)
    shutdown_timer.start()

def shutdown():
    print("[x] No messages for 10 seconds. Shutting down.")
    connection.close()
    exit()

def callback(ch, method, properties, body):
    reset_shutdown_timer()
    order = order_pb2.Order()
    order.ParseFromString(body)
    print(f"[x] Received Order: {order}")

    # Echo response back
    channel.basic_publish(
        exchange='chat_direct',
        routing_key='responder.to.sender',
        body=order.SerializeToString()
    )
    print("[x] Sent response back.")

reset_shutdown_timer()
channel.basic_consume(queue='q1', on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except Exception as e:
    print("Exception occurred:", e)
finally:
    if shutdown_timer:
        shutdown_timer.cancel()
    connection.close()
