import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

warnings.filterwarnings('ignore')

# --- Adım 1: Veri Yükleme ve Hazırlama ---

print("Veri seti yükleniyor...")
file_path = 'household_power_consumption.txt'
df_daily = None

try:
    df = pd.read_csv(
        file_path,
        sep=';',
        low_memory=False,
        na_values=['?']
    )
    df.dropna(inplace=True)
    df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
    df.set_index('datetime', inplace=True)
    df['Global_active_power'] = pd.to_numeric(df['Global_active_power'])
    df_daily = df['Global_active_power'].resample('D').sum()
    df_daily = df_daily.fillna(0)
    print(f"Toplam {len(df_daily)} günlük veri analiz için hazır.")

except Exception as e:
    print(f"Veri yükleme hatası: {e}")
    exit()

# --- Adım 2: Derin Öğrenme için Veri Ön İşleme ---
scaler = MinMaxScaler(feature_range=(0, 1))
dataset = scaler.fit_transform(df_daily.values.reshape(-1, 1))

train_size = int(len(dataset) * 0.80)
test_size = len(dataset) - train_size
train_data, test_data = dataset[0:train_size, :], dataset[train_size:len(dataset), :]

def create_sequences(dataset, look_back=7):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)

look_back = 7
trainX, trainY = create_sequences(train_data, look_back)
testX, testY = create_sequences(test_data, look_back)

trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1], 1))
testX = np.reshape(testX, (testX.shape[0], testX.shape[1], 1))

# --- Adım 3: LSTM Modeli Oluşturma ve Eğitme ---
print("\n--- Derin Öğrenme (LSTM) Modeli Eğitimi Başlıyor ---")
model = Sequential()
model.add(LSTM(50, input_shape=(look_back, 1)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(trainX, trainY, epochs=20, batch_size=32, verbose=2)
print("--- Model Eğitimi Tamamlandı ---")

# --- ADIM 4: MODELİ KAYDETME ---
model.save('lstm_model.h5')
print("\n*** Model başarıyla 'lstm_model.h5' dosyasına kaydedildi. ***")

print("Analiz Tamamlandı. Artık 'proje_main.py' dosyasını çalıştırabilirsiniz.")