import paho.mqtt.client as mqtt
import json
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Biến toàn cục lưu dữ liệu từ MQTT và trạng thái
mqtt_data = {
    "date": "N/A",
    "time": "N/A",
    "data": "No data received"
}
updated_status = "No status updated yet"  # Biến lưu trạng thái đã cập nhật

# Cấu hình MQTT
broker = "192.168.0.103"
port = 1883
topic = "MQTT_DongCo_DCs"


# Hàm callback khi nhận được tin nhắn
def on_message(client, userdata, msg):
    global mqtt_data
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        print(data)
        mqtt_data["date"] = data.get("date", "N/A")
        mqtt_data["time"] = data.get("time", "N/A")
        mqtt_data["data"] = data.get("status", "N/A")
    except json.JSONDecodeError:
        print("Lỗi: Dữ liệu không phải là JSON hợp lệ")
    except Exception as e:
        print(f"Lỗi khác: {e}")


# Khởi tạo MQTT client
def start_mqtt():
    try:
        client = mqtt.Client(protocol=mqtt.MQTTv311)  # Đảm bảo sử dụng phiên bản MQTTv3.1.1
        client.on_message = on_message  # Gán callback cho message

        # Kết nối và đăng ký chủ đề
        client.connect(broker, port, 60)
        client.subscribe(topic)

        # Lắng nghe tin nhắn
        client.loop_forever()
    except Exception as e:
        print(f"Lỗi trong luồng MQTT: {e}")


# API endpoint để cung cấp dữ liệu MQTT mới nhất
@app.route("/get_mqtt_data", methods=["GET"])
def get_mqtt_data():
    global mqtt_data
    return jsonify(mqtt_data)


# Endpoint chính để hiển thị dữ liệu trên web và xử lý form
@app.route("/", methods=["GET", "POST"])
def index():
    global mqtt_data, updated_status
    if request.method == "POST":
        new_status = request.form["status"]
        updated_status = f"Trạng thái đã được cập nhật: {new_status}"

        # Cập nhật trạng thái dữ liệu của MQTT
        mqtt_data["data"] = new_status

        # Gửi dữ liệu cập nhật qua MQTT (nếu cần)
        mqtt_client.publish(topic, json.dumps(mqtt_data))

    return render_template("index.html", mqtt_data=mqtt_data, updated_status=updated_status)


if __name__ == "__main__":
    # Chạy MQTT trong luồng riêng
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Chạy Flask
    app.run(host="0.0.0.0", port=5000)
