import pandas as pd



def fill_missing(df, col, strat="Unknown"):
    if col not in df.columns:
        return df
    
    if df[col].isnull().sum() == 0:
        return df
    
    if df[col].dtype == 'object':
        fill = df[col].mode()[0] if not df[col].mode().empty else strat
        df[col] = df[col].fillna(fill)
    else:
        if strat == 'mean':
            fill = df[col].mean()
        elif strat == 'mode':
            fill = df[col].mode()[0]
        elif strat == 'median':
            fill = df[col].median()
        else:
            fill = 0
        df[col] = df[col].fillna(fill)
    return df

def drop_duplicates(df):
    return df.drop_duplicates()

def convert_dtype(df, col, target):
    if col in df.columns:
        try: 
            df[col] = df[col].astype(target)
        except Exception:
            pass
    return df 

def fix_outliers(df, col, strat):

    copied = df.copy()
    if col not in copied:
        return copied
    
    q1 = copied[col].quantile(0.25)
    q3 = copied[col].quantile(0.75)
    iqr = q3 - q1
    lower_bnd = q1 - iqr * 1.5
    upper_bnd = q3 + iqr * 1.5

    if strat == 'cap':
        copied[col] = copied[col].clip(lower_bnd, upper_bnd)
    elif strat == 'drop':
        copied = copied[(copied[col] >= lower_bnd) & (copied[col] <= upper_bnd)]
    return copied 



def apply_fixes(org_df, approved):
    cleaned = org_df.copy()

    tot_missing_before = cleaned.isnull().sum().sum()
    tot_duplicates_before = len(cleaned)

    dispatch = { 
        "Missing values": lambda df, fix: fill_missing(df, fix['col']),
        "Duplicate values": lambda df, fix: drop_duplicates(df),
        "Data Type Issue": lambda df, fix: convert_dtype(df, fix['col'], 'float64' ),
        "Outlier": lambda df, fix: fix_outliers(df, fix['col'], 'cap')

    }

    applied = []
    skipped = []

    for fix in approved:
        issue_type = fix.get('issue_type')
        if issue_type in dispatch:
            try: 
                cleaned = dispatch[issue_type](cleaned, fix)
                applied.append(fix)
            except Exception as e:
                skipped.append({**fix, 'reason': str(e)})
        else:
            skipped.append({**fix, 'reason': 'No handler for issue type'})
    
    return cleaned, applied, skipped, tot_missing_before, tot_duplicates_before