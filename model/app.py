import streamlit as st
import pandas as pd
import numpy as np
import os
from model.knn_model import KNNRecommender
from model.data_handler import DataHandler

# Set page config
st.set_page_config(page_title="Sistem Rekomendasi Ekstrakurikuler", layout="wide")

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'main'
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Main page
def main_page():
    st.markdown("<div class='main-header'><h1>Sistem Rekomendasi Ekstrakurikuler</h1><p>SMA Muhammadiyah 4 Margahayu</p></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='card'>
        <h3>Selamat Datang di Sistem Rekomendasi Ekstrakurikuler</h3>
        <p>Sistem ini membantu siswa menemukan ekstrakurikuler yang sesuai dengan minat dan bakat mereka menggunakan metode K-Nearest Neighbor (KNN).</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Siswa", key="siswa_btn"):
            st.session_state['role'] = 'siswa'
            st.session_state['page'] = 'recommend'
            st.rerun()
    
    with col2:
        if st.button("Guru", key="guru_btn"):
            st.session_state['role'] = 'guru'
            st.session_state['page'] = 'guru_login'
            st.rerun()

# Guru login page
def guru_login_page():
    st.markdown("<div class='main-header'><h1>Login Guru</h1></div>", unsafe_allow_html=True)
    
    # Back button
    if st.button("Kembali ke Halaman Utama", key="back_from_login"):
        st.session_state['page'] = 'main'
        st.rerun()
    
    st.markdown("""
    <div class='card'>
        <h3>Masuk ke Dashboard Guru</h3>
        <p>Silakan masukkan username dan password untuk mengakses dashboard guru.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username", placeholder="Masukkan username")
        
        with col2:
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
        
        login_button = st.form_submit_button("Login")
    
    # Simple authentication (in real app, use proper authentication)
    if login_button:
        if username == "admin" and password == "guru123":
            st.session_state['logged_in'] = True
            st.session_state['page'] = 'guru_dashboard'
            st.success("Login berhasil! Mengalihkan ke dashboard...")
            st.rerun()
        else:
            st.error("Username atau password salah. Silakan coba lagi.")

# Recommendation page for students
def recommendation_page():
    st.markdown("<div class='main-header'><h1>Rekomendasi Ekstrakurikuler untuk Siswa</h1></div>", unsafe_allow_html=True)
    
    # Back button
    if st.button("Kembali ke Halaman Utama", key="back_from_rec"):
        st.session_state['page'] = 'main'
        st.rerun()
    
    # Initialize data handler and model
    data_handler = DataHandler()
    data = data_handler.load_data()
    model = KNNRecommender(k=3)
    model.train(data)
    
    st.markdown("<div class='card'><h3>Isi Data Diri dan Minat Anda</h3></div>", unsafe_allow_html=True)
    
    # Input form
    with st.form("recommendation_form"):
        # Student identity
        col1, col2 = st.columns(2)
        with col1:
            nama_siswa = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
        with col2:
            kelas_siswa = st.selectbox("Kelas", ["X IPA 1", "X IPA 2", "X IPS 1", "X IPS 2", "XI IPA 1", "XI IPA 2", "XI IPS 1", "XI IPS 2", "XII IPA 1", "XII IPA 2", "XII IPS 1", "XII IPS 2"])
        
        st.markdown("---")
        
        # Interest inputs
        col1, col2, col3 = st.columns(3)
        with col1:
            minat_olahraga = st.slider("Minat Olahraga", 1, 5, 3)
        with col2:
            minat_keorganisasian = st.slider("Minat Keorganisasian", 1, 5, 3)
        with col3:
            minat_keagamaan = st.slider("Minat Keagamaan", 1, 5, 3)
        
        submit_button = st.form_submit_button("Dapatkan Rekomendasi")
    
    if submit_button:
        if not nama_siswa:
            st.error("Nama lengkap harus diisi!")
        else:
            # Get recommendation
            ekskul_rekomendasi = model.predict(minat_olahraga, minat_keorganisasian, minat_keagamaan)
            
            # Save student data with "Pending" status
            new_id = f"S{len(data) + 1}"  # Generate new ID
            data_handler.add_data_with_status(
                id_siswa=new_id,
                nama=nama_siswa,
                kelas=kelas_siswa,
                minat_olahraga=minat_olahraga,
                minat_keorganisasian=minat_keorganisasian,
                minat_keagamaan=minat_keagamaan,
                ekskul_pilihan=ekskul_rekomendasi,
                status="Menunggu Konfirmasi"
            )
            
            # Display recommendation
            st.markdown(f"<div class='stSuccess'><h3>Rekomendasi: {ekskul_rekomendasi}</h3></div>", unsafe_allow_html=True)
            
            # Display explanation
            st.markdown("<div class='card'><h3>Penjelasan Rekomendasi</h3></div>", unsafe_allow_html=True)
            
            st.write("Berdasarkan perhitungan jarak Euclidean, berikut adalah 3 tetangga terdekat:")
            
            # Get explanation
            nearest_neighbors = model.get_distance_explanation(minat_olahraga, minat_keorganisasian, minat_keagamaan, data)
            
            # Format nearest neighbors for display
            display_neighbors = nearest_neighbors[['ID', 'Minat Olahraga', 'Minat Keorganisasian', 'Minat Keagamaan', 'Ekskul Pilihan', 'Jarak']]
            st.dataframe(display_neighbors)
            
            st.markdown(f"""
            <div class='card'>
                <h4>Data Anda telah tersimpan!</h4>
                <p><strong>Nama:</strong> {nama_siswa}</p>
                <p><strong>Kelas:</strong> {kelas_siswa}</p>
                <p><strong>Rekomendasi Ekstrakurikuler:</strong> {ekskul_rekomendasi}</p>
                <p><em>Data Anda sedang menunggu konfirmasi dari guru. Silakan hubungi guru untuk konfirmasi pilihan ekstrakurikuler.</em></p>
            </div>
            """, unsafe_allow_html=True)

# Teacher dashboard
def teacher_dashboard():
    # Check if logged in
    if not st.session_state['logged_in']:
        st.session_state['page'] = 'guru_login'
        st.rerun()
    
    st.markdown("<div class='main-header'><h1>Dashboard Guru</h1></div>", unsafe_allow_html=True)
    
    # Logout button
    if st.button("Logout", key="logout_btn"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'main'
        st.rerun()
    
    # Initialize data handler
    data_handler = DataHandler()
    data = data_handler.load_data()
    
    # Sidebar menu
    st.sidebar.title("Menu Guru")
    menu = ["Rekomendasi", "Konfirmasi Data Siswa", "Lihat Dataset", "Tambah Data", "Kelola Akun"]
    choice = st.sidebar.selectbox("Pilih Menu", menu)
    
    if choice == "Rekomendasi":
        st.markdown("<div class='card'><h3>Rekomendasi Ekstrakurikuler</h3></div>", unsafe_allow_html=True)
        
        # Initialize model
        model = KNNRecommender(k=3)
        model.train(data)
        
        # Input form
        with st.form("teacher_recommendation_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                minat_olahraga = st.slider("Minat Olahraga", 1, 5, 3, key="teacher_olahraga")
            
            with col2:
                minat_keorganisasian = st.slider("Minat Keorganisasian", 1, 5, 3, key="teacher_keorganisasian")
            
            with col3:
                minat_keagamaan = st.slider("Minat Keagamaan", 1, 5, 3, key="teacher_keagamaan")
            
            submit_button = st.form_submit_button("Dapatkan Rekomendasi")
        
        if submit_button:
            # Get recommendation
            ekskul_rekomendasi = model.predict(minat_olahraga, minat_keorganisasian, minat_keagamaan)
            
            # Display recommendation
            st.markdown(f"<div class='stSuccess'><h3>Rekomendasi: {ekskul_rekomendasi}</h3></div>", unsafe_allow_html=True)
            
            # Get explanation
            nearest_neighbors = model.get_distance_explanation(minat_olahraga, minat_keorganisasian, minat_keagamaan, data)
            
            # Display explanation
            st.write("Berdasarkan perhitungan jarak Euclidean, berikut adalah 3 tetangga terdekat:")
            
            # Format nearest neighbors for display
            display_neighbors = nearest_neighbors[['ID', 'Nama', 'Kelas', 'Minat Olahraga', 'Minat Keorganisasian', 'Minat Keagamaan', 'Ekskul Pilihan', 'Jarak']]
            st.dataframe(display_neighbors)
    
    elif choice == "Konfirmasi Data Siswa":
        st.markdown("<div class='card'><h3>Konfirmasi Data Siswa Baru</h3></div>", unsafe_allow_html=True)
        
        # Filter data yang menunggu konfirmasi
        pending_data = data[data['Status'] == 'Menunggu Konfirmasi']
        
        if pending_data.empty:
            st.info("Tidak ada data siswa yang menunggu konfirmasi.")
        else:
            st.write(f"Terdapat {len(pending_data)} data siswa yang menunggu konfirmasi:")
            
            # Display pending data
            st.dataframe(pending_data[['ID', 'Nama', 'Kelas', 'Minat Olahraga', 'Minat Keorganisasian', 'Minat Keagamaan', 'Ekskul Pilihan']])
            
            # Confirmation form
            st.markdown("---")
            st.markdown("<div class='card'><h3>Konfirmasi Pilihan Ekstrakurikuler</h3></div>", unsafe_allow_html=True)
            
            with st.form("confirmation_form"):
                # Select student
                student_options = pending_data['ID'].tolist()
                selected_student = st.selectbox("Pilih Siswa", student_options)
                
                # Get student data
                student_data = pending_data[pending_data['ID'] == selected_student].iloc[0]
                
                # Display student info
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Nama:** {student_data['Nama']}")
                    st.write(f"**Kelas:** {student_data['Kelas']}")
                with col2:
                    st.write(f"**Minat Olahraga:** {student_data['Minat Olahraga']}")
                    st.write(f"**Minat Keorganisasian:** {student_data['Minat Keorganisasian']}")
                    st.write(f"**Minat Keagamaan:** {student_data['Minat Keagamaan']}")
                
                st.write(f"**Rekomendasi Sistem:** {student_data['Ekskul Pilihan']}")
                
                # Confirmation options
                col1, col2 = st.columns(2)
                with col1:
                    confirm = st.radio("Konfirmasi Pilihan", ["Setuju dengan Rekomendasi", "Ubah Pilihan"])
                
                with col2:
                    if confirm == "Ubah Pilihan":
                        new_ekskul = st.selectbox("Pilih Ekstrakurikuler", ['Futsal', 'Hizbul Wathan', 'Tapak Suci', 'Tahfizh Quran'])
                    else:
                        new_ekskul = student_data['Ekskul Pilihan']
                
                submit_button = st.form_submit_button("Konfirmasi")
            
            if submit_button:
                # Update status
                data_handler.update_status(selected_student, "Terkonfirmasi", new_ekskul)
                st.success(f"Data siswa {student_data['Nama']} telah dikonfirmasi dengan ekstrakurikuler {new_ekskul}!")
                st.rerun()
    
    elif choice == "Lihat Dataset":
        st.markdown("<div class='card'><h3>Dataset Latih</h3></div>", unsafe_allow_html=True)
        
        st.dataframe(data)
        
        # Option to download dataset
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Dataset",
            data=csv,
            file_name='dataset_ekskul.csv',
            mime='text/csv'
        )
    
    elif choice == "Tambah Data":
        st.markdown("<div class='card'><h3>Tambah Data Latih Baru</h3></div>", unsafe_allow_html=True)
        
        with st.form("add_data_form"):
            id_siswa = st.text_input("ID Siswa")
            nama_siswa = st.text_input("Nama Siswa")
            kelas_siswa = st.selectbox("Kelas", ["X IPA 1", "X IPA 2", "X IPS 1", "X IPS 2", "XI IPA 1", "XI IPA 2", "XI IPS 1", "XI IPS 2", "XII IPA 1", "XII IPA 2", "XII IPS 1", "XII IPS 2"])
            minat_olahraga = st.slider("Minat Olahraga", 1, 5, 3, key="add_olahraga")
            minat_keorganisasian = st.slider("Minat Keorganisasian", 1, 5, 3, key="add_keorganisasian")
            minat_keagamaan = st.slider("Minat Keagamaan", 1, 5, 3, key="add_keagamaan")
            ekskul_pilihan = st.selectbox("Ekskul Pilihan", ['Futsal', 'Hizbul Wathan', 'Tapak Suci', 'Tahfizh Quran'])
            
            submitted = st.form_submit_button("Tambah Data")
            
            if submitted:
                # Add data
                updated_data = data_handler.add_data_with_status(
                    id_siswa=id_siswa,
                    nama=nama_siswa,
                    kelas=kelas_siswa,
                    minat_olahraga=minat_olahraga,
                    minat_keorganisasian=minat_keorganisasian,
                    minat_keagamaan=minat_keagamaan,
                    ekskul_pilihan=ekskul_pilihan,
                    status="Terkonfirmasi"
                )
                
                st.success("Data berhasil ditambahkan!")
                st.dataframe(updated_data)
    
    elif choice == "Kelola Akun":
        st.markdown("<div class='card'><h3>Kelola Akun Guru</h3></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='card'>
            <h4>Informasi Akun</h4>
            <p><strong>Username:</strong> admin</p>
            <p><strong>Role:</strong> Guru</p>
            <p><strong>Status:</strong> Aktif</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
<div class='card'>
    <h4>Statistik Sistem</h4>
    <p><strong>Total Siswa:</strong> {len(data)}</p>
    <p><strong>Siswa Terkonfirmasi:</strong> {len(data[data['Status'] == 'Terkonfirmasi'])}</p>
    <p><strong>Menunggu Konfirmasi:</strong> {len(data[data['Status'] == 'Menunggu Konfirmasi'])}</p>
</div>
""", unsafe_allow_html=True)


# Navigation
if st.session_state['page'] == 'main':
    main_page()
elif st.session_state['page'] == 'recommend':
    recommendation_page()
elif st.session_state['page'] == 'guru_login':
    guru_login_page()
elif st.session_state['page'] == 'guru_dashboard':
    teacher_dashboard()