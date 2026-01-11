import streamlit as st
import re
from collections import Counter
import io

def extract_text_from_file(uploaded_file):
    """Extract text from different file types"""
    text_content = ""
    
    try:
        file_type = uploaded_file.type
        
        if file_type == "application/pdf":
            # Handle PDF files
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            except ImportError:
                st.error("PyPDF2 not installed. Install with: pip install PyPDF2")
                return ""
                
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Handle DOCX files
            try:
                import docx
                doc = docx.Document(uploaded_file)
                text_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            except ImportError:
                st.error("python-docx not installed. Install with: pip install python-docx")
                return ""
                
        elif file_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            # Handle Excel files
            try:
                import pandas as pd
                df = pd.read_excel(uploaded_file)
                text_content = " ".join([str(cell) for cell in df.values.flatten() if pd.notna(cell)])
            except ImportError:
                st.error("pandas not installed. Install with: pip install pandas openpyxl")
                return ""
                
        else:
            # Handle text files (txt, md, etc.)
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            text_content = stringio.read()
            
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""
    
    return text_content

def get_keywords(text):
    """Extract keywords dynamically without duplicates or stop words"""
    if not text or len(text.strip()) < 10:
        return []
    
    # Clean and normalize text
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    
    # Comprehensive stop words list
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'among', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
        'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'one', 'two', 'three',
        'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'also', 'said', 'get', 'go', 'know',
        'make', 'way', 'take', 'come', 'see', 'time', 'use', 'first', 'last', 'long', 'great', 'little',
        'own', 'other', 'old', 'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early',
        'young', 'important', 'few', 'public', 'bad', 'same', 'able', 'back', 'each', 'good', 'new',
        'here', 'there', 'where', 'when', 'what', 'why', 'how', 'who', 'which', 'than', 'then', 'now',
        'well', 'very', 'just', 'only', 'even', 'still', 'much', 'more', 'most', 'many', 'some', 'any',
        'all', 'both', 'either', 'neither', 'each', 'every', 'another', 'such', 'no', 'not', 'yes'
    }
    
    # Filter words: longer than 2 chars, not stop words, alphabetic only, no duplicates
    filtered_words = []
    seen_words = set()
    
    for word in words:
        if (len(word) > 2 and 
            word not in stop_words and 
            word.isalpha() and 
            word not in seen_words):
            filtered_words.append(word)
            seen_words.add(word)
    
    # Count frequency and get most important words
    word_freq = Counter(filtered_words)
    
    # Dynamic number of keywords based on text length
    text_length = len(words)
    if text_length < 100:
        num_keywords = min(5, len(word_freq))
    elif text_length < 500:
        num_keywords = min(10, len(word_freq))
    elif text_length < 1000:
        num_keywords = min(15, len(word_freq))
    else:
        num_keywords = min(20, len(word_freq))
    
    # Return top keywords (words only, no frequencies shown)
    top_keywords = [word for word, freq in word_freq.most_common(num_keywords)]
    return top_keywords

def main():
    # Page configuration
    st.set_page_config(
        page_title="Keyword Extractor",
        page_icon="",
        layout="centered"
    )
    
    # Main heading
    st.title("Keyword Extractor")
    
    # File upload box
    uploaded_file = st.file_uploader(
        "",
        type=['pdf', 'docx', 'doc', 'txt', 'md', 'xlsx', 'xls'],
        help=None
    )
    
    # Process uploaded file
    if uploaded_file is not None:
        with st.spinner('Processing file...'):
            # Extract text from file
            text_content = extract_text_from_file(uploaded_file)
            
            if text_content:
                # Extract keywords
                keywords = get_keywords(text_content)
                
                if keywords:
                    # Display keywords in a clean format
                    st.markdown("### Keywords:")
                    
                    # Display keywords as badges/chips
                    keyword_html = ""
                    for keyword in keywords:
                        keyword_html += f"""
                        <span style="
                            display: inline-block;
                            background-color: #e1f5fe;
                            color: #01579b;
                            padding: 5px 12px;
                            margin: 3px;
                            border-radius: 20px;
                            font-size: 14px;
                            font-weight: 500;
                            border: 1px solid #b3e5fc;
                        ">{keyword}</span>
                        """
                    
                    st.markdown(keyword_html, unsafe_allow_html=True)
                    
                else:
                    st.warning("No keywords found in the uploaded file.")
            else:
                st.error("Could not extract text from the file.")
    
if __name__ == "__main__":
    main()