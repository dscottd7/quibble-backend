import re


def parse_html(page_content: str) -> str:

    # Remove CSS
    css_pattern = r'\{[^{}]*\}'
    while re.search(css_pattern, page_content):
        page_content = re.sub(css_pattern, '', page_content)

    # Remove any .markup #markup or @markup
    page_content = re.sub(r'\.[\w\-]+(?:\.[\w\-]+)*', '', page_content)
    page_content = re.sub(r'[#|::|@][\w\-]+(?:\.[\w\-]+)*', '', page_content)

    # Remove any /characters
    page_content = page_content.replace('\n', '').replace('\r', '').replace('\t', '')

    # Remove content with <script> tags
    page_content = re.sub(r'<script.*?>.*?</script>', '', page_content, flags=re.DOTALL)

    # Remove html tags
    page_content = re.sub(r'<[^>]+>', '', page_content)

    # Remove white space
    page_content = re.sub(r'\s+', ' ', page_content).strip()

    return page_content
