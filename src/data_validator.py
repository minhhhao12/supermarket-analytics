import pandas as pd


class DataValidator:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def validate_cols(self) -> list:
        errors = []
        cols = ['Invoice ID','Branch','City','Customer type','Gender','Product line','Unit price','Quantity','Tax 5%','Sales','Date','Time','Payment','cogs','gross margin percentage','gross income','Rating']
        missing_cols = []
        for col in cols:
            if col not in self.df.columns:
                missing_cols.append(col)

        if missing_cols:
            errors.append(
                f"File dữ liệu bị thiếu các cột bắt buộc: {', '.join(missing_cols)}"
            )
        return errors

    def validate_invalid_data(self) -> list:
        errors = []

        invalid_quantity = self.df[self.df["Quantity"] <= 0]
        if not invalid_quantity.empty:
            errors.append(
                f"Có {len(invalid_quantity)} dòng có Quantity <= 0. Tại dòng: {list(invalid_quantity.index[:])}"
            )
        invalid_price = self.df[self.df["Unit price"] < 0]
        if not invalid_price.empty:
            errors.append(
                f"Có {len(invalid_price)} dòng có Unit price < 0. Tại dòng: {list(invalid_price.index[:])}"
            )

        invalid_sales = self.df[self.df["Sales"] < 0]
        if not invalid_sales.empty:
            errors.append(
                f"Có {len(invalid_sales)} dòng có Sales < 0. Tại dòng: {list(invalid_sales.index[:])}"
            )
        return errors

    def check_currency_logic(self) -> list:
        errors = []
        tax = (self.df["Quantity"] * self.df["Unit price"]) * 0.05
        invalid_sales = self.df[tax == 'Tax 5%']

        if not invalid_sales.empty:
            errors.append(
                f"Có {len(invalid_sales)} dòng sai logic tiền tệ . Tại dòng: {list(invalid_sales.index[:])}"
            )

        return errors

    def run_all_validators(self):
        all_errors = []
        col_errors = self.validate_cols()
        if col_errors:
            all_errors.extend(col_errors)
            return all_errors
        all_errors.extend(self.validate_invalid_data())
        all_errors.extend(self.check_currency_logic())
        if all_errors is None:
            return None
        return all_errors