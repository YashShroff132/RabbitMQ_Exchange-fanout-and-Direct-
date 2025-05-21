import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='chat_direct', exchange_type='direct')

# Declare and bind queues with routing keys
channel.queue_declare(queue='q1')
channel.queue_bind(exchange='chat_direct', queue='q1', routing_key='sender.to.responder')

channel.queue_declare(queue='q2')
channel.queue_bind(exchange='chat_direct', queue='q2', routing_key='responder.to.sender')


msg = "Hello from sender!"
channel.basic_publish(exchange='chat_direct', routing_key='sender.to.responder', body=msg)
print(" Sent this :", msg)

# Listen for reply
def callback(ch, method, properties, body):
    print(" Received from responder:", body.decode())
    connection.close()

channel.basic_consume(queue='q2', on_message_callback=callback, auto_ack=True)
print("[*] Waiting for response...")
channel.start_consuming()
