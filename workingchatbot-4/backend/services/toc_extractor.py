# services/toc_extractor.py

import re
from orchestrator import generate_answer

def extract_table_of_contents(doc_content, doc_id):
    """Extract table of contents from document content using AI analysis"""
    
    # Create a prompt to extract table of contents structure
    prompt = f"""You are an expert document analyzer. Analyze the following research paper/document content and extract a comprehensive table of contents.

Instructions:
1. Identify all major sections and subsections based on headings, titles, and document structure
2. Create a numbered hierarchical structure (1., 1.1, 1.2, 2., 2.1, etc.)
3. Include both main sections and subsections
4. Format each entry as: "NUMBER|TITLE|LEVEL" where LEVEL is 1 for main sections, 2 for subsections, 3 for sub-subsections
5. Be thorough and capture the complete document structure
6. Common research paper sections include: Abstract, Introduction, Literature Review, Methodology, Results, Discussion, Conclusion, References

Example format:
1|Introduction|1
1.1|Background|2
1.2|Problem Statement|2
2|Literature Review|1
2.1|Previous Studies|2
2.2|Research Gaps|2

Document content:
{doc_content[:4000]}...

Extract the complete table of contents in the specified format:"""

    try:
        response = generate_answer(prompt)
        
        if response and not response.startswith("❌") and not response.startswith("⚠️"):
            # Parse the AI response
            toc_entries = []
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            
            for line in lines:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        section_number = parts[0].strip()
                        section_title = parts[1].strip()
                        try:
                            level = int(parts[2].strip())
                        except ValueError:
                            level = 1
                        
                        toc_entries.append({
                            'section_number': section_number,
                            'section_title': section_title,
                            'level': level
                        })
            
            # If AI parsing worked, return the entries
            if toc_entries:
                return toc_entries
        
        # Fallback: Use regex-based extraction if AI fails
        return extract_toc_with_regex(doc_content)
        
    except Exception as e:
        print(f"TOC extraction error with AI: {e}")
        # Fallback to regex-based extraction
        return extract_toc_with_regex(doc_content)

def extract_toc_with_regex(doc_content):
    """Fallback method to extract TOC using regex patterns"""
    
    toc_entries = []
    
    # Common heading patterns in research papers
    patterns = [
        # Numbered sections (1., 2., 3.)
        r'^(\d+)\.\s*([A-Z][A-Za-z\s]+)$',
        # Subsections (1.1, 1.2, etc.)
        r'^(\d+\.\d+)\s*([A-Z][A-Za-z\s]+)$',
        # Sub-subsections (1.1.1, 1.1.2, etc.)
        r'^(\d+\.\d+\.\d+)\s*([A-Z][A-Za-z\s]+)$',
        # All caps headings
        r'^([A-Z\s]{3,})$',
        # Title case headings at start of line
        r'^([A-Z][a-z]+(?:\s[A-Z][a-z]*)*):?\s*$'
    ]
    
    lines = doc_content.split('\n')
    section_counter = 1
    
    for line in lines:
        line = line.strip()
        if len(line) < 3 or len(line) > 100:  # Skip very short or very long lines
            continue
            
        # Check numbered patterns first
        for i, pattern in enumerate(patterns[:3]):
            match = re.match(pattern, line)
            if match:
                section_number = match.group(1)
                section_title = match.group(2).strip()
                
                # Determine level based on numbering
                level = len(section_number.split('.'))
                
                toc_entries.append({
                    'section_number': section_number,
                    'section_title': section_title,
                    'level': level
                })
                break
        else:
            # Check for common research paper section titles
            common_sections = [
                'ABSTRACT', 'INTRODUCTION', 'LITERATURE REVIEW', 'METHODOLOGY', 
                'METHODS', 'RESULTS', 'DISCUSSION', 'CONCLUSION', 'CONCLUSIONS',
                'REFERENCES', 'BIBLIOGRAPHY', 'ACKNOWLEDGMENTS', 'APPENDIX'
            ]
            
            if line.upper() in common_sections:
                toc_entries.append({
                    'section_number': str(section_counter),
                    'section_title': line.title(),
                    'level': 1
                })
                section_counter += 1
    
    # If still no entries found, create a basic structure
    if not toc_entries:
        toc_entries = [
            {'section_number': '1', 'section_title': 'Document Content', 'level': 1},
            {'section_number': '2', 'section_title': 'Main Sections', 'level': 1},
            {'section_number': '3', 'section_title': 'Conclusion', 'level': 1}
        ]
    
    return toc_entries