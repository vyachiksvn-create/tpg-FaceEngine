#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для построения базы данных эмбендингов лиц.
Извлекает эмбендинги из всех фото в base_photos, нормализует имена,
группирует дубликаты и сохраняет в embeddings.npy и metadata.json
"""

import os
import sys
import io
import cv2
import json
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import re
from collections import defaultdict
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==================== КОНФИГУРАЦИЯ ====================
BASE_DIR = "base_photos"
INPUT_DIR = "input_photos"
DB_EMB_FILE = "embeddings.npy"
DB_META_FILE = "metadata.json"

# ==================== ИНИЦИАЛИЗАЦИЯ МОДЕЛИ ====================
print("[*] Загрузка модели InsightFace...")
app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))
print("[+] Модель загружена")

# ==================== ФУНКЦИИ ====================
def normalize_name(filename):
    """
    Нормализует имя файла для группировки фото одной персоны.
    Примеры:
        "Абакарова Ольга - хостесс.jpg" -> "абакарова ольга"
        "Абакарова Ольга2.jpg" -> "абакарова ольга"
    """
    name = Path(filename).stem
    
    # Убираем суффиксы с цифрами в конце
    name = re.sub(r'[_\s]*(\d+)$', '', name)
    
    # Убираем должности и роли (после " - ", "–", "—")
    name = re.split(r'\s*[-–—]\s*', name)[0]
    
    # Приводим к нижнему регистру и убираем лишние пробелы
    name = ' '.join(name.lower().split())
    
    return name

def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

def extract_embeddings_from_image(filepath):
    data = np.fromfile(filepath, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        return None, "Не удалось прочитать файл"
    
    faces = app.get(img)
    if not faces:
        return None, "Лицо не найдено"
    
    face = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]))
    return face.embedding, None

def build_database():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(INPUT_DIR, exist_ok=True)
    
    files = [f for f in os.listdir(BASE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
    if not files:
        print(f"[-] В папке '{BASE_DIR}' не найдено изображений!")
        return
    
    print(f"\n[*] Найдено файлов: {len(files)}")
    print("[*] Начинаю обработку...\n")
    
    embeddings = []
    metadata = []
    person_groups = defaultdict(list)
    
    errors = []
    processed = 0
    
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(BASE_DIR, filename)
        emb, error = extract_embeddings_from_image(filepath)
        
        if emb is None:
            errors.append((filename, error))
            continue
        
        original_name = Path(filename).stem
        normalized_name = normalize_name(filename)
        is_known = has_cyrillic(original_name)
        
        metadata_entry = {
            "original_name": original_name,
            "normalized_name": normalized_name,
            "file": filename,
            "is_known": is_known
        }
        
        embeddings.append(emb)
        metadata.append(metadata_entry)
        person_groups[normalized_name].append(len(metadata) - 1)
        
        processed += 1
        
        if processed % 100 == 0:
            print(f"  Обработано: {processed} / {len(files)} ({processed/len(files)*100:.1f}%)")
    
    print("\n" + "="*60)
    print("[*] СТАТИСТИКА ОБРАБОТКИ")
    print("="*60)
    print(f"[+] Успешно обработано: {processed}")
    print(f"[-] Ошибок: {len(errors)}")
    print(f"[*] Уникальных персон: {len(person_groups)}")
    
    duplicates = {k: v for k, v in person_groups.items() if len(v) > 1}
    multi_variations = {k: v for k, v in duplicates.items() 
                       if len(set(metadata[idx]["original_name"] for idx in v)) > 1}
    
    print(f"[*] Персон с несколькими фото: {len(duplicates)}")
    print(f"[!] Персон с разными вариантами имени: {len(multi_variations)}")
    
    if errors:
        print(f"\n[!] Файлы с ошибками ({len(errors)}):")
        for filename, error in errors[:10]:
            print(f"  - {filename}: {error}")
        if len(errors) > 10:
            print(f"  ... и еще {len(errors) - 10}")
    
    if multi_variations:
        print(f"\n[*] Примеры дубликатов (требуют объединения):")
        for i, (norm_name, indices) in enumerate(list(multi_variations.items())[:5]):
            variations = list(set(metadata[idx]["original_name"] for idx in indices))
            print(f"\n  {i+1}. {norm_name.upper()}")
            print(f"     Фото: {len(indices)}")
            for var in variations[:5]:
                print(f"     - {var}")
            if len(variations) > 5:
                print(f"     ... и еще {len(variations) - 5}")
    
    print("\n" + "="*60)
    print("[*] СОХРАНЕНИЕ БАЗЫ ДАННЫХ")
    print("="*60)
    
    embeddings_array = np.array(embeddings, dtype=np.float32)
    np.save(DB_EMB_FILE, embeddings_array)
    print(f"[+] Сохранено эмбендингов: {embeddings_array.shape}")
    print(f"    Файл: {DB_EMB_FILE} ({os.path.getsize(DB_EMB_FILE) / 1024 / 1024:.2f} MB)")
    
    groups_info = {}
    for norm_name, indices in person_groups.items():
        if len(indices) > 1:
            variations = list(set(metadata[idx]["original_name"] for idx in indices))
            groups_info[norm_name] = {
                "count": len(indices),
                "variations": variations,
                "indices": indices
            }
    
    db_data = {
        "metadata": metadata,
        "person_groups": groups_info,
        "stats": {
            "total_photos": processed,
            "unique_persons": len(person_groups),
            "persons_with_duplicates": len(duplicates),
            "persons_with_name_variations": len(multi_variations),
            "errors": len(errors)
        }
    }
    
    with open(DB_META_FILE, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)
    
    print(f"[+] Сохранено метаданных: {DB_META_FILE}")
    print(f"    Фото в базе: {len(metadata)}")
    print(f"    Уникальных персон: {len(person_groups)}")
    
    print("\n" + "="*60)
    print("[+] БАЗА ДАННЫХ УСПЕШНО СОЗДАНА!")
    print("="*60)
    print(f"\n[*] Следующие шаги:")
    print(f"  1. Запустите: streamlit run operator_app.py")
    print(f"  2. Добавьте фото в папку: {INPUT_DIR}")
    print(f"  3. Обрабатывайте фото через веб-интерфейс")
    
    if multi_variations:
        print(f"\n[*] Рекомендация:")
        print(f"  В базе найдено {len(multi_variations)} персон с разными")
        print(f"  вариантами имени. Используйте интерфейс оператора для")
        print(f"  объединения дубликатов.")

if __name__ == "__main__":
    try:
        build_database()
    except KeyboardInterrupt:
        print("\n\n[!] Прервано пользователем")
    except Exception as e:
        print(f"\n[-] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
