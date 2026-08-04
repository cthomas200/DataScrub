import pandas as pd
import numpy as np 


def scan(df):
    issues = []  
    totRows = len(df)

    if totRows == 0:
        return issues
    
    #Find missing values
    for col in df.columns:
        countMissing = df[col].isnull().sum()
        emptStr = 0
        whtspc = 0 
        if df[col].dtype == 'object':
            emptStr = (df[col] == "").sum()
            whtspc = (df[col].astype(str).str.isspace()).sum()
        #Calculate how severe missing values are 
        totMissing = countMissing + emptStr + whtspc 
        if totMissing > 0:
            prct = (totMissing / totRows) * 100
            if prct > 30:
                severity = 'severe'
            elif prct > 5: 
                severity = 'moderate'
            else:
                severity = 'low'
        
            issues.append({
                'type': 'Missing values',
                'column': col,
                'severity': severity,
                'count': totMissing,
                'description': f'{prct:.2f}%  missing or empty values detected'
            })
    #Find duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        issues.append({
            'type': 'Duplicate values',
            'column': 'All columns',
            'severity': 'moderate' if duplicates < (totRows * 0.1) else 'severe',
            'count': duplicates,
            'description': 'Exact full row duplicates detected.'
        })
    #Check if objects can be converted to numbers 
    for col in df.columns:
        if df[col].dtype == 'object':
            converted = pd.to_numeric(df[col], errors='coerce')
            notnumnotnull = converted.isnull().sum() - df[col].isnull().sum()

            if (notnumnotnull / totRows ) < 0.2:
                issues.append({
                    'type': 'Data Type Issue',
                    'column': col,
                    'severity': 'moderate',
                    'count': notnumnotnull,
                    'description': 'Column appear numeric but is stored as object.'
                })
    #Find outliers 
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR 
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]
        outCount = len(outliers)
        if outCount > 0:
            prctOut = (outCount / totRows) * 100
            issues.append({
                'type': 'Outlier',
                'column': col,
                'severity': 'moderate' if prctOut < 5 else 'severe',
                'count': outCount,
                'description': f'{outCount} outliers ({prctOut:.2f}%) outside IQR bounds ({lower:.2f} - {upper:.2f}).'
            })
    #Check formatting
    for col in df.select_dtypes(include=['object']).columns:
        whtspc_rows = df[df[col].astype(str).str.contains(r'^\s+|\s+$', na=False)].shape[0]
        if whtspc_rows > 0:
            issues.append({
                'type': 'Formatting',
                'column': col,
                'severity': 'low',
                'count': whtspc_rows,
                'description': 'Values contain leading or trailing whitespaces.'
            })
        #Check for inconsistent case
        if df[col].nunique() > 1:
            lwercse_nun = df[col].astype(str).str.lower().nunique()
            if lwercse_nun < df[col].nunique():
                issues.append({
                    'type': 'Formatting', 
                    'column': col,
                    'severity': 'low',
                    'count': df[col].nunique() - lwercse_nun,
                    'description': 'Mixed case inconsistencies'
                })
    return issues 

