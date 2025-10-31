import pandas as pd
from io import BytesIO
# import datetime
import datetime as dt


def excel_to_dict(file_path, sheet_name=0, start_row=0, end_row=None):

    try:

        if end_row is not None:
            nrows = end_row - start_row
        else:
            nrows = None  # read 
        
        print("no rows :", nrows)
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            skiprows=start_row-1,
            nrows=nrows,
            date_format='%Y-%m-%d'
        )

        # Drop any rows that ended up being completely empty (e.g., due to extra lines
        # or miscalculated skip counts)
        df.dropna(how='all', inplace=True)

        # Convert the resulting DataFrame into a list of dictionaries (records format).
        # 'records' format: [{'col1': val1, 'col2': val2}, {'col1': val3, 'col2': val4}, ...]
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

   
        raw_dicts = df.to_dict('records')
        cleaned_dicts = []


        for record in raw_dicts:
            new_record = {}
            for key, value in record.items():

                # ✅ Convert datetime/date values to formatted string
                if isinstance(value, (dt.datetime, pd.Timestamp, dt.date)):
                    try:
                        new_record[key] = value.strftime('%Y-%m-%d')
                    except (ValueError, AttributeError):
                        new_record[key] = None

                # ✅ Convert NaT/NaN to None
                elif pd.isna(value):
                    new_record[key] = None

                else:
                    new_record[key] = value

            cleaned_dicts.append(new_record)

        return cleaned_dicts

    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return []
    except ValueError as e:
        print(f"Error reading Excel sheet: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
 