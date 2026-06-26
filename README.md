# ⚔️ Dungeon Adventure Game
> **Final Project - Aplikasi RPG CLI dengan Database CSV**

Dungeon Adventure Game adalah permainan RPG berbasis teks (*Command Line Interface*) yang dibangun menggunakan **Python**. Proyek ini dibuat untuk mendemonstrasikan implementasi struktur data fundamental secara manual tanpa library eksternal, serta manajemen data berbasis file CSV[cite: 1].

---

## 🚀 Fitur Utama

* **Eksplorasi Map:** Berpindah tempat antar lokasi terhubung menggunakan arah mata angin[cite: 1].
* **Pertarungan Turn-Based:** Hadapi monster, gunakan *potion*, atau melarikan diri secara taktis[cite: 1].
* **Inventory & Shop:** Sistem beli item (*weapon, armor, potion*) untuk meningkatkan status karakter[cite: 1].
* **Admin Panel (CRUD):** Fitur khusus untuk melihat, menambah, atau menghapus data pemain, lokasi, item, dan musuh secara *real-time*[cite: 1].
* **Auto-Save System:** Game otomatis menyimpan progress pemain langsung ke file CSV[cite: 1].

---

## 🧠 Implementasi Struktur Data

Untuk mendukung mekanik game, proyek ini menggunakan 4 struktur data berbeda yang diimplementasikan secara manual:

* **Linked List (`LocationLinkedList`):** Digunakan untuk memetakan jalur antar lokasi (North, South, East, West)[cite: 1].
* **Hash Map (`HashMap`):** Digunakan untuk mengelola *inventory* item pemain dengan fungsi *hashing* custom[cite: 1].
* **Queue (`EnemyQueue`):** Mengatur antrean monster yang muncul di suatu lokasi menggunakan prinsip FIFO[cite: 1].
* **Stack (`MoveStack`):** Menyimpan riwayat langkah pemain, mendukung fitur *Undo* untuk kembali ke lokasi sebelumnya (LIFO)[cite: 1].

---

## 📂 Struktur Data File (Database)

Aplikasi akan otomatis membuat folder `data/` dan file CSV berikut saat pertama kali dijalankan[cite: 1]:
* `players.csv` – Menyimpan data status dan posisi terakhir pemain[cite: 1].
* `locations.csv` – Menyimpan data map dan keterhubungan antar lokasi[cite: 1].
* `items.csv` – Menyimpan daftar item beserta harga dan efeknya[cite: 1].
* `enemies.csv` – Menyimpan status monster dan lokasi tempat mereka muncul[cite: 1].

---

## 🛠️ Cara Menjalankan

1. **Clone Repositori:**
   ```bash
   git clone [https://github.com/farid404ops/dungeon-adventure-game.git](https://github.com/farid404ops/dungeon-adventure-game.git)
   cd dungeon-adventure-game