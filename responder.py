import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='chat_direct', exchange_type='direct')


channel.queue_declare(queue='q1')
channel.queue_bind(exchange='chat_direct', queue='q1', routing_key='sender.to.responder')

channel.queue_declare(queue='q2')
channel.queue_bind(exchange='chat_direct', queue='q2', routing_key='responder.to.sender')

# Listen to sender messages
def callback(ch, method, properties, body):
    msg = body.decode()
    print(" Received this from sender:", msg)

    reply = f"Responder got: {msg}"
    channel.basic_publish(exchange='chat_direct', routing_key='responder.to.sender', body=reply)
    print(" Replied to sender.")

channel.basic_consume(queue='q1', on_message_callback=callback, auto_ack=True)
print("[*] Waiting for message from sender...")
channel.start_consuming()
