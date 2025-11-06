import pandas as pd
import numpy as np
import warnings
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import sys

# --- 0. Sürdürülebilirlik Sabitleri (Araştırma Sonuçları) ---
# 1 kWh elektrik üretimi için ortalama CO2 salınımı (kg)
CO2_PER_KWH = 0.475
# Yetişkin bir ağacın 1 yılda emdiği ortalama CO2 (kg)
CO2_PER_TREE_YEAR = 22.0
# Ortalama bir binek aracın 1 km'de saldığı CO2 (kg)
CO2_PER_CAR_KM = 0.18

warnings.filterwarnings('ignore')


# --- 1. Veri Yükleme Fonksiyonu ---
def load_and_prep_data(file_path='household_power_consumption.txt'):
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
        return df_daily
    except FileNotFoundError:
        print(f"HATA: '{file_path}' dosyası bulunamadı. Lütfen kontrol edin.")
        return None
    except Exception as e:
        print(f"Veri yükleme hatası: {e}")
        return None


# --- 2. LSTM için Dizi Oluşturma Fonksiyonu ---
def create_sequences(dataset, look_back=7):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
    return np.array(dataX)  # Sadece X (girdi) döndürür, çünkü tahmin yapacağız


# --- ANA PROJE MOTORU ---
def run_eco_save_analysis():
    print("ECO-SAVE Analiz Motoru Başlatıldı...")

    # 1. Veriyi Yükle
    df_daily = load_and_prep_data()
    if df_daily is None:
        return

    print(f"Toplam {len(df_daily)} günlük veri yüklendi.")

    # 2. Modeli Yükle
    try:
        model = load_model('lstm_model.h5')
        print("Eğitilmiş LSTM modeli 'lstm_model.h5' başarıyla yüklendi.")
    except (IOError, ImportError):
        print("\n--- KRİTİK HATA ---")
        print("Kaydedilmiş model 'lstm_model.h5' bulunamadı.")
        print("Lütfen önce 'dl_analiz.py' (güncellenmiş) kodunu çalıştırıp modeli kaydettiğinizden emin olun.")
        return

    # 3. Tahmin için Veriyi Hazırla (Tüm veri üzerinden yapacağız)
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset_scaled = scaler.fit_transform(df_daily.values.reshape(-1, 1))

    look_back = 7
    dataX = create_sequences(dataset_scaled, look_back)
    dataX = np.reshape(dataX, (dataX.shape[0], dataX.shape[1], 1))

    # 4. Tahminleri Yap
    print("Model, veri seti üzerinde tahminler yapıyor...")
    predictions_scaled = model.predict(dataX)

    # Tahminleri geri ölçekle (kWh değerine dönüştür)
    predictions = scaler.inverse_transform(predictions_scaled)

    # Gerçek verileri de (kayma olmadan) al
    actuals = df_daily.values[look_back + 1:]
    dates = df_daily.index[look_back + 1:]

    # Hata payımızı biliyoruz (RMSE ~405 kWh)
    ANOMALY_THRESHOLD = 405.0 * 2.5  # Ortalama hatanın 2.5 katı

    # --- 5. SÜRDÜRÜLEBİLİRLİK ÖZELLİKLERİ ---

    print("\n" + "=" * 50)
    print("   ECO-SAVE SÜRDÜRÜLEBİLİRLİK RAPORU")
    print("=" * 50)

    # --- ÖZELLİK 1: ANOMALİ TESPİTİ ---
    print("\n### ÖZELLİK 1: ANOMALİ TESPİT SİSTEMİ ###")
    anomalies_found = 0
    for i in range(len(predictions)):
        error = actuals[i] - predictions[i][0]
        if error > ANOMALY_THRESHOLD:
            anomalies_found += 1
            print(f"  [UYARI] {dates[i].date()}: ANORMAL TÜKETİM!")
            print(f"    > Tahmin Edilen: {predictions[i][0]:.2f} kWh")
            print(f"    > Gerçekleşen:  {actuals[i]:.2f} kWh")
            print(f"    > Fark (Anomali): {error:.2f} kWh\n")

    if anomalies_found == 0:
        print("  > Analiz edilen periyotta belirgin bir anomali tespit edilmedi.")
    else:
        print(f"  > Toplam {anomalies_found} anormal tüketim günü bulundu.")

    # --- ÖZELLİK 2: EKOLOJİK ÖNERİ MOTORU ---
    print("\n### ÖZELLİK 2: KİŞİSELLEŞTİRİLMİŞ EKOLOJİK ÖNERİ ###")

    overall_mean_kwh = actuals.mean()
    last_30_days_mean_kwh = actuals[-30:].mean()

    print(f"  > Tüm zamanlar günlük ortalamanız: {overall_mean_kwh:.2f} kWh")
    print(f"  > Son 30 gün ortalamanız:        {last_30_days_mean_kwh:.2f} kWh")

    if last_30_days_mean_kwh > overall_mean_kwh * 1.1:
        print("  > DURUM: Son 30 gündür genel ortalamanızın üzerindesiniz.")
    else:
        print("  > DURUM: Tüketiminiz kontrol altında. Tebrikler!")

    # %10 Tasarruf potansiyeli (Aylık)
    potential_saving_kwh_monthly = (last_30_days_mean_kwh * 0.10) * 30
    potential_saving_co2_monthly = potential_saving_kwh_monthly * CO2_PER_KWH

    print(f"\n  > EKOLOJİK HEDEF: Mevcut tüketiminizi sadece %10 azaltarak,")
    print(f"    aylık {potential_saving_kwh_monthly:.2f} kWh tasarruf edebilirsiniz.")
    print(f"    Bu tasarruf, {potential_saving_co2_monthly:.2f} kg CO2 salınımını önlemeye eşdeğerdir.")

    # --- ÖZELLİK 3: OYUNLAŞTIRMA (EKOLOJİK ETKİ) ---
    print("\n### ÖZELLİK 3: TASARRUFUNUZUN ANLAMI (OYUNLAŞTIRMA) ###")

    tree_equivalent = potential_saving_co2_monthly / (CO2_PER_TREE_YEAR / 12)  # Aylık ağaç eşdeğeri
    car_km_equivalent = potential_saving_co2_monthly / CO2_PER_CAR_KM

    print(f"  > Önleyeceğiniz {potential_saving_co2_monthly:.2f} kg CO2 salınımı şu anlama gelir:")
    print(f"    * {tree_equivalent:.1f} yetişkin ağacın 1 AYDA emdiği CO2 miktarı.")
    print(f"    * Ortalama bir aracın {car_km_equivalent:.1f} km'de yaptığı salınım.")
    print("\n" + "=" * 50)
    print("ECO-SAVE Analizi Tamamlandı.")


# --- Projeyi Çalıştır ---
if __name__ == "__main__":
    run_eco_save_analysis()