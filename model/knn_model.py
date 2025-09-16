import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

class KNNRecommender:
    def __init__(self, k=3):
        self.k = k
        self.model = KNeighborsClassifier(n_neighbors=self.k)
        self.le = LabelEncoder()
        self.is_trained = False
        
    def train(self, data):
        # Pisahkan fitur dan label
        X = data[['Minat Olahraga', 'Minat Keorganisasian', 'Minat Keagamaan']]
        y = data['Ekskul Pilihan']
        
        # Encode label
        y_encoded = self.le.fit_transform(y)
        
        # Latih model
        self.model.fit(X, y_encoded)
        self.is_trained = True
        
    def predict(self, minat_olahraga, minat_keorganisasian, minat_keagamaan):
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Panggil metode train() terlebih dahulu.")
            
        # Buat dataframe dari input
        input_data = np.array([[minat_olahraga, minat_keorganisasian, minat_keagamaan]])
        
        # Prediksi
        pred_encoded = self.model.predict(input_data)
        
        # Decode label
        pred_label = self.le.inverse_transform(pred_encoded)
        
        return pred_label[0]
    
    def get_distance_explanation(self, minat_olahraga, minat_keorganisasian, minat_keagamaan, data):
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Panggil metode train() terlebih dahulu.")
            
        # Buat dataframe dari input
        input_data = np.array([[minat_olahraga, minat_keorganisasian, minat_keagamaan]])
        
        # Hitung jarak ke semua titik data
        distances, indices = self.model.kneighbors(input_data)
        
        # Ambil data tetangga terdekat
        nearest_neighbors = data.iloc[indices[0]]
        
        # Tambahkan kolom jarak
        nearest_neighbors = nearest_neighbors.copy()
        nearest_neighbors['Jarak'] = distances[0]
        
        return nearest_neighbors