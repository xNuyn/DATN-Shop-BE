import pandas as pd

# Đường dẫn file Excel đầu vào
excel_file = 'Subproduct.xlsx'

# Đường dẫn file CSV đầu ra
csv_file = 'test.csv'

# Đọc file Excel
df = pd.read_excel(excel_file)

# Ép kiểu sang int cho một số cột (ví dụ: 'product_id', 'stock', 'price')
columns_to_convert = ['subproduct_old_price']
for col in columns_to_convert:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# Ghi dataframe ra file CSV
df.to_csv(csv_file, index=False)
