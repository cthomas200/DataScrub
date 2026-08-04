import streamlit as st 
from core.loader import loadFile
from core.analyzer import scan
import pandas as pd
from core.ai_advisor import ai_suggestions
from core.cleaner import apply_fixes
import io

st.set_page_config(page_title='DataScruber', layout='wide')
st.title('File Upload & Preview')
st.markdown('Upload CSV, Excel, JSON file below')

uploaded_file = st.file_uploader('Choose a file to process', type=['csv', 'xlsx', 'json'])
if uploaded_file is not None: 
    df, error = loadFile(uploaded_file)
    if error: 
        st.error(f'Error loading file {error}')
    else:
        st.session_state['df'] = df
        st.success(f'Successfully loaded {uploaded_file.name}')
        col1, col2 = st.columns(2) #Load two containers to preview file selected
        col1.metric('Total Rows Found', df.shape[0]) 
        col2.metric('Total Columns Found', df.shape[1])
        st.write('Interactive Preview (Only First 5 Rows)')
        st.dataframe(df.head(), use_container_width=True)
        
        issues_lst = scan(df) #Returns list of quality issues
        st.subheader('Data Quality Issues')
        if issues_lst: #Display  if scan function returns list
            st.dataframe(pd.DataFrame(issues_lst))

            st.subheader('AI Suggested Fixes')
            st.write('Takes a few seconds to analyze')

            fixes, ai_error = ai_suggestions(df, issues_lst) #Uses claude API to fetch suggestions
            if ai_error:
                st.error(f'AI Error: {ai_error}')
            elif fixes:
                for fix in fixes:
                    with st.container(border=True):
                        col1, col2 = st.columns([3,1])
                        col1.markdown(f"**{fix['issue_type']}** - `{fix['column']}`")
                        col2.markdown(f"Risk: `{fix['risk']}`")
                        st.write(fix['reasoning'])
                        st.caption(f"Action: {fix['recommended_action']}")

                        approved = f"approve_{fix['column']}_{fix['issue_type']}" #generates unique key to track each approved fix
                        if st.button('Apply fix', key=approved):
                            if 'approved_fixes' not in st.session_state:
                                st.session_state['approved_fixes'] = [] #initialize list if not in session state
                            st.session_state['approved_fixes'].append(fix) #append each approved fix to session state
                            st.success('Fix queued!')
            else:
                st.info('No fixes suggested')
            #Display Approved fixes 
            if st.session_state.get('approved_fixes'):
                st.divider()
                st.subheader(f"Approved Fixes ({len(st.session_state['approved_fixes'])})")
                st.dataframe(pd.DataFrame(st.session_state['approved_fixes']))

                if st.button('Apply All Approved Fixes'):
                    cleaned, applied, skipped, missing_before, dupes_before = apply_fixes(
                        st.session_state['df'],
                        st.session_state['approved_fixes'])
                    st.session_state['cleaned'] = cleaned
                    st.session_state['applied'] = applied
                    st.session_state['skipped'] = skipped
                #Display Original and Cleaned Dataset
                if 'cleaned' in st.session_state:
                    st.divider()
                    st.subheader('Before vs. After')
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('**Original**')
                        st.dataframe(st.session_state['df'].head(), use_container_width=True)
                        st.caption(f"Shape: {st.session_state['df'].shape}")
                    with col2:
                        st.markdown("**Cleaned**")
                        st.dataframe(st.session_state['cleaned'].head(), use_container_width=True)
                        st.caption(f"Shape: {st.session_state['cleaned'].shape}")

                    st.divider()
                    csv = st.session_state['cleaned'].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label= 'Download Cleaned CSV',
                        data = csv,
                        file_name= 'cleaned_data.csv',
                        mime= 'text/csv'
                    )
                    
                    json_data = st.session_state['cleaned'].to_json(orient='records')
                    st.download_button(
                        label = 'Download Cleaned JSON',
                        data = json_data,
                        file_name = 'cleaned_data.json',
                        mime = 'application/json'
                    )
                    
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        st.session_state['cleaned'].to_excel(writer, index=False, sheet_name='Sheet1')
                    
                    st.download_button(
                        label = 'Download Cleaned Excel Sheet',
                        data = buffer.getvalue(),
                        file_name = 'cleaned_data.xlsx',
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    if st.session_state.get('skipped'):
                        st.warning(f"{len(st.session_state['skipped'])} fixes were skipped")
                        st.dataframe(pd.DataFrame(st.session_state['skipped']))



        else:
            st.write('No Data Quality Issues Detected')
            st.write('No Suggested Fixes')

        
else:
    st.info('Please upload .csv, .xlsx, or .json file above.')
        