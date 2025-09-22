import pandas as pd
import re

## Cleans and preprocesses data in the DataFrame 'df'.
# Performs several cleaning and text extraction operations, such as removing diacritics, normalizing text, 
# and extracting specific patterns (e.g., 'XP' numbers, volume, ISSN, ISBN, DOI, issue, year, page start, page end, etc.).
# Additional cleaning steps, such as stripping, replacing certain words, and handling author names, are also applied.
# Column names are updated for clarity.
# The cleaned DataFrame is returned.
# @param df: The input DataFrame with raw data.
# @return: The cleaned and preprocessed DataFrame.
#
def clean_data(df):
    df = pre_extraction_cleaning(df)
    df = extract_and_remove_1(df)
    df = additional_cleaning_1(df)
    df = extract_and_remove_2(df)
    df = additional_cleaning_2(df)
    df = extract_and_remove_3(df)
    df = handle_missing_titles(df)
    df = final_cleaning(df)
    df = rename_and_drop_columns(df)
    print ('done cleaning') 

    return df

## Extracts a pattern from a given text using regular expressions and removes it.
# @param text: The string with the characters to check.
# @param pattern: The regular expression pattern to search for.
# @param group_index: The index of the group to extract from the pattern match.
# @return: A tuple containing the matched text (or None if not found) and the modified text.
#
def extract_and_remove_pattern(text, pattern, group_index):
    match = re.search(pattern, text)
    if match:
        matched_text = match.group(group_index)
        modified_text = re.sub(pattern, '', text)
        return matched_text, modified_text
    else:
        return None, text

## Extracts page numbers from a given text.
# @param text: The string with the page numbers to extract.
# @return: A tuple containing the first page number, the second page number, and the modified text.
#
def extract_and_remove_page(text):
    match = re.search(r'(\d+)\s*[- ]\s*(\d+)', text)
    if match:
        first = match.group(1)
        second = match.group(2)
        modified_text = re.sub(r'(\d+)\s*[- ]\s*(\d+)', '', text)
        return first, second, modified_text
    else:
        match = re.search(r'page (\d+)', text)
        if match:
            first = match.group(1)
            modified_text = re.sub(r'page (\d+)', '', text)
            return first, first, modified_text
        else:
            return None, None, text

## Extracts month and day from a given text.
# @param text: The string with the date information to extract.
# @return: A tuple containing the day, month, and modified text.
#
def extract_and_remove_month(text):
    pattern = r'(\d{1,2}(?:th|\.)?)\s+(january|february|march|april|may|june|july|august|september|october|november|december)|' \
              r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}(?:th|\.)?)'
    match = re.search(pattern, text)
    if match:
        if match.group(1):
            day = match.group(1)
            month = match.group(2)
        else:
            month = match.group(3)
            day = match.group(4)
        modified_text = re.sub(pattern, '', text)
        return day, month, modified_text
    else:
        pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december)'
        match = re.search(pattern,text)
        if match:
            month = match.group(0)
            modified_text = re.sub(pattern, '', text)
            return None, month, modified_text
        return None, None, text

## Extracts URLs from a given text.
# @param text: The string with the URLs to extract.
# @return: A tuple containing the extracted URL and the modified text.
#
def extract_and_remove_url(text):
    pattern = r'url\S*[ \t>,"]*'
    match = re.search(pattern, text)
    if match:
        url = match.group(0)
        modified_text = re.sub(pattern, '', text)
        return url, modified_text
    else:
        pattern = r'www[^ ,">]*'
        match = re.search(pattern,text)
        if match:
            url = match.group(0)
            modified_text = re.sub(pattern, '', text)
            return url, modified_text
        else:
            return None, text

## Adds extra digits to the 'page end' value if needed.
# This function is used to fix 'page end' values when they are shorter than 'page start'.
# @param row: The row containing 'page start' and 'page end' values.
# @return: The corrected 'page end' value.
#
def add_extra_digits(row):
    page_start = row['page start']
    page_end = row['page end']
    if pd.notna(page_start) and pd.notna(page_end):
        if int(page_start) > int(page_end):
            extra_digits = page_start[:len(page_start) - len(page_end)]
            new_page_end = extra_digits + page_end
            return new_page_end
        else:
            return page_end
    
    return page_end

## Cleans a string by removing a leading dot (.) if present.
# @param text: The string to be cleaned.
# @return: The text with the leading dot removed if present.
#
def clean_point(text):
    if text.startswith("."):
        text = text[1:]
        return text
    else:
        return text

## Keeps only alphanumeric characters in a string and removes any other characters.
# @param text: The string to be processed.
# @return: The string with only alphanumeric characters.
#
def keep_alphanumeric(text):
    if text is not None:
        alphanumeric_text = re.sub(r'[^a-zA-Z0-9]', '', text)
        return alphanumeric_text
    else:
        return text

## Cleans a text by removing specific patterns and extra spaces.
# @param text: The text to be cleaned.
# @return: The cleaned text with patterns removed and extra spaces removed.
#
def clean_text(text):
    text = re.sub(r'[()<>]', '', text)  # Remove parentheses and angle brackets
    text = re.sub(r'vol\.|no\.|s-s| -|page|,|\.\.', '', text)  # Remove specific patterns
    text = re.sub(r' +', ' ', text)  # Remove multiple spaces
    text = text.strip()  # Remove leading/trailing whitespace
    return text

## Extracts and removes an author from the input text, preserving the rest of the text.
# The author is typically separated by 'et al', ':', or ';'.
# @param text: The text to extract the author from.
# @return: A tuple containing the extracted author (if found) and the modified text with the author removed.
#
def extract_and_remove_author(text):
    delimiters = ['et al', ':', ';']
    
    for delimiter in delimiters:
        index = text.find(delimiter)
        if index != -1:
            author = text[:index].strip()
            modified_text = text[index + len(delimiter):].strip()
            return author, modified_text

    return None, text

## Extracts and removes the journal name from the input text.
# The journal name is usually located at the beginning of the text and followed by a period.
# @param text: The text containing the journal name.
# @return: A tuple containing the extracted journal name (if found) and the modified text with the journal name removed.
#
def extract_and_remove_journal(text):
    # If the text is longer than 50 characters, check for a period (.) and extract the journal name if found
    if len(text) > 50:
        period_index = text.find('.')
        if period_index != -1:
            result = text[period_index + 1:]
            modified_text = text.replace(result, '')
            return result, modified_text
        # If a period is not found, return None for the journal name and the original text
        else:
            return None, text
    # If the text is shorter than 50 characters, return the entire text as the journal name and None for the modified text
    else:
        return text, None

## Extracts and removes non-alphabetic and non-space characters from the input text.
# Additionally, it removes 'et al', extra spaces, and trims the text.
# @param text: The text to be processed.
# @return: The text with non-alphabetic and non-space characters removed and cleaned.
#
def text_left(text):
    if text is not None:
        # Remove non-alphabetic and non-space characters
        modified_text = re.sub(r'[^a-zA-Z\s]', '', text)
        modified_text = modified_text.replace('et al', '')  # Remove 'et al'
        modified_text = modified_text.replace('  ', ' ')  # Remove extra spaces
        modified_text = modified_text.strip()  # Trim leading and trailing spaces
        if modified_text == '' or len(modified_text) <= 2:
            modified_text = None
        return modified_text
    return None

def pre_extraction_cleaning(df):
    replacements = {
        '  ': ' ',
        'pages': 'page',
        'seiten': 'page',
        'seite': 'page',
        'pp.': 'page',
        'volume ': 'vol.',
        'jan.': 'january',
        'feb.': 'february',
        'mar.': 'march',
        'apr.': 'april',
        'jun.': 'june',
        'jul.': 'july',
        'juli': 'july',
        'aug.': 'august',
        'sep.': 'september',
        'sept.': 'september',
        'oct.': 'october',
        'okt.': 'october',
        'oktober': 'october',
        'nov.': 'november',
        'dec.': 'december',
        'nr. ': 'no.'
    }

    df['npl_biblio'] = (
        df['npl_biblio']
        .str.strip()  # Remove leading/trailing whitespace
        .str.normalize('NFKD')  # Normalize unicode (e.g., é → e +  ́)
        .str.encode('ascii', errors='ignore')  # Remove diacritics by ignoring non-ASCII
        .str.decode('utf-8')  # Decode bytes back to string
        .str.lower()  # Convert to lowercase
        .replace(replacements, regex=False)
    )

    return df

def extract_and_remove_1(df):
    pattern_extracts = [
        ('XP', r'xp-?(\d{9})', 1),
        ('volume', r'vol\.?\s?(\d+)', 1),
        ('ISSN', r'issn\s?:?\s?(\d{4}-\d{4})', 1),
        ('ISBN', r'isbn\s?:?\s?(\d{4}-\d{4})', 1),
        ('DOI', r'doi\s?:?\s?([^, "\n]+)', 1),
        ('issue', r'no\. (\d+)', 1),
        ('year', r'\b(19\d{2}|20[01]\d|2022|2023)\b', 0),
        ('rest number', r'[-+]?\d*\.\d+|\d+', 0)
    ]

    for col, pattern, group in pattern_extracts:
        df[col], df['npl_biblio'] = zip(*df['npl_biblio'].apply(
            lambda x: extract_and_remove_pattern(x, pattern, group)
        ))

    df['page start'], df['page end'], df['npl_biblio'] = zip(*df['npl_biblio'].apply(extract_and_remove_page))
    df['day'], df['month'], df['npl_biblio'] = zip(*df['npl_biblio'].apply(extract_and_remove_month))
    df['url'], df['npl_biblio'] = zip(*df['npl_biblio'].apply(extract_and_remove_url))

    return df

def additional_cleaning_1(df):
    df['npl_biblio'] = df['npl_biblio'].apply(clean_text)
    return df

def extract_and_remove_2(df):
    df['title'], df['npl_biblio'] = zip(*df['npl_biblio'].apply(lambda x: extract_and_remove_pattern(x, r"'(.*?)'", 0)))
    df['author'], df['npl_biblio'] = zip(*df['npl_biblio'].apply(extract_and_remove_author))

    return df

def additional_cleaning_2(df):
    replacements = {
        'et al': '',
        ':': ''
    }

    df['npl_biblio'] = df['npl_biblio'].replace(replacements, regex=False)
    df['author'] = df['author'].replace({'et al': ''}, regex=False)
    df['npl_biblio'] = df['npl_biblio'].apply(clean_point).str.strip()

    return df

def final_cleaning(df):
    for col in ['npl_biblio', 'title', 'author', 'journal', 'url']:
        df[col] = df[col].apply(text_left)

    df['rest_text'] = df['npl_biblio']
    df['npl_biblio'] = None

    df['DOI'] = df['DOI'].str.replace('doi:', '', regex=False).str.replace('doi', '', regex=False)
    df['DOI'] = df['DOI'].apply(keep_alphanumeric)

    url_replacements = {'url': '', 'http': '', 'www': '', ' ': ''}
    df['url'] = df['url'].replace(url_replacements, regex=False)

    df['page end'] = df.apply(add_extra_digits, axis=1)

    for col in ['day', 'page start', 'page end']:
        df[col] = df[col].str.replace('th', '', regex=False).str.replace('.', '', regex=False)
        df[col] = df[col].apply(
            lambda x: x if x is None or len(x) != 2 else {
                '01': '1', '02': '2', '03': '3', '04': '4',
                '05': '5', '06': '6', '07': '7', '08': '8', '09': '9'
            }.get(x, x)
        )

    return df

def rename_and_drop_columns(df):
    df.rename(columns={'year': 'publication_year', 'page start': 'page_start', 'page end': 'page_end', 'day': 'publication_day', 'month': 'publication_month', 
                       'rest number': 'rest_number', 'title': 'paper_title', 'author': 'author_names', 'journal': 'journal_name', 'url': 'URL'}, inplace=True)
    df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

    return df

def handle_missing_titles(df):
    mask = df['title'].isna()
    df.loc[mask, 'title'] = df.loc[mask, 'npl_biblio']
    df['npl_biblio'] = df['npl_biblio'].where(~mask, '')
    return df

def extract_and_remove_3(df):
    df['journal'], df['npl_biblio'] = zip(*df['npl_biblio'].apply(extract_and_remove_journal))
    return df