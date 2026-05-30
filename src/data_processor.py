import pandas as pd
import os


class DataProcessor:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def clean_missing_and_duplicates(self):
        self.df = self.df.drop_duplicates().dropna()

    def normalize_dtypes(self):
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df['Time']=pd.to_datetime(self.df['Time'],format='%I:%M:%S %p')
        currency_cols = ['Unit price', 'Tax 5%', 'Sales', 'cogs', 'gross income']
        for i in currency_cols:
            self.df[i] = self.df[i].astype(float)

    def feature_engineering(self):
        self.df['Day']=self.df['Date'].dt.day
        self.df['Month'] = self.df['Date'].dt.month
        self.df['Year'] = self.df['Date'].dt.year
        self.df['Day of week'] = self.df['Date'].dt.day_name()
        self.df['Hour']=self.df['Time'].dt.hour


    def save_processed_data(self, save_path: str = '../data/processed/cleaned_supermarket_data.csv'):
        #os.makedirs(os.path.dirname(save_path), exist_ok=True)
        self.df.to_csv(save_path, index=False)
        print(f"Đã lưu dữ liệu làm sạch tại: {save_path}")

    def run_pipeline(self) -> pd.DataFrame:
        self.clean_missing_and_duplicates()
        self.normalize_dtypes()
        self.feature_engineering()
        return self.df