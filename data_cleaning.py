import pandas as pd

def clean_data():
    # Load the data
    df = pd.read_csv('Open Transaction Data_2025(1).csv', encoding='latin-1')
    
    # Data Prerocessing: Remove whitespace and filter out invalid rows
    df['District'] = df['District'].astype(str).str.strip()
    df = df[df['District'].notna() & (df['District'] != 'nan') & (df['District'] != 'nan')]
    
    # State Mapping: Create a mapping from District to State based on Malaysian administrative divisions
    state_mapping = {
        # Johor
        'Johor Bahru': 'Johor', 'Batu Pahat': 'Johor', 'Muar': 'Johor', 'Kulai': 'Johor', 'Kluang': 'Johor', 
        'Kota Tinggi': 'Johor', 'Pontian': 'Johor', 'Segamat': 'Johor', 'Tangkak': 'Johor', 'Mersing': 'Johor',
        # Kedah
        'Kota Setar': 'Kedah', 'Kuala Muda': 'Kedah', 'Kulim': 'Kedah', 'Kubang Pasu': 'Kedah', 'Langkawi': 'Kedah',
        'Padang Terap': 'Kedah', 'Pendang': 'Kedah', 'Pokok Sena': 'Kedah', 'Sik': 'Kedah', 'Yan': 'Kedah', 'Bandar Baru': 'Kedah', 'Baling': 'Kedah',
        # Kelantan
        'Bachok': 'Kelantan', 'Besut': 'Kelantan', 'Gua Musang': 'Kelantan', 'Jeli': 'Kelantan', 'Kota Bahru': 'Kelantan',
        'Kuala Krai': 'Kelantan', 'Machang': 'Kelantan', 'Pasir Mas': 'Kelantan', 'Pasir Puteh': 'Kelantan', 'Tanah Merah': 'Kelantan', 'Tumpat': 'Kelantan',
        # Melaka
        'Melaka Tengah': 'Melaka', 'Alor Gajah': 'Melaka', 'Jasin': 'Melaka',
        # Negeri Sembilan
        'Jelebu': 'Negeri Sembilan', 'Jempol': 'Negeri Sembilan', 'Kuala Pilah': 'Negeri Sembilan', 'Port Dickson': 'Negeri Sembilan', 
        'Rembau': 'Negeri Sembilan', 'Seremban': 'Negeri Sembilan', 'Tampin': 'Negeri Sembilan',
        # Pahang
        'Kuantan': 'Pahang', 'Pekan': 'Pahang', 'Temerloh': 'Pahang', 'Bentong': 'Pahang', 'Bera': 'Pahang', 'Jerantut': 'Pahang',
        'Lipis': 'Pahang', 'Maran': 'Pahang', 'Raub': 'Pahang', 'Rompin': 'Pahang', 'DAERAH KECIL MUADZAM SHAH': 'Pahang', 'Cameron Highland': 'Pahang',
        # Perak
        'Kinta': 'Perak', 'Larut Matang': 'Perak', 'Bagan Datuk': 'Perak', 'Batang Padang': 'Perak', 'Hilir Perak': 'Perak',
        'Hulu Perak': 'Perak', 'Kampar': 'Perak', 'Kerian': 'Perak', 'Kuala Kangsar': 'Perak', 'Manjung': 'Perak', 'Muallim': 'Perak', 'Perak Tengah': 'Perak', 'Selama': 'Perak',
        # Perlis
        'Perlis': 'Perlis',
        # Penang
        'Barat Daya': 'Penang', 'Seberang Perai Selatan': 'Penang', 'Seberang Perai Tengah': 'Penang', 'Seberang Perai Utara': 'Penang', 'Timur Laut': 'Penang',
        # Sabah
        'Kota Kinabalu': 'Sabah', 'Tawau': 'Sabah', 'Sandakan': 'Sabah', 'Kota Marudu': 'Sabah', 'Keningau': 'Sabah', 'Papar': 'Sabah',
        'Putatan': 'Sabah', 'Ranau': 'Sabah', 'Semporna': 'Sabah', 'Sipitang': 'Sabah', 'Tenom': 'Sabah', 'Tuaran': 'Sabah', 'Kinabatangan': 'Sabah', 'Labuk Sugut': 'Sabah', 'Kota Belud': 'Sabah', 'Kudat': 'Sabah', 'Kunak': 'Sabah', 'Penampang': 'Sabah', 'Beaufort': 'Sabah', 'Lahad Datu': 'Sabah',
        # Sarawak
        'Kuching': 'Sarawak', 'Miri': 'Sarawak', 'Sibu': 'Sarawak', 'Bintulu': 'Sarawak', 'Samarahan': 'Sarawak', 'Serian': 'Sarawak', 
        'Betong': 'Sarawak', 'Limbang': 'Sarawak', 'Mukah': 'Sarawak', 'Sarikei': 'Sarawak', 'Sri Aman': 'Sarawak', 'Kapit': 'Sarawak',
        'Bahagian Bintulu': 'Sarawak', 'Bahagian Kuching': 'Sarawak', 'Bahagian Miri': 'Sarawak', 'Bahagian Samarahan': 'Sarawak', 'Bahagian Serian': 'Sarawak', 'Bahagian Sibu': 'Sarawak', 'Bahagian Betong': 'Sarawak', 'Bahagian Limbang': 'Sarawak', 'Bahagian Mukah': 'Sarawak', 'Bahagian Sarikei': 'Sarawak', 'Bahagian Sarikie': 'Sarawak', 'Bahagian Sri Aman': 'Sarawak', 'Bahagian Kapit': 'Sarawak',
        # Selangor
        'Petaling': 'Selangor', 'Klang': 'Selangor', 'Hulu Langat': 'Selangor', 'Gombak': 'Selangor', 'Sepang': 'Selangor', 'Kuala Langat': 'Selangor', 'Hulu Selangor': 'Selangor', 'Sabak Bernam': 'Selangor', 'Kuala Selangor': 'Selangor',
        # Terengganu
        'Dungun': 'Terengganu', 'Hulu Terengganu': 'Terengganu', 'Kemaman': 'Terengganu', 'Kuala Nerus': 'Terengganu', 'Kuala Terengganu': 'Terengganu', 'Marang': 'Terengganu', 'Setiu': 'Terengganu',
        # Wilayah
        'Kuala Lumpur': 'Wilayah Persekutuan', 'Putrajaya': 'Wilayah Persekutuan', 'Labuan': 'Wilayah Persekutuan'
    }
    
    df['State'] = df['District'].map(state_mapping).fillna('Uncategorized')
    
    # Clean price column 
    df['Price_Num'] = pd.to_numeric(df['Transaction Price  '].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce').fillna(0)
    
  # Merge with population data
    print("正在合并人口数据...")
    pop_df = pd.read_csv('population_malaysia_mclean(1).csv')
    pop_df.columns = pop_df.columns.str.strip() 

    pop_df = pop_df.rename(columns={'state': 'State'})
    
    pop_df['State'] = pop_df['State'].astype(str).str.strip().str.title()
    df['State'] = df['State'].astype(str).str.strip().str.title()
    
    final_df = pd.merge(df, pop_df, on='State', how='left')
    final_df['age'] = final_df['age'].fillna('Unknown')
    final_df['ethnicity'] = final_df['ethnicity'].fillna('Unknown')
    
    # Save the cleaned and merged dataset
    final_df.to_pickle('final_dataset.pkl')
    print("清洗与合并完成，已生成 final_dataset.pkl")
    
if __name__ == "__main__":
    clean_data()