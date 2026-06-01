import time
import json
import random
import matplotlib.pyplot as plt

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.integral = 0
        self.previous_error = 0

    def compute(self, current_value, dt):
        error = self.setpoint - current_value
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        self.previous_error = error
        return output

class MeltPoolSimulation:
    def __init__(self, ambient_temp=25):
        self.temperature = ambient_temp
        self.ambient_temp = ambient_temp
        self.thermal_mass = 0.5  # Malzemenin ısıl eylemsizliği
        self.cooling_rate = 0.05 # Ortama ısı kaybı katsayısı

    def update(self, laser_power, dt):
        # Lazer gücü sıcaklığı artırır, ortam ise soğutur. Toz yatağındaki rastgele bozulmaları (noise) ekliyoruz.
        heat_input = laser_power * 1.2
        heat_loss = (self.temperature - self.ambient_temp) * self.cooling_rate
        noise = random.uniform(-15, 15) # Toz katmanındaki ufak düzensizlikler
        
        temp_change = (heat_input - heat_loss + noise) / self.thermal_mass * dt
        self.temperature += temp_change
        return self.temperature

# --- SİMÜLASYON KURULUMU ---
TARGET_TEMP = 1650.0  # Titanyum Ti-6Al-4V için hedeflenen erime havuzu sıcaklığı (°C)
SIMULATION_TIME = 50  # Saniye
DT = 0.1              # Zaman adımı (Zaman çözünürlüğü)

# PID Parametreleri (Bu değerlerle oynayarak sistemin overshoot/salınım tepkilerini inceleyebilirsin)
pid = PIDController(Kp=0.8, Ki=0.1, Kd=0.05, setpoint=TARGET_TEMP)
system = MeltPoolSimulation()

time_data = []
temp_data = []
power_data = []
log_data = []

print("Eklemeli İmalat (Powder-Bed) Lazer PID Kontrol Simülasyonu Başlıyor...")

# --- SİMÜLASYON DÖNGÜSÜ ---
current_time = 0
while current_time <= SIMULATION_TIME:
    # 1. Sensörden güncel sıcaklığı oku
    current_temp = system.temperature
    
    # 2. PID algoritması ile gereken lazer gücünü hesapla
    # Lazer gücünü 0 ile 500 Watt arasında sınırlandırıyoruz (Fiziksel donanım limiti)
    laser_power = pid.compute(current_temp, DT)
    laser_power = max(0, min(500, laser_power)) 
    
    # 3. Sistemi yeni lazer gücü ile güncelle
    system.update(laser_power, DT)
    
    # 4. Verileri kaydet
    time_data.append(current_time)
    temp_data.append(current_temp)
    power_data.append(laser_power)
    
    # JSON loglaması için sözlük yapısı
    log_data.append({
        "time_s": round(current_time, 2),
        "melt_pool_temp_C": round(current_temp, 2),
        "laser_power_W": round(laser_power, 2)
    })
    
    current_time += DT

# --- VERİLERİ JSON OLARAK KAYDETME ---
with open('am_sensor_logs.json', 'w') as f:
    json.dump(log_data, f, indent=4)
print("Sensör verileri 'am_sensor_logs.json' dosyasına başarıyla kaydedildi.")

# --- GRAFİK ÇİZİMİ (Birim Basamak Yanıtı / Step Response) ---
plt.figure(figsize=(12, 6))

# Sıcaklık Grafiği
plt.subplot(2, 1, 1)
plt.plot(time_data, temp_data, label='Eriyik Havuzu Sıcaklığı (°C)', color='red')
plt.axhline(y=TARGET_TEMP, color='black', linestyle='--', label='Hedef Sıcaklık (Setpoint)')
plt.title('Titanyum (Ti-6Al-4V) Eklemeli İmalat Termal PID Kontrolü')
plt.ylabel('Sıcaklık (°C)')
plt.legend()
plt.grid(True)

# Lazer Gücü Grafiği
plt.subplot(2, 1, 2)
plt.plot(time_data, power_data, label='Uygulanan Lazer Gücü (Watt)', color='blue')
plt.xlabel('Zaman (Saniye)')
plt.ylabel('Güç (W)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()