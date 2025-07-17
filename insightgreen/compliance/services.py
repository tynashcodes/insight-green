import json
import re
from decimal import Decimal, ROUND_HALF_UP
from .models import ESGComplianceFramework, ExtractedReportPage, ESGComplianceScore, ESGComplianceSummary

def build_flexible_gemini_prompt(requirement, page_text, disclosure_title, standard_area, sub_standard_area):
    return f"""
You are an ESG compliance analyst. Evaluate how well this report content addresses the ESG requirement.

**ESG Requirement:**
- Requirement: {requirement}
- Standard Area: {standard_area or "N/A"}
- Sub-Standard Area: {sub_standard_area or "N/A"}

**Report Content:**
{page_text}

**Instructions:**
Score from 0-1 where: 1=fully meets requirement, 0.5=partially meets, 0=doesn't meet
Always provide detailed feedback explaining your score.

**Reply ONLY with valid JSON:**
{{
  "score": 0.0,
  "feedback": "Your detailed explanation here",
  "recommendation": "..."
}}
"""

def parse_response(response_text):
    """Extract score and feedback from API response"""
    try:
        # Clean and extract JSON
        cleaned = re.sub(r'```(?:json)?|```', '', response_text.strip())
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        
        if json_match:
            data = json.loads(json_match.group(0))
            return {
                'score': max(0.0, min(1.0, float(data.get('score', 0)))),
                'feedback': data.get('feedback', 'No feedback provided'),
                'recommendation': data.get('recommendation', 'No recommendation provided')
            }
    except:
        pass
    
    # Fallback regex parsing
    score_match = re.search(r'"score":\s*([0-9.]+)', response_text)
    feedback_match = re.search(r'"feedback":\s*"([^"]*)"', response_text, re.DOTALL)
    recommendation_match = re.search(r'"recommendation":\s*"([^"]*)"', response_text, re.DOTALL)
    
    return {
        'score': float(score_match.group(1)) if score_match else 0.0,
        'feedback': feedback_match.group(1) if feedback_match else f"Error parsing response: {response_text[:100]}...",
        'recommendation': recommendation_match.group(1) if recommendation_match else "No recommendation provided"
    }
    
from openai import OpenAI
def evaluate_report_against_framework(evaluation):
    """Evaluate report pages against ESG framework for a specific evaluation"""

    client = OpenAI(api_key="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")
    model = "gpt-4o-mini"

    scores = []
    framework_items = ESGComplianceFramework.objects.all()
    pages = ExtractedReportPage.objects.select_related('report').all()

    for framework_item in framework_items:
        best_result = None

        for page in pages:
            try:
                prompt = build_flexible_gemini_prompt(
                    requirement=framework_item.requirements,
                    page_text=page.page_text,
                    disclosure_title=getattr(framework_item, 'disclosure_title', None),
                    standard_area=framework_item.standard_area,
                    sub_standard_area=framework_item.sub_standard_area
                )

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert ESG compliance analyst. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=6000
                )

                parsed = parse_response(response.choices[0].message.content if response.choices else "")

                if best_result is None or parsed['score'] > best_result['score']:
                    best_result = {
                        'page': page,
                        'score': parsed['score'],
                        'feedback': parsed['feedback'],
                        'paragraph': best_result['page'].page_text.strip().split('\n\n')[0][:120], # Simple heuristic
                        'recommendation': parsed['recommendation']
                    }

            except Exception as e:
                continue

        if best_result:
            ESGComplianceScore.objects.create(
                evaluation=evaluation,  # Link score to this evaluation
                page=best_result['page'],
                compliance_item=framework_item,
                score=best_result['score'],
                feedback=best_result['feedback'],
                paragraph=best_result['paragraph'],
                recommendation=best_result['recommendation'],
            )
            scores.append(best_result['score'])

    # Save summary for this evaluation
    if scores:
        total_possible = len(framework_items) # One score per requirement
        total_score = sum(scores)
        compliance_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0

        summary = ESGComplianceSummary.objects.create(
            evaluation=evaluation,
            total_score=Decimal(str(total_score)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            total_possible=total_possible,
            compliance_percentage=Decimal(str(compliance_percentage)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        )
        
        # Mark evaluation as completed
        evaluation.status = "Completed"
        evaluation.save()
    
        return summary  # Return the actual summary object
    
    return None  # Not a boolean
