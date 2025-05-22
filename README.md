Here’s a detailed `README.md` for your project titled:

---

# 🐇 RabbitMQ\_Exchange-fanout-and-Direct

A Python-based project that demonstrates **message exchange between a Sender and Responder** using **RabbitMQ** with:

* Direct exchange (`chat_direct`)
* Protocol Buffers (`.proto`) for structured data
* Nested messages
* Custom routing keys
* Controlled message timing
* Inactivity-based shutdown

This project is designed for developers seeking **real-world examples of messaging systems**, especially in **event-driven microservices or distributed systems**.

---

## 📁 Project Overview

This project has **two Python scripts**:

1. `sender.py` — sends a specified number of structured messages (via command-line arg), one every 250ms.
2. `responder.py` — receives those messages, processes them, and sends back a structured response. Shuts down automatically after 5 seconds of inactivity.

All communication happens via **RabbitMQ** using a **direct exchange** with **two named queues**.

---

## 🧩 Technologies Used

| Component        | Details                                      |
| ---------------- | -------------------------------------------- |
| **RabbitMQ**     | Message broker (fanout & direct exchanges)   |
| **pika**         | Python client for RabbitMQ                   |
| **protobuf**     | Google's Protocol Buffers for message schema |
| **Python 3.12+** | Core language, with `threading`, `sys`, etc. |
| **venv**         | Used to isolate Python environment           |

---

## 🛠️ Setup Instructions

### 🔧 System Requirements

* Python 3.12+
* RabbitMQ installed and running on `localhost`
* `protoc` compiler (`sudo apt install protobuf-compiler`)

---

### 🐍 1. Clone and Create Virtual Environment

```bash
git clone <your_repo_url>
cd RabbitMQ_Exchange-fanout-and-Direct

python3 -m venv rabbitmq_env
source rabbitmq_env/bin/activate
```

---

### 📦 2. Install Dependencies

```bash
pip install pika protobuf --break-system-packages
```

---

### 📄 3. Define Your Protobuf Message

Create `order.proto`:

```proto
syntax = "proto3";

message Price {
  double buy = 1;
  double sell = 2;
}

message Order {
  string ticker = 1;
  int32 volume = 2;
  Price price = 3;
}
```

---

### ⚙️ 4. Compile Protobuf

```bash
protoc --python_out=. order.proto
```

This generates `order_pb2.py` — used by both `sender.py` and `responder.py`.

---

## 📜 How It Works

### 🔁 Exchange & Queues

| Exchange      | Type   | Routing Key           | Target Queue |
| ------------- | ------ | --------------------- | ------------ |
| `chat_direct` | direct | `sender.to.responder` | `q1`         |
| `chat_direct` | direct | `responder.to.sender` | `q2`         |

---

### 📨 `sender.py` Flow

```bash
python sender.py 10
```

* Takes a CLI argument (e.g. 10 messages)
* Sends each message every 250ms to `q1`
* Waits on `q2` for replies from responder
* Serializes messages using Protocol Buffers (`Order`)

Each message looks like:

```json
Order {
  ticker: "STOCK1",
  volume: 101,
  price: { buy: 121.0, sell: 126.0 }
}
```

---

### 📨 `responder.py` Flow

```bash
python responder.py
```

* Waits on `q1` for messages
* When a message is received:

  * Decodes protobuf message
  * Responds with the same message to `q2`
* If **no message is received for 5 seconds**, shuts down automatically

This uses a `threading.Timer` to manage idle shutdown:

```python
shutdown_timer = threading.Timer(5.0, shutdown)
shutdown_timer.start()
```

---

## ⚙️ Design Complexity & Highlights

| Feature                         | Description                                                          |
| ------------------------------- | -------------------------------------------------------------------- |
| **Nested Protobuf Messages**    | Demonstrates real-world structuring (`Order → Price`)                |
| **Direct Exchange Routing**     | Routing keys used to direct traffic between services                 |
| **Controlled Send Rate**        | Uses `time.sleep(0.25)` to space out messages                        |
| **CLI-Controlled Sender**       | You specify how many messages to send (`python sender.py 10`)        |
| **Inactivity Timeout**          | Responder shuts down cleanly after 5 seconds of no incoming messages |
| **Try-Except-Finally Handling** | Graceful shutdown on Ctrl+C or connection failure                    |
| **Environment Isolation**       | Uses `venv` for clean dependency management                          |

---

## 📂 Folder Structure

```
RabbitMQ_Exchange-fanout-and-Direct/
│
├── rabbitmq_env/              ← Virtual environment
├── sender.py                  ← Sends protobuf-encoded messages
├── responder.py               ← Processes messages, sends back response
├── order.proto                ← Protobuf schema definition
├── order_pb2.py               ← Generated Python classes from proto
├── requirements.txt           ← (Optional) Dependency list
└── README.md                  ← This file
```

---

## 🚀 Example Run

### In Terminal 1:

```bash
python responder.py
```

### In Terminal 2:

```bash
python sender.py 5
```

Expected Output:

```
[x] Sent Order 1: ticker: "STOCK0" volume: 100 ...
[x] Received response: ticker: "STOCK0" ...
...
```

---

## ✅ Future Extensions (Optional Ideas)

* Add message IDs or timestamps
* Introduce `auto_ack=False` with manual acknowledgments
* Log all received/sent messages to a file
* Convert into a full-duplex chat system
* Use `fanout` exchange to broadcast to multiple responders

---

## 📚 Learnings

* Master asynchronous communication
* Learn RabbitMQ's direct exchange and routing
* Use Protocol Buffers for compact, structured data
* Understand timer-based graceful shutdown logic
* Learn Python's threading and exception handling

---

## 💬 Need Help?

Open an issue or reach out via discussions if you're trying to:

* Deploy this in Docker
* Add metrics/monitoring
* Integrate with web APIs

