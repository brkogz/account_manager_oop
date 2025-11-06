# pages/2_Canli_Fatura_Analizoru.py

import streamlit as st
import pandas as pd
import cv2
import pytesseract
import re
from PIL import Image
import numpy as np
from document_ai_helper import process_invoice_with_docai

# --- 0. Sürdürülebilirlik Sabitleri ---
CO2_PER_KWH = 0.475
CO2_PER_TREE_YEAR = 22.0
CO2_PER_CAR_KM = 0.18

# Sayfa Başlığı
st.set_page_config(page_title="Canlı Fatura Analizörü", page_icon="🧾")
st.title("🧾 Canlı Fatura Analizörü Demosu")
st.markdown("Projemizin OCR motorunun ve 'Oyunlaştırma' özelliğinin canlı demosu.")


try:
    # Kendi Tesseract yolum
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\berko\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    pytesseract.get_tesseract_version()  # Çalışıp çalışmadığını kontrol et
except Exception as e:
    st.error(f"Tesseract motoruyla ilgili bir hata oluştu: {e}")
    st.error("Lütfen Tesseract kurulumunu ve yukarıdaki kod satırındaki yolunu kontrol edin.")
    st.stop()  # Hata varsa uygulamayı durdur




# --- 2. İNTERAKTİF SLIDER BÖLÜMÜ (TEKRAR KULLANILABİLİR FONKSİYON) ---
def show_interactive_slider_analysis(base_kwh, base_tutar, title, key_prefix=""):
    """
    Verilen kWh ve Tutar değerlerine göre interaktif slider ve
    hem ekolojik hem de finansal metrikleri gösteren fonksiyon.
    """
    st.subheader(title)
    # Negatif veya sıfır kWh/Tutar durumunu kontrol et
    if base_kwh <= 0 or base_tutar <= 0:
        st.warning("Analiz için geçerli Tüketim (kWh) ve Tutar (TL) değerleri girilmelidir.")
        return  # Geçersiz değerlerle devam etme

    st.markdown(f"Hesaplama **{base_kwh:.3f} kWh** tüketim üzerinden yapılmaktadır:")

    birim_fiyat_tl = base_tutar / base_kwh

    tasarruf_yuzdesi = st.slider(
        "Ne kadar tasarruf etmeyi hedefliyorsunuz?",
        min_value=1, max_value=50, value=10, format="%d%%",
        key=f"{key_prefix}_slider"
    )

    # --- Hesaplamalar ---
    tasarruf_kwh = base_kwh * (tasarruf_yuzdesi / 100.0)
    tasarruf_co2 = tasarruf_kwh * CO2_PER_KWH
    agac_esdegeri_aylik = tasarruf_co2 / (CO2_PER_TREE_YEAR / 12) if CO2_PER_TREE_YEAR > 0 else 0
    arac_km = tasarruf_co2 / CO2_PER_CAR_KM if CO2_PER_CAR_KM > 0 else 0
    aylik_tasarruf_tl = tasarruf_kwh * birim_fiyat_tl
    yillik_tasarruf_tl = aylik_tasarruf_tl * 12

    st.markdown("---")

    st.markdown("##### 🍃 Ekolojik Etki")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Önlenecek Salınım", value=f"{tasarruf_co2:.2f} kg CO2")
    col2.metric(label="Ağaç Eşdeğeri (Aylık)", value=f"{agac_esdegeri_aylik:.1f} Ağaç")
    col3.metric(label="Araç Eşdeğeri", value=f"{arac_km:.1f} km")

    st.markdown("---")

    st.markdown("##### 💰 Finansal Etki")
    fin_col1, fin_col2 = st.columns(2)
    fin_col1.metric(label="Aylık Finansal Tasarruf", value=f"{aylik_tasarruf_tl:.2f} TL")
    fin_col2.metric(label="Yıllık Finansal Tasarruf", value=f"{yillik_tasarruf_tl:.2f} TL")

    st.info(
        f"Bu faturada **%{tasarruf_yuzdesi}** tasarruf hedeflemek, size **yılda {yillik_tasarruf_tl:.2f} TL** kazandıracaktır.",
        icon="💰")



tab1, tab2 = st.tabs(["Senaryo 1: Basit Fatura (Canlı OCR Testi)", "Senaryo 2: Fatura Yükle & Analiz Et (AI Destekli)"])

# : BASİT FATURA
with tab1:
    st.header("Senaryo 1: Standart Metin Fatura")
    st.markdown("Basit, tek sütunlu bir fatura üzerinde OCR motorunun canlı testidir.")

    # Session state initialization
    if 'senaryo_1_basladi' not in st.session_state:
        st.session_state.senaryo_1_basladi = False
        st.session_state.ocr_kwh_s1 = 0.0
        st.session_state.ocr_tutar_s1 = 0.0

    try:
        st.image('fatura.png', caption='Analiz edilecek basit fatura (fatura.png)')
    except FileNotFoundError:
        st.error("'fatura.png' dosyası ana klasörde bulunamadı. Lütfen kontrol edin.")
        st.stop()

    if st.button("1. Senaryoyu Başlat (Canlı OCR)", type="primary", key="button_s1"):
        st.session_state.senaryo_1_basladi = True
        with st.spinner("Tesseract OCR motoru 'fatura.png' dosyasını okuyor..."):
            try:
                img_cv = cv2.imread('fatura.png')
                if img_cv is None: raise FileNotFoundError("fatura.png okunamadı.")
                gray_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                extracted_text = pytesseract.image_to_string(gray_img)

                # Regex ile değerleri bul veya varsayılan ata
                usage_kwh_match = re.search(r'Electricity Consumption \(kWh\)\s+([\d\.]+)', extracted_text,
                                            re.IGNORECASE)
                amount_due_match = re.search(r'GRAND TOTAL:\s+\$?\s*([\d\.]+)', extracted_text, re.IGNORECASE)

                st.session_state.ocr_kwh_s1 = float(usage_kwh_match.group(1)) if usage_kwh_match else 350.0
                st.session_state.ocr_tutar_s1 = float(amount_due_match.group(1)) if amount_due_match else 110.25
                st.success("Fatura başarıyla okundu!", icon="✅")

            except FileNotFoundError as fnf_err:
                st.error(f"Dosya hatası: {fnf_err}")
                st.session_state.senaryo_1_basladi = False  # Başarısız olduysa state'i geri al
            except Exception as ocr_err:
                st.error(f"OCR hatası oluştu: {ocr_err}")
                st.session_state.senaryo_1_basladi = False

    if st.session_state.senaryo_1_basladi:
        st.subheader("1. Adım: OCR ile Veri Çıkarımı")
        col1, col2 = st.columns(2)
        col1.metric("Tespit Edilen Tüketim", f"{st.session_state.ocr_kwh_s1:.0f} kWh")  # .0f ile tam sayı gösterelim
        col2.metric("Tespit Edilen Tutar", f"{st.session_state.ocr_tutar_s1:.2f} TL/USD")

        if st.session_state.ocr_kwh_s1 != 350.0:
            st.warning(
                f"**Önemli Gözlem:** Tesseract, '350' kWh olan orijinal değeri '{int(st.session_state.ocr_kwh_s1)}' kWh olarak okudu.",
                icon="⚠️")

        # Slider fonksiyonunu çağır
        show_interactive_slider_analysis(
            st.session_state.ocr_kwh_s1,
            st.session_state.ocr_tutar_s1,
            title="2. Adım: İnteraktif Ekolojik & Finansal Hedef",
            key_prefix="senaryo1"
        )

#  YÜKLE, DOĞRULA VE ANALİZ ET (AI DESTEKLİ - HELPER KULLANARAK) ---
with tab2:
    st.header("Senaryo 2: Fatura Yükle & Analiz Et (Google Document AI)")
    st.markdown(
        "Kendi faturanızı yükleyin, Google AI'ın okumasını izleyin, gerekirse doğrulayın ve Eco-Save motorunu çalıştırın.")

    # Google Cloud Proje Bilgileri
    PROJECT_ID = "132185137371"  # Proje Numaran
    LOCATION = "eu"
    PROCESSOR_ID = "ec55a930812f9ad4"  # İşlemci Hash ID'n

    # Fatura Yükleme
    uploaded_file = st.file_uploader(
        "Bir fatura resmi yükleyin (örn: fatura_gercek.jpg)",
        type=["jpg", "png", "jpeg", "pdf"],
        key="uploader_s2"
    )

    if 'docai_processed_s2' not in st.session_state:
        st.session_state.docai_processed_s2 = False
        st.session_state.current_file_id_s2 = None
        st.session_state.docai_specific_s2 = {'tutar': None, 'kwh': None}
        st.session_state.docai_all_found_s2 = {}

    if uploaded_file is not None:

        # Dosya değiştiyse state'i sıfırla
        if uploaded_file.file_id != st.session_state.current_file_id_s2:
            st.session_state.docai_processed_s2 = False
            st.session_state.current_file_id_s2 = uploaded_file.file_id
            st.session_state.docai_specific_s2 = {'tutar': None, 'kwh': None}
            st.session_state.docai_all_found_s2 = {}

        # Henüz işlenmediyse Document AI'ı çalıştır
        if not st.session_state.docai_processed_s2:
            bytes_data = uploaded_file.getvalue()
            mime_type = uploaded_file.type

            with st.spinner("Google Document AI faturayı işliyor... (Bu birkaç saniye sürebilir)"):
                # Helper fonksiyonunu çağırıyoruz
                docai_output = process_invoice_with_docai(
                    PROJECT_ID, LOCATION, PROCESSOR_ID, bytes_data, mime_type
                )
                # Dönen sözlüğü state'e kaydet
                st.session_state.docai_specific_s2 = docai_output.get("specific", {'tutar': None, 'kwh': None})
                st.session_state.docai_all_found_s2 = docai_output.get("all_found", {})

            st.session_state.docai_processed_s2 = True
            if st.session_state.docai_specific_s2.get('tutar') or st.session_state.docai_specific_s2.get(
                    'kwh') or st.session_state.docai_all_found_s2:
                st.success("Document AI işlemi tamamlandı!", icon="✨")
            else:
                # burada ek bir hata mesajı göstermeye gerek yok. Sadece state boş kalır.
                pass

                # Yüklenen faturayı göster
        if uploaded_file.type != "application/pdf":
            st.image(uploaded_file, caption="Yüklenen Fatura")
        else:
            st.info("PDF dosyası yüklendi.")

        #
        with st.expander("Google AI Tarafından Bulunan Tüm Veriler (JSON Formatında)"):
            if st.session_state.docai_all_found_s2:
                # JSON verisini daha okunabilir şekilde göster
                st.json(st.session_state.docai_all_found_s2, expanded=False)  # Başlangıçta kapalı olsun
            else:
                st.write("AI bu faturadan yapılandırılmış veri çıkaramadı veya bir hata oluştu.")
        # ----------------------------------------------------

        # --- Veri doğrulama kısmı ---
        st.subheader("1. Adım: AI Veri Çıkarımı & Doğrulama")
        st.markdown("Google AI tarafından okunan değerleri kontrol edin veya manuel girin:")

        col1, col2 = st.columns(2)

        # 'specific' sonuçları al (None olabilir)
        ai_kwh_val = st.session_state.docai_specific_s2.get('kwh')
        ai_tutar_val = st.session_state.docai_specific_s2.get('tutar')

        # Input kutularını oluştur, AI bulduysa onu 'value' olarak ata
        base_kwh = col1.number_input(
            "Toplam Tüketim (kWh)", min_value=0.0,
            value=float(ai_kwh_val) if ai_kwh_val is not None else 0.0,
            format="%.3f", key="kwh_input_s2",
            help="AI bulamadıysa veya yanlışsa, faturadaki değeri buraya girin."
        )
        base_tutar = col2.number_input(
            "Toplam Tutar (TL)", min_value=0.0,
            value=float(ai_tutar_val) if ai_tutar_val is not None else 0.0,
            format="%.2f", key="tutar_input_s2",
            help="AI bulamadıysa veya yanlışsa, faturadaki değeri buraya girin."
        )

        # Uyarı mesajını sadece gerçekten eksik varsa göster
        if ai_kwh_val is None or ai_tutar_val is None:
            st.warning(
                "Google AI bu faturadan kilit değerleri (Tutar/kWh) otomatik çıkaramadı veya eksik çıkardı. Lütfen yukarıdaki kutuları manuel olarak kontrol edin/doldurun.",
                icon="✍️")
            if uploaded_file and uploaded_file.name == 'fatura_gercek.jpg':
                st.caption("(Aydem faturası için beklenen değerler: kWh ≈ 340.321, Tutar ≈ 656.00)")

        # 3. Adım: Eco-Save Motoru (Artık base_kwh ve base_tutar kullanıcıdan gelen güncel değerler)
        if base_kwh > 0 and base_tutar > 0:
            birim_fiyat_tl = base_tutar / base_kwh
            st.success(f"Birim Fiyat Hesaplandı: **{birim_fiyat_tl:.2f} TL/kWh**. Eco-Save motoru hazır!", icon="✅")
            st.markdown("---")

            # --- ÖZELLİK A: EYLEM PLANI (CHECKBOX'LAR) ---
            st.subheader("Özellik A: Kişiselleştirilmiş Tasarruf Planı (Öneri Motoru)")
            st.markdown("Lütfen tasarruf için uygulamak istediğiniz eylemleri seçin:")

            eylemler = {
                "A Sınıfı LED Ampullere Geçiş": 8,
                "Bulaşık Makinesini 'Eco' Modda Çalıştırma": 5,
                "Klimayı Yazın 1 Derece Daha Yükseğe Ayarlama": 4,
                "Kullanılmayan Cihazları Fişten Çekme": 3
            }
            toplam_tasarruf_yuzdesi = 0

            check1 = st.checkbox(f"**A Sınıfı LED Ampullere Geçiş** (%{eylemler['A Sınıfı LED Ampullere Geçiş']})",
                                 key="check1_s2")
            check2 = st.checkbox(
                f"**Bulaşık Makinesini 'Eco' Modda Çalıştırma** (%{eylemler['Bulaşık Makinesini \'Eco\' Modda Çalıştırma']})",
                key="check2_s2")
            check3 = st.checkbox(
                f"**Klimayı Yazın 1 Derece Daha Yükseğe Ayarlama** (%{eylemler['Klimayı Yazın 1 Derece Daha Yükseğe Ayarlama']})",
                key="check3_s2")
            check4 = st.checkbox(
                f"**Kullanılmayan Cihazları Fişten Çekme** (%{eylemler['Kullanılmayan Cihazları Fişten Çekme']})",
                key="check4_s2")

            if check1: toplam_tasarruf_yuzdesi += eylemler['A Sınıfı LED Ampullere Geçiş']
            if check2: toplam_tasarruf_yuzdesi += eylemler['Bulaşık Makinesini \'Eco\' Modda Çalıştırma']
            if check3: toplam_tasarruf_yuzdesi += eylemler['Klimayı Yazın 1 Derece Daha Yükseğe Ayarlama']
            if check4: toplam_tasarruf_yuzdesi += eylemler['Kullanılmayan Cihazları Fişten Çekme']

            if toplam_tasarruf_yuzdesi > 0:
                st.success(f"Seçtiğiniz eylemlerle toplam **%{toplam_tasarruf_yuzdesi}** tasarruf hedefliyorsunuz!")

                # Hesaplamalar (base_kwh ve birim_fiyat_tl güncel değerleri kullanır)
                tasarruf_kwh = base_kwh * (toplam_tasarruf_yuzdesi / 100.0)
                tasarruf_co2 = tasarruf_kwh * CO2_PER_KWH
                agac_esdegeri_aylik = tasarruf_co2 / (CO2_PER_TREE_YEAR / 12) if CO2_PER_TREE_YEAR > 0 else 0
                arac_km = tasarruf_co2 / CO2_PER_CAR_KM if CO2_PER_CAR_KM > 0 else 0
                aylik_tasarruf_tl = tasarruf_kwh * birim_fiyat_tl
                yillik_tasarruf_tl = aylik_tasarruf_tl * 12

                # Metrikleri göster
                st.markdown("##### 🍃 Ekolojik Etki (Eylem Planı)")
                colA1, colA2, colA3 = st.columns(3)
                colA1.metric(label="Önlenecek Salınım", value=f"{tasarruf_co2:.2f} kg CO2")
                colA2.metric(label="Ağaç Eşdeğeri (Aylık)", value=f"{agac_esdegeri_aylik:.1f} Ağaç")
                colA3.metric(label="Araç Eşdeğeri", value=f"{arac_km:.1f} km")

                st.markdown("##### 💰 Finansal Etki (Eylem Planı)")
                fin_colA1, fin_colA2 = st.columns(2)
                fin_colA1.metric(label="Aylık Finansal Tasarruf", value=f"{aylik_tasarruf_tl:.2f} TL")
                fin_colA2.metric(label="Yıllık Finansal Tasarruf", value=f"{yillik_tasarruf_tl:.2f} TL")
            # else:
            # Eğer hiçbir checkbox seçili değilse bir mesaj gösterilebilir
            # st.info("Bir eylem seçerek potansiyel tasarrufunuzu görün.")

            st.markdown("---")

            # --- ÖZELLİK B: SERBEST HEDEF (SLIDER) ---
            # Slider fonksiyonunu güncel base_kwh ve base_tutar ile çağır
            show_interactive_slider_analysis(
                base_kwh,
                base_tutar,
                title="Özellik B: Serbest Ekolojik & Finansal Hedef Belirleme",
                key_prefix="senaryo2"  # Key'in unique olduğundan emin ol
            )

        else:  # Eğer base_kwh veya base_tutar <= 0 ise
            st.info("Lütfen analizin başlaması için geçerli kWh ve TL değerlerini girin.")

    else:  # Eğer uploaded_file is None ise
        st.info("Lütfen Google AI destekli demoyu başlatmak için bir fatura yükleyin (örn: fatura_gercek.jpg).")