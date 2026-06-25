import csv
import os
import random
from collections import deque


DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PLAYERS   = os.path.join(DIR, "data", "players.csv")
FILE_LOCATIONS = os.path.join(DIR, "data", "locations.csv")
FILE_ITEMS     = os.path.join(DIR, "data", "items.csv")
FILE_ENEMIES   = os.path.join(DIR, "data", "enemies.csv")


class LocationNode:
    def __init__(self, loc_id, name, description, north=None, south=None, east=None, west=None):
        self.loc_id      = loc_id
        self.name        = name
        self.description = description
        self.exits       = {"north": north, "south": south, "east": east, "west": west}
        self.next        = None   # pointer ke node berikutnya di linked list


class LocationLinkedList:
    def __init__(self):
        self.head = None

    def add(self, node: LocationNode):
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
                cur.next = node

    def find(self, loc_id: str):
        cur = self.head
        while cur:
            if cur.loc_id == loc_id:
                return cur
            cur = cur.next
        return None

    def all_ids(self):
        ids, cur = [], self.head
        while cur:
            ids.append(cur.loc_id)
            cur = cur.next
        return ids


class HashMap:
    def __init__(self, size=64):
        self.size    = size
        self.buckets = [[] for _ in range(size)]

    def _hash(self, key: str) -> int:
        return sum(ord(c) for c in key) % self.size

    def set(self, key: str, value):
        idx = self._hash(key)
        for pair in self.buckets[idx]:
            if pair[0] == key:
                pair[1] = value
                return
        self.buckets[idx].append([key, value])

    def get(self, key: str):
        idx = self._hash(key)
        for pair in self.buckets[idx]:
            if pair[0] == key:
                return pair[1]
        return None

    def delete(self, key: str) -> bool:
        idx = self._hash(key)
        for i, pair in enumerate(self.buckets[idx]):
            if pair[0] == key:
                self.buckets[idx].pop(i)
                return True
        return False

    def all_items(self):
        result = []
        for bucket in self.buckets:
            for pair in bucket:
                result.append((pair[0], pair[1]))
        return result

    def is_empty(self):
        return all(len(b) == 0 for b in self.buckets)

class EnemyQueue:
    def __init__(self):
        self._q = deque()

    def enqueue(self, enemy: dict):
        self._q.append(enemy)

    def dequeue(self):
        return self._q.popleft() if self._q else None

    def peek(self):
        return self._q[0] if self._q else None

    def is_empty(self):
        return len(self._q) == 0

    def size(self):
        return len(self._q)

class MoveStack:
    def __init__(self):
        self._stack = []

    def push(self, loc_id):
        self._stack.append(loc_id)

    def pop(self):
        return self._stack.pop() if self._stack else None

    def peek(self):
        return self._stack[-1] if self._stack else None

    def is_empty(self):
        return len(self._stack) == 0

    def history(self):
        return list(self._stack)


def ensure_dir():
    os.makedirs(os.path.join(DIR, "data"), exist_ok=True)


def init_csv_files():
    ensure_dir()

    if not os.path.exists(FILE_PLAYERS):
        with open(FILE_PLAYERS, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["name", "hp", "max_hp", "attack", "defense", "gold", "location_id"])

    if not os.path.exists(FILE_LOCATIONS):
        with open(FILE_LOCATIONS, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["loc_id", "name", "description", "north", "south", "east", "west"])
            w.writerows([
                ["L1", "Gerbang Kerajaan",    "Pintu masuk ke dungeon yang gelap.",          "",   "L2", "",   ""],
                ["L2", "Lorong Batu",         "Lorong sempit berbau lembab.",                "L1", "L3", "L4", ""],
                ["L3", "Ruang Bawah Tanah",   "Ruang gelap berisi peti harta karun.",        "L2", "",   "",   ""],
                ["L4", "Hutan Misterius",     "Hutan lebat dengan suara aneh.",              "",   "",   "",   "L2"],
                ["L5", "Gua Naga",            "Sarang naga yang menyemburkan api.",          "",   "",   "L3", ""],
            ])

    if not os.path.exists(FILE_ITEMS):
        with open(FILE_ITEMS, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["item_id", "name", "type", "value", "effect"])
            w.writerows([
                ["I1", "Pedang Besi",     "weapon", 50,  15],
                ["I2", "Perisai Kayu",    "armor",  30,  10],
                ["I3", "Ramuan Merah",    "potion", 20,  30],
                ["I4", "Busur Elfin",     "weapon", 80,  20],
                ["I5", "Helm Baja",       "armor",  40,  12],
                ["I6", "Ramuan Biru",     "potion", 25,  50],
                ["I7", "Tongkat Sihir",   "weapon", 70,  25],
                ["I8", "Jubah Malam",     "armor",  60,  18],
            ])

    if not os.path.exists(FILE_ENEMIES):
        with open(FILE_ENEMIES, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["enemy_id", "name", "hp", "attack", "defense", "gold_drop", "location_id"])
            w.writerows([
                ["E1", "Goblin",      30,  8,  3,  10, "L2"],
                ["E2", "Ork Besar",   60, 15,  6,  25, "L3"],
                ["E3", "Serigala",    40, 10,  4,  15, "L4"],
                ["E4", "Naga Muda",  120, 30, 15,  80, "L5"],
                ["E5", "Zombie",      35,  7,  2,  12, "L2"],
                ["E6", "Penyihir",    50, 20,  5,  30, "L3"],
            ])


def load_locations() -> LocationLinkedList:
    ll = LocationLinkedList()
    with open(FILE_LOCATIONS, newline="") as f:
        for row in csv.DictReader(f):
            node = LocationNode(
                row["loc_id"], row["name"], row["description"],
                row["north"] or None, row["south"] or None,
                row["east"] or None,  row["west"] or None,
            )
            ll.add(node)
    return ll


def load_all_items() -> dict:
    items = {}
    with open(FILE_ITEMS, newline="") as f:
        for row in csv.DictReader(f):
            items[row["item_id"]] = {
                "name": row["name"], "type": row["type"],
                "value": int(row["value"]), "effect": int(row["effect"]),
            }
    return items


def load_enemies_for_location(loc_id: str) -> EnemyQueue:
    q = EnemyQueue()
    with open(FILE_ENEMIES, newline="") as f:
        for row in csv.DictReader(f):
            if row["location_id"] == loc_id:
                q.enqueue({
                    "enemy_id": row["enemy_id"],
                    "name":     row["name"],
                    "hp":       int(row["hp"]),
                    "attack":   int(row["attack"]),
                    "defense":  int(row["defense"]),
                    "gold":     int(row["gold_drop"]),
                })
    return q


def read_all_players() -> list:
    players = []
    with open(FILE_PLAYERS, newline="") as f:
        for row in csv.DictReader(f):
            players.append(row)
    return players


def save_player(player: dict):
    players = read_all_players()
    found = False
    for p in players:
        if p["name"] == player["name"]:
            p.update(player)
            found = True
            break
    if not found:
        players.append(player)
    with open(FILE_PLAYERS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name","hp","max_hp","attack","defense","gold","location_id"])
        w.writeheader()
        w.writerows(players)


def delete_player(name: str) -> bool:
    players = read_all_players()
    new_list = [p for p in players if p["name"] != name]
    if len(new_list) == len(players):
        return False
    with open(FILE_PLAYERS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name","hp","max_hp","attack","defense","gold","location_id"])
        w.writeheader()
        w.writerows(new_list)
    return True


def add_location_csv(loc_id, name, desc, north="", south="", east="", west=""):
    with open(FILE_LOCATIONS, "a", newline="") as f:
        csv.writer(f).writerow([loc_id, name, desc, north, south, east, west])


def add_item_csv(item_id, name, itype, value, effect):
    with open(FILE_ITEMS, "a", newline="") as f:
        csv.writer(f).writerow([item_id, name, itype, value, effect])


def add_enemy_csv(enemy_id, name, hp, attack, defense, gold, loc_id):
    with open(FILE_ENEMIES, "a", newline="") as f:
        csv.writer(f).writerow([enemy_id, name, hp, attack, defense, gold, loc_id])


SEP  = "=" * 55
SEP2 = "-" * 55

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print(SEP)
    print("  ⚔  DUNGEON ADVENTURE GAME  ⚔")
    print("  Final Project — Python + CSV Database")
    print(SEP)

def show_status(player: dict):
    print(SEP2)
    print(f"  [{player['name']}]  HP: {player['hp']}/{player['max_hp']}  "
          f"ATK: {player['attack']}  DEF: {player['defense']}  Gold: {player['gold']}")
    print(SEP2)

def show_location(node: LocationNode):
    print(f"\n📍 {node.name}")
    print(f"   {node.description}")
    exits = [f"{d.upper()}={node.exits[d]}" for d in node.exits if node.exits[d]]
    print(f"   Keluar: {', '.join(exits) if exits else 'Tidak ada'}")


def battle(player: dict, enemy: dict, inventory: HashMap) -> bool:
    """Return True jika player menang."""
    print(f"\n⚔  PERTARUNGAN! {player['name']} vs {enemy['name']}")
    print(SEP2)
    enemy_hp = enemy["hp"]
    p_atk = int(player["attack"])
    p_def = int(player["defense"])

    while int(player["hp"]) > 0 and enemy_hp > 0:
        print(f"\n  [Kamu] HP:{player['hp']}  vs  [{enemy['name']}] HP:{enemy_hp}")
        print("  [1] Serang  [2] Gunakan Ramuan  [3] Lari")
        choice = input("  Pilih: ").strip()

        if choice == "1":
            dmg_to_enemy = max(1, p_atk - enemy["defense"] + random.randint(-2, 4))
            enemy_hp -= dmg_to_enemy
            print(f"  💥 Kamu menyerang! Damage: {dmg_to_enemy}")
            if enemy_hp <= 0:
                break
            dmg_to_player = max(1, enemy["attack"] - p_def + random.randint(-2, 4))
            player["hp"] = str(int(player["hp"]) - dmg_to_player)
            print(f"  🩸 {enemy['name']} menyerang! Damage: {dmg_to_player}")

        elif choice == "2":
            potions = [(k, v) for k, v in inventory.all_items() if v["type"] == "potion"]
            if not potions:
                print("  Tidak ada ramuan!")
                continue
            print("  Ramuan tersedia:")
            for i, (k, v) in enumerate(potions, 1):
                print(f"  [{i}] {v['name']} (+{v['effect']} HP)")
            pi = input("  Pilih ramuan: ").strip()
            if pi.isdigit() and 1 <= int(pi) <= len(potions):
                key, item = potions[int(pi)-1]
                player["hp"] = str(min(int(player["max_hp"]), int(player["hp"]) + item["effect"]))
                inventory.delete(key)
                print(f"  ✅ Menggunakan {item['name']}. HP sekarang: {player['hp']}")

        elif choice == "3":
            print("  🏃 Kamu melarikan diri!")
            return False

    if int(player["hp"]) <= 0:
        print(f"\n  💀 Kamu dikalahkan oleh {enemy['name']}!")
        return False
    else:
        gold_gain = enemy["gold"]
        player["gold"] = str(int(player["gold"]) + gold_gain)
        print(f"\n  🏆 {enemy['name']} dikalahkan! +{gold_gain} Gold")
        return True


def shop(player: dict, all_items: dict, inventory: HashMap):
    print("\n🛒 TOKO ITEM")
    print(SEP2)
    shop_items = list(all_items.items())
    for i, (iid, item) in enumerate(shop_items, 1):
        print(f"  [{i}] {item['name']:15} | Tipe: {item['type']:6} | Efek: +{item['effect']:2} | Harga: {item['value']} Gold")
    print(f"\n  Gold kamu: {player['gold']}")
    choice = input("  Beli nomor (0=keluar): ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(shop_items):
            iid, item = shop_items[idx]
            if int(player["gold"]) >= item["value"]:
                player["gold"] = str(int(player["gold"]) - item["value"])
                inventory.set(iid + "_" + str(random.randint(100,999)), item)
                print(f"  ✅ {item['name']} dibeli!")
            else:
                print("  ❌ Gold tidak cukup!")


def equip_item(player: dict, inventory: HashMap):
    items = [(k, v) for k, v in inventory.all_items() if v["type"] in ("weapon", "armor")]
    if not items:
        print("  Tidak ada item yang bisa diequip.")
        return
    print("\n🎒 EQUIP ITEM")
    for i, (k, v) in enumerate(items, 1):
        print(f"  [{i}] {v['name']} | Efek: +{v['effect']}")
    choice = input("  Pilih (0=batal): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(items):
        key, item = items[int(choice)-1]
        if item["type"] == "weapon":
            player["attack"] = str(int(player["attack"]) + item["effect"])
            print(f"  ⚔  {item['name']} diequip! ATK +{item['effect']}")
        else:
            player["defense"] = str(int(player["defense"]) + item["effect"])
            print(f"  🛡  {item['name']} diequip! DEF +{item['effect']}")
        inventory.delete(key)


def play_game(player: dict, loc_ll: LocationLinkedList, all_items: dict):
    inventory  = HashMap()
    move_stack = MoveStack()
    move_stack.push(player["location_id"])

    while True:
        clr()
        banner()
        show_status(player)

        current_node = loc_ll.find(player["location_id"])
        if not current_node:
            print("  [ERROR] Lokasi tidak ditemukan!")
            break

        show_location(current_node)

        enemy_q = load_enemies_for_location(player["location_id"])

        print("\n  [1] Jelajahi (hadapi musuh)")
        print("  [2] Pindah lokasi")
        print("  [3] Kembali (undo)")
        print("  [4] Lihat inventory")
        print("  [5] Equip item")
        print("  [6] Toko item")
        print("  [7] Simpan & keluar")

        act = input("\n  >> ").strip()

        if act == "1":
            if enemy_q.is_empty():
                print("\n  ✅ Tidak ada musuh di sini. Area aman!")
            else:
                enemy = enemy_q.dequeue()
                result = battle(player, enemy, inventory)
                if int(player["hp"]) <= 0:
                    print("\n  💀 GAME OVER!")
                    player["hp"] = player["max_hp"]
                    player["location_id"] = "L1"
                    save_player(player)
                    input("\n  Tekan Enter untuk kembali ke menu...")
                    return
            input("\n  Tekan Enter...")

        elif act == "2":
            print("\n  Pilih arah:")
            valid = {d: v for d, v in current_node.exits.items() if v}
            for d, dest in valid.items():
                dest_node = loc_ll.find(dest)
                dname = dest_node.name if dest_node else dest
                print(f"  [{d[0].upper()}] {d.capitalize()} → {dname}")
            direction = input("  Arah (n/s/e/w): ").strip().lower()
            dir_map = {"n": "north", "s": "south", "e": "east", "w": "west"}
            full_dir = dir_map.get(direction)
            if full_dir and current_node.exits.get(full_dir):
                move_stack.push(player["location_id"])
                player["location_id"] = current_node.exits[full_dir]
                print(f"\n  ➡  Berpindah ke {current_node.exits[full_dir]}...")
            else:
                print("  ❌ Arah tidak valid!")
            input("\n  Tekan Enter...")

        elif act == "3":
            if move_stack.is_empty() or move_stack.peek() == player["location_id"]:
                print("  Tidak ada history pergerakan.")
            else:
                prev = move_stack.pop()
                if prev:
                    player["location_id"] = prev
                    print(f"  ↩  Kembali ke lokasi sebelumnya: {prev}")
            input("\n  Tekan Enter...")

        elif act == "4":
            print("\n🎒 INVENTORY")
            if inventory.is_empty():
                print("  Inventory kosong.")
            else:
                for k, v in inventory.all_items():
                    print(f"  • {v['name']} [{v['type']}] efek +{v['effect']}")
            input("\n  Tekan Enter...")

        elif act == "5":
            equip_item(player, inventory)
            input("\n  Tekan Enter...")

        elif act == "6":
            shop(player, all_items, inventory)
            input("\n  Tekan Enter...")

        elif act == "7":
            save_player(player)
            print("\n  💾 Game tersimpan. Sampai jumpa!")
            break


def admin_panel(loc_ll: LocationLinkedList):
    while True:
        clr()
        print(SEP)
        print("  ⚙  ADMIN PANEL")
        print(SEP)
        print("  [1] Lihat semua pemain (Read)")
        print("  [2] Tambah lokasi baru (Create)")
        print("  [3] Tambah item baru (Create)")
        print("  [4] Tambah musuh baru (Create)")
        print("  [5] Hapus pemain (Delete)")
        print("  [0] Kembali")
        choice = input("\n  >> ").strip()

        if choice == "1":
            players = read_all_players()
            print(f"\n  Total pemain: {len(players)}")
            print(f"  {'Nama':<15} {'HP':<8} {'ATK':<6} {'DEF':<6} {'Gold':<8} {'Lokasi'}")
            print("  " + "-"*50)
            for p in players:
                print(f"  {p['name']:<15} {p['hp']}/{p['max_hp']:<5} {p['attack']:<6} {p['defense']:<6} {p['gold']:<8} {p['location_id']}")
            input("\n  Tekan Enter...")

        elif choice == "2":
            print("\n  Tambah Lokasi Baru")
            lid  = input("  ID Lokasi (cth: L6): ").strip()
            name = input("  Nama: ").strip()
            desc = input("  Deskripsi: ").strip()
            n = input("  North (ID/kosong): ").strip()
            s = input("  South (ID/kosong): ").strip()
            e = input("  East  (ID/kosong): ").strip()
            w = input("  West  (ID/kosong): ").strip()
            add_location_csv(lid, name, desc, n, s, e, w)
            new_node = LocationNode(lid, name, desc, n or None, s or None, e or None, w or None)
            loc_ll.add(new_node)
            print(f"  ✅ Lokasi '{name}' ditambahkan!")
            input("\n  Tekan Enter...")

        elif choice == "3":
            print("\n  Tambah Item Baru")
            iid   = input("  ID Item (cth: I9): ").strip()
            name  = input("  Nama: ").strip()
            itype = input("  Tipe (weapon/armor/potion): ").strip()
            val   = input("  Harga: ").strip()
            eff   = input("  Efek: ").strip()
            add_item_csv(iid, name, itype, val, eff)
            print(f"  ✅ Item '{name}' ditambahkan!")
            input("\n  Tekan Enter...")

        elif choice == "4":
            print("\n  Tambah Musuh Baru")
            eid  = input("  ID Musuh (cth: E7): ").strip()
            name = input("  Nama: ").strip()
            hp   = input("  HP: ").strip()
            atk  = input("  Attack: ").strip()
            deff = input("  Defense: ").strip()
            gold = input("  Gold drop: ").strip()
            lid  = input("  Lokasi ID: ").strip()
            add_enemy_csv(eid, name, hp, atk, deff, gold, lid)
            print(f"  ✅ Musuh '{name}' ditambahkan!")
            input("\n  Tekan Enter...")

        elif choice == "5":
            name = input("  Nama pemain yang dihapus: ").strip()
            if delete_player(name):
                print(f"  ✅ Pemain '{name}' dihapus.")
            else:
                print(f"  ❌ Pemain '{name}' tidak ditemukan.")
            input("\n  Tekan Enter...")

        elif choice == "0":
            break

def main():
    init_csv_files()
    loc_ll    = load_locations()
    all_items = load_all_items()

    while True:
        clr()
        banner()
        print("\n  [1] Mulai Game Baru")
        print("  [2] Lanjutkan Game")
        print("  [3] Admin Panel")
        print("  [0] Keluar")
        choice = input("\n  >> ").strip()

        if choice == "1":
            clr()
            print("\n  ── BUAT KARAKTER BARU ──")
            name = input("  Nama karakter: ").strip()
            if not name:
                print("  Nama tidak boleh kosong!")
                input()
                continue
            # Cek duplikat
            if any(p["name"] == name for p in read_all_players()):
                print(f"  ❌ Nama '{name}' sudah ada! Gunakan menu Lanjutkan.")
                input("\n  Tekan Enter...")
                continue
            player = {
                "name": name, "hp": "100", "max_hp": "100",
                "attack": "15", "defense": "8",
                "gold": "50", "location_id": "L1",
            }
            save_player(player)
            print(f"\n  ✅ Karakter '{name}' dibuat! Petualangan dimulai...")
            input("  Tekan Enter...")
            play_game(player, loc_ll, all_items)

        elif choice == "2":
            players = read_all_players()
            if not players:
                print("  Belum ada save game!")
                input()
                continue
            print("\n  Pilih karakter:")
            for i, p in enumerate(players, 1):
                print(f"  [{i}] {p['name']}  HP:{p['hp']}/{p['max_hp']}  Gold:{p['gold']}  Loc:{p['location_id']}")
            sel = input("  Pilih: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(players):
                player = players[int(sel)-1]
                play_game(player, loc_ll, all_items)

        elif choice == "3":
            admin_panel(loc_ll)

        elif choice == "0":
            print("\n  Terima kasih telah bermain! 👋\n")
            break


if __name__ == "__main__":
    main()
