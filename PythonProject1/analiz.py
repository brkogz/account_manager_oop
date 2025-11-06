import pandas as pd
import warnings
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import numpy as np

# Uyarıları bastıralım
warnings.filterwarnings('ignore')

# --- Adım 1: Veri Yükleme ve Hazırlama (LSTM ile aynı) ---

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

# --- Adım 2: Train ve Test Olarak Ayırma (LSTM ile aynı) ---

# Veriyi aynı %80 / %20 oranında ayırıyoruz
train_size = int(len(df_daily) * 0.80)
train_data, test_data = df_daily[0:train_size], df_daily[train_size:len(df_daily)]

print(f"Eğitim için {len(train_data)} gün, Test için {len(test_data)} gün veri ayrıldı.")
print("--- Klasik ML (ARIMA) Modeli Eğitimi Başlıyor ---")
# Bu işlem, LSTM'den daha hızlı olabilir.

# --- Adım 3: ARIMA Modeli Oluşturma, Eğitme ve Tahmin ---

try:
    # 3.1. Modeli EĞİTİM VERİSİ (train_data) üzerinde eğit
    model = ARIMA(train_data, order=(1, 1, 1))  # Demo için (1,1,1) kullanıyoruz
    model_fit = model.fit()

    print("ARIMA modeli başarıyla eğitildi.")

    # 3.2. Tahmin yap
    # Başlangıç ve bitiş noktalarını belirle
    start = len(train_data)
    end = len(train_data) + len(test_data) - 1

    # Test seti için tahminleri oluştur
    predictions = model_fit.predict(start=start, end=end, dynamic=False, typ='levels')

    # Bazen predict() fonksiyonu index isimlerini farklı verebilir,
    # karşılaştırma için test_data'nın index'ini kullanalım
    predictions.index = test_data.index

    # 3.3. Performansı Hesaplama (RMSE)
    test_rmse = np.sqrt(mean_squared_error(test_data, predictions))

    print("\n--- ARIMA MODELİ PERFORMANSI (RMSE) ---")
    print(f"Test Seti RMSE: {test_rmse:.2f} kWh")
    print("------------------------------------------")


except Exception as e:
    print(f"ARIMA modeli hatası: {e}")