# document_ai_helper.py (En İyi Tutar Mantığı + En İyi kWh Mantığı)

from google.cloud import documentai_v1 as documentai
import re
import streamlit as st
import traceback


def clean_turkish_number(text_value: str) -> float | None:
    """
    Türkçe sayı formatındaki (örn: '1.015,76 TL', '310,00') metni temizler
    ve float sayıya dönüştürür.
    """
    if not text_value:
        return None
    try:

        match = re.search(r'([\d.,]+)', text_value)
        if not match:
            return None

        number_str = match.group(1)

        # 1. Binlik ayraçları (.) kaldır
        no_thousands = number_str.replace('.', '')
        # 2. Ondalık virgülünü (,) noktaya çevir
        dot_decimal = no_thousands.replace(',', '.')

        # 3. Sadece rakam ve nokta kaldığından emin ol
        if re.match(r'^\d+(\.\d+)?$', dot_decimal):
            return float(dot_decimal)
        else:
            # Belki de format 1.234.56 (hatalı okuma) idi? Sadece son noktayı koru.
            parts = dot_decimal.split('.')
            if len(parts) > 1:
                cleaned_str = "".join(parts[:-1]) + "." + parts[-1]
                if re.match(r'^\d+(\.\d+)?$', cleaned_str):
                    return float(cleaned_str)
            return None

    except Exception:
        return None


def process_invoice_with_docai(project_id: str, location: str, processor_id: str, file_content: bytes,
                               mime_type: str) -> dict:
    """
    Google Document AI kullanarak fatura görüntüsünden veri çıkarır.
    Tutar: 'total_amount' VEYA Türkçe etiketleri arar ve en büyüğünü alır.
    kWh: 'line_item' VEYA 'kwh'/'tüketim' kelimelerini arar ve toplamını alır.
    """
    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}
    output = {"specific": {'tutar': None, 'kwh': None}, "all_found": {}}

    try:
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        name = client.processor_path(project_id, location, processor_id)
        raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        document = result.document

        all_entities_simple = {}
        possible_tutarlar = []  # Olası TL tutarlarını sakla
        possible_kwhs = []  # Olası kWh değerlerini sakla

        for entity in document.entities:
            field_type = entity.type_
            field_value_raw = entity.mention_text.strip()
            confidence = entity.confidence

            # Bulunan her şeyi sakla (JSON'da göstermek için)
            if field_type not in all_entities_simple:
                all_entities_simple[field_type] = []
            all_entities_simple[field_type].append({"value": field_value_raw, "confidence": f"{confidence:.2f}"})

            if 'total_amount' in field_type or 'amount_due' in field_type or \
                    any(keyword in field_value_raw.lower() for keyword in
                        ["ödenecek", "toplam tutar", "fatura tutarı", "genel toplam", "toplam ödenecek"]):

                tutar_val = clean_turkish_number(field_value_raw)
                if tutar_val is not None:
                    possible_tutarlar.append(tutar_val)

            if 'line_item' in field_type or \
                    any(keyword in field_value_raw.lower() for keyword in ["kwh", "tüketim", "aktif enerji", "enerji"]):

                # Ama yine de içinde bu kelimelerden biri geçiyorsa sayıyı al (Dağıtım Bedeli gibi satırları atlamak için)
                if any(keyword in field_value_raw.lower() for keyword in ["kwh", "tüketim", "enerji", "aktif enerji"]):
                    kwh_val = clean_turkish_number(field_value_raw)
                    if kwh_val is not None:
                        possible_kwhs.append(kwh_val)

        # --- EN İYİ DEĞERLERİ SEÇME ---

        # Tutar: Bulunan tüm adaylar arasından en BÜYÜK olanı seç
        if possible_tutarlar:
            output["specific"]['tutar'] = max(possible_tutarlar)

        # kWh: Bulunan tüm kWh adaylarının hepsini TOPLA
        if possible_kwhs:
            output["specific"]['kwh'] = sum(possible_kwhs)

        output["all_found"] = all_entities_simple
        return output

    except ImportError:
        st.error("Google Cloud kütüphaneleri bulunamadı...")
        return output
    except Exception as e:
        st.error(f"Google Document AI API Hatası: {e}")
        st.error("Tam Hata Detayı:")
        st.code(traceback.format_exc())
        st.error("Lütfen Google Cloud ayarlarınızı ve ortam değişkeninizi kontrol edin.")
        return output