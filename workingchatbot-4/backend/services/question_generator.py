# services/question_generator.py

from orchestrator import generate_answer

def generate_suggested_questions(doc_content, doc_id):
    """Generate 5 suggested questions based on document content"""
    
    # Create a prompt to generate relevant questions
    prompt = f"""You are an expert researcher. Based on the following document content, generate exactly 5 insightful and relevant questions that a user might ask about this document. 

The questions should be:
1. Specific to the document content
2. Varied in type (factual, analytical, comparative, etc.)
3. Practical and useful for someone studying this document
4. Clear and well-formulated
5. Each question should be on a separate line with no numbering or bullet points

Document content:
{doc_content[:3000]}...

Generate exactly 5 questions, one per line:"""

    try:
        response = generate_answer(prompt)
        
        # Parse the response to extract individual questions
        if response and not response.startswith("❌") and not response.startswith("⚠️"):
            questions = [q.strip() for q in response.split('\n') if q.strip()]
            # Take only the first 5 questions if more are generated
            questions = questions[:5]
            
            # If we have fewer than 5 questions, add some generic ones
            while len(questions) < 5:
                generic_questions = [
                    "What is the main topic of this document?",
                    "What are the key findings discussed in this document?",
                    "What methodology or approach is described?",
                    "What conclusions can be drawn from this document?",
                    "What are the implications of the findings discussed?"
                ]
                for generic_q in generic_questions:
                    if generic_q not in questions and len(questions) < 5:
                        questions.append(generic_q)
            
            return questions[:5]
        else:
            # Fallback to generic questions if LLM fails
            return [
                "What is the main topic of this document?",
                "What are the key findings or results presented?",
                "What methodology or approach is described in this document?",
                "What conclusions or recommendations are made?",
                "What are the practical implications of this document?"
            ]
            
    except Exception as e:
        print(f"Question generation error: {e}")
        # Return generic questions as fallback
        return [
            "What is the main topic of this document?",
            "What are the key findings or results presented?",
            "What methodology or approach is described in this document?", 
            "What conclusions or recommendations are made?",
            "What are the practical implications of this document?"
        ]