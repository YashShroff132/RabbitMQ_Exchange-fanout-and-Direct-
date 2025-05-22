import pika
import time
import sys
import datetime
import order_pb2
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timezone
import random

if len(sys.argv) != 3:
    print("Usage: python3 sender.py <number_of_messages> <type: order|trade|mixed>")
    sys.exit(1)

num_messages = int(sys.argv[1])
mode = sys.argv[2].lower()

if mode not in ['order', 'trade', 'mixed']:
    print("Invalid type. Choose: order, trade, or mixed.")
    sys.exit(1)

received_count = 0

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
    order.created_at.FromDatetime(datetime.now(timezone.utc))
    return order

def create_trade(i):
    trade = order_pb2.Trade()
    trade.trade_id = f"TRD-{i}"
    trade.trade_price = 130.0 + i
    trade.trade_quantity = 50 + i
    trade.trade_time.FromDatetime(datetime.now(timezone.utc))
    return trade

# Send messages
for i in range(num_messages):
    envelope = order_pb2.Envelope()

    message_type = mode
    if mode == "mixed":
        message_type = random.choice(["order", "trade"])

    if message_type == "order":
        envelope.order.CopyFrom(create_order(i))
        print(f"[x] Sent Order {i+1}: {envelope.order}")
    else:
        envelope.trade.CopyFrom(create_trade(i))
        print(f"[x] Sent Trade {i+1}: {envelope.trade}")

    message = envelope.SerializeToString()
    channel.basic_publish(exchange='chat_direct', routing_key='sender.to.responder', body=message)
    time.sleep(0.25)

print("[x] All messages sent. Waiting for responses...")

# Callback to count received responses
def callback(ch, method, properties, body):
    global received_count
    envelope = order_pb2.Envelope()
    envelope.ParseFromString(body)

    if envelope.HasField("order"):
        print(f"[x] Received response {received_count + 1}: Order - {envelope.order}")
    elif envelope.HasField("trade"):
        print(f"[x] Received response {received_count + 1}: Trade - {envelope.trade}")

    received_count += 1

    if received_count == num_messages:
        print("[x] All responses received. Closing connection.")
        channel.stop_consuming()

channel.basic_consume(queue='q2', on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
finally:
    connection.close()
