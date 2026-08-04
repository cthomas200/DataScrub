import pandas as pd 

def loadFile(file): 
    name = file.name.lower()
    try:
        if name.endswith('.csv'):
            try:
                df = pd.read_csv(file)
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding='latin-1')
        elif name.endswith('.json'):
                df = pd.read_json(file)
        elif name.endswith('.xlsx'):
            df = pd.read_excel(file, engine='openpyxl', sheet_name=0)
        else: 
            return None, f'Unsupported file type: {file.name}'
        return df, ''
    except Exception as e: 
        return None, str(e)