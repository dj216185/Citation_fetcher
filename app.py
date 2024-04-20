import streamlit as st
import pandas as pd
import requests
import time
import base64

def fetch_citations(dois, styles, progress_bar):
    citations = []
    for i, (doi, style) in enumerate(zip(dois, styles)):
        if not doi.startswith('#'):
            url = f'https://citation.crosscite.org/format?doi={doi}&style={style}&lang=en-US'
            response = requests.get(url)
            if response.status_code == 200:
                citations.append(response.text)
        progress_bar.progress((i + 1) / len(dois))
    return citations


def replace_special_chars(df):
    problem_encodings = {
        'Ã¢Â€Âœ': '"', 
        'Ã¢Â€Â': '"', 
        'â': '"', 
        'â': '"', 
        'Ã¢Â€Â™': "'",  # apostrophe
        'Ã¢Â€Â“': '–',  # dash
        'Ã¢Â€Â¦': '...',  # ellipsis
        'Ã¢Â€Â“': '-',  # another type of dash
        'ÃƒÂ³': 'ó',  # assuming this should be replaced with 'ó'
        'ÃƒÂ': 'à',  # assuming this should be replaced with 'à'
        'Ã…Â›': 'ś',  # assuming this should be replaced with 'ś'
        'Ã…Âº': 'ź',  # assuming this should be replaced with 'ź'
        'Ã‚Â': 'Â',  # assuming this should be replaced with 'Â'
        'Ã…ÂŸ': 'ş'  # assuming this should be replaced with 'ş'
    }

    for encoding, replacement in problem_encodings.items():
        df['Citation'] = df['Citation'].apply(lambda x: x.replace(encoding, replacement))
        
    # Add error handling for decoding errors
    df['Citation'] = df['Citation'].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8', 'ignore'))
    return df

def main():
    st.title('Citation Fetcher')
    
    uploaded_file = uploaded_file = st.file_uploader("Drop a file with DOI links", type=["csv", "xls", "xlsx", "tsv", "txt", "json"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        dois = df['DOI'].tolist()

        # Add a dropdown for citation styles
        styles = ['ieee', 'apa', 'vancouver', 'chicago-author-date', 'elsevier-harvard', 'modern-language-association']
        selected_style = st.selectbox('Select a citation style:', styles)

        st.write("Fetching citations. This may take 5-10 minutes depending on the file size.")
        progress_bar = st.progress(0)
        # Use the selected style for all DOIs
        citations = fetch_citations(dois, [selected_style]*len(dois), progress_bar)
        new_df = pd.DataFrame(citations, columns=['Citation'])
        new_df = replace_special_chars(new_df)

        final_df = new_df
        
        st.write(final_df)
        
        if st.button('Download Dataframe as CSV'):
            csv = final_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  
            href = f'<a href="data:file/csv;base64,{b64}" download="citations.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
