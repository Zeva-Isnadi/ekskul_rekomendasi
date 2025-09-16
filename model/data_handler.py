import pandas as pd
import os

class DataHandler:
    def __init__(self, data_path='data/dataset.csv'):
        self.data_path = data_path
        self.data = None
        
    def load_data(self):
        # Cek apakah folder data ada, jika tidak buat
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        # Cek apakah file ada
        if not os.path.exists(self.data_path):
            # Buat dataset sintetis jika belum ada
            self.create_synthetic_data()
        
        # Muat data
        try:
            self.data = pd.read_csv(self.data_path)
            # Jika data kosong, buat ulang
            if self.data.empty:
                self.create_synthetic_data()
                self.data = pd.read_csv(self.data_path)
        except pd.errors.EmptyDataError:
            # Jika file ada tapi kosong, buat ulang
            self.create_synthetic_data()
            self.data = pd.read_csv(self.data_path)
        
        return self.data
    
    def create_synthetic_data(self):
        # Dataset sintetis berdasarkan pola yang telah ditentukan
        data = {
            'ID': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6'],
            'Nama': ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fajar'],
            'Kelas': ['X IPA 1', 'X IPS 2', 'XI IPA 1', 'X IPA 2', 'XI IPS 1', 'XII IPA 2'],
            'Minat Olahraga': [5, 2, 4, 1, 3, 5],
            'Minat Keorganisasian': [1, 5, 2, 1, 4, 3],
            'Minat Keagamaan': [2, 3, 5, 5, 4, 2],
            'Ekskul Pilihan': ['Futsal', 'Hizbul Wathan', 'Tapak Suci', 'Tahfizh Quran', 'Hizbul Wathan', 'Futsal'],
            'Status': ['Terkonfirmasi', 'Terkonfirmasi', 'Terkonfirmasi', 'Terkonfirmasi', 'Terkonfirmasi', 'Terkonfirmasi']
        }
        
        df = pd.DataFrame(data)
        df.to_csv(self.data_path, index=False)
        return df
    
    def add_data(self, id_siswa, minat_olahraga, minat_keorganisasian, minat_keagamaan, ekskul_pilihan):
        # Muat data yang ada
        if self.data is None:
            self.load_data()
        
        # Buat data baru
        new_data = pd.DataFrame({
            'ID': [id_siswa],
            'Nama': ['Unknown'],
            'Kelas': ['Unknown'],
            'Minat Olahraga': [minat_olahraga],
            'Minat Keorganisasian': [minat_keorganisasian],
            'Minat Keagamaan': [minat_keagamaan],
            'Ekskul Pilihan': [ekskul_pilihan],
            'Status': ['Terkonfirmasi']
        })
        
        # Gabungkan dengan data lama
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        
        # Simpan kembali
        self.data.to_csv(self.data_path, index=False)
        
        return self.data
    
    def add_data_with_status(self, id_siswa, nama, kelas, minat_olahraga, minat_keorganisasian, minat_keagamaan, ekskul_pilihan, status):
        # Muat data yang ada
        if self.data is None:
            self.load_data()
        
        # Buat data baru
        new_data = pd.DataFrame({
            'ID': [id_siswa],
            'Nama': [nama],
            'Kelas': [kelas],
            'Minat Olahraga': [minat_olahraga],
            'Minat Keorganisasian': [minat_keorganisasian],
            'Minat Keagamaan': [minat_keagamaan],
            'Ekskul Pilihan': [ekskul_pilihan],
            'Status': [status]
        })
        
        # Gabungkan dengan data lama
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        
        # Simpan kembali
        self.data.to_csv(self.data_path, index=False)
        
        return self.data
    
    def update_status(self, id_siswa, new_status, new_ekskul=None):
        # Muat data yang ada
        if self.data is None:
            self.load_data()
        
        # Update status
        self.data.loc[self.data['ID'] == id_siswa, 'Status'] = new_status
        
        # Update ekskul jika ada perubahan
        if new_ekskul:
            self.data.loc[self.data['ID'] == id_siswa, 'Ekskul Pilihan'] = new_ekskul
        
        # Simpan kembali
        self.data.to_csv(self.data_path, index=False)
        
        return self.data
    
    def delete_student(self, id_siswa):
        # Load data yang ada
        if self.data is None:
            self.load_data()
        
        # Hapus baris data siswa
        self.data = self.data[self.data['ID'] != id_siswa]
        
        # Simpan kembali
        self.data.to_csv(self.data_path, index=False)
        
        return self.data