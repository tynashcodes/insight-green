import json
import re
from decimal import Decimal, ROUND_HALF_UP
# Assuming these models are correctly defined in .models
from .models import ESGComplianceFramework, ExtractedReportPage, ESGComplianceScore, ESGComplianceSummary
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
- Score from 0-1 where: 1 = fully meets requirement, 0.5 = partially meets, 0 = doesn't meet.
- Always provide detailed feedback explaining your score.
- Provide a recommendation for improvement.
- Also, identify and return the exact paragraph from the Report Content that is most relevant to the ESG requirement, exactly as it appears in the content (do not paraphrase).

**Reply ONLY with valid JSON:**
{{
  "score": 0.0,
  "feedback": "Your detailed explanation here",
  "recommendation": "Your recommendation here",
  "paragraph": "The relevant paragraph exactly as in the report content"
}}
"""

def parse_response(response_text):
    """Extract score, feedback, recommendation, and paragraph from API response."""
    try:
        # Remove code block markers (if any) and clean the response
        cleaned = re.sub(r'```(?:json)?|```', '', response_text.strip())
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return {
                'score': max(0.0, min(1.0, float(data.get('score', 0)))),
                'feedback': data.get('feedback', 'No feedback provided'),
                'recommendation': data.get('recommendation', 'No recommendation provided'),
                'paragraph': data.get('paragraph', '')
            }
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error: {e}. Raw response: {response_text}")
    except Exception as e:
        logging.error(f"Error during parse_response: {e}. Raw response: {response_text}")

    # Fallback regex parsing (less reliable)
    logging.warning("Attempting fallback regex parsing due to initial JSON parsing failure.")
    score_match = re.search(r'"score":\s*([0-9.]+)', response_text)
    feedback_match = re.search(r'"feedback":\s*"([^"]*)"', response_text, re.DOTALL)
    recommendation_match = re.search(r'"recommendation":\s*"([^"]*)"', response_text, re.DOTALL)
    paragraph_match = re.search(r'"paragraph":\s*"([^"]*)"', response_text, re.DOTALL)

    return {
        'score': float(score_match.group(1)) if score_match else 0.0,
        'feedback': feedback_match.group(1) if feedback_match else f"Error parsing response: {response_text[:200]}...",
        'recommendation': recommendation_match.group(1) if recommendation_match else "No recommendation provided",
        'paragraph': paragraph_match.group(1) if paragraph_match else ""
    }

def evaluate_report_against_framework(evaluation):
    """Evaluate report pages against ESG framework for a specific evaluation using Gemini Flash 2.0."""

    # Configure Gemini with your API key
    genai.configure(api_key="AIzaSyBV4BSol2U2cOrfhiZcl3gU5FJPtvmqCe8")  # Replace with your actual Gemini API key
    model = genai.GenerativeModel("gemini-2.5-flash")  # Using Gemini 1.5 Flash (recommended over 2.0-flash if 2.0 is not stable)

    scores = []
    framework_items = ESGComplianceFramework.objects.all()
    pages = ExtractedReportPage.objects.select_related('report').all()

    logging.info(f"Starting evaluation for evaluation ID: {evaluation.id}")
    logging.info(f"Found {len(framework_items)} framework items.")
    logging.info(f"Found {len(pages)} extracted report pages.")

    if not framework_items:
        logging.warning("No ESGComplianceFramework items found. Cannot perform evaluation.")
        evaluation.status = "Failed"
        evaluation.save()
        return None
    if not pages:
        logging.warning("No ExtractedReportPage items found. Cannot perform evaluation.")
        evaluation.status = "Failed"
        evaluation.save()
        return None

    for framework_item in framework_items:
        best_result = None
        logging.info(f"Processing framework item: {framework_item.id} - {framework_item.requirements}")

        # Loop over all pages; Gemini will return a JSON object with score, feedback, recommendation, and paragraph
        for page in pages:
            try:
                prompt = build_flexible_gemini_prompt(
                    requirement=framework_item.requirements,
                    page_text=page.page_text,
                    disclosure_title=getattr(framework_item, 'disclosure_title', None), # Assuming disclosure_title might be a field
                    standard_area=framework_item.standard_area,
                    sub_standard_area=framework_item.sub_standard_area
                )
                logging.debug(f"Prompt for page {page.id}, item {framework_item.id}:\n{prompt[:500]}...") # Log part of the prompt
                response = model.generate_content(prompt)
                
                # Access response.text and handle potential issues with the response object
                response_text = response.text if response and hasattr(response, 'text') else ""
                if not response_text:
                    logging.warning(f"Gemini returned empty response for item {framework_item.id} on page {page.id}.")
                    continue

                parsed = parse_response(response_text)
                logging.info(f"Parsed response for page {page.id}, item {framework_item.id}: Score={parsed['score']}, Feedback={parsed['feedback'][:100]}...")

                if best_result is None or parsed['score'] > best_result['score']:
                    best_result = {
                        'page': page,
                        'score': parsed['score'],
                        'feedback': parsed['feedback'],
                        'recommendation': parsed['recommendation'],
                        'paragraph': parsed['paragraph']
                    }
                    logging.info(f"Updated best result for item {framework_item.id} with score {best_result['score']} from page {page.id}")
            except Exception as e:
                # Log the exception for debugging purposes
                logging.error(f"Error evaluating framework item {framework_item.id} on page {page.id}: {e}", exc_info=True)
                continue

        if best_result:
            try:
                ESGComplianceScore.objects.create(
                    evaluation=evaluation,  # Link score to this evaluation
                    page=best_result['page'],
                    compliance_item=framework_item,
                    score=best_result['score'],
                    feedback=best_result['feedback'],
                    recommendation=best_result['recommendation'],
                    paragraph=best_result['paragraph'],
                )
                scores.append(best_result['score'])
                logging.info(f"Saved score for framework item {framework_item.id} with score {best_result['score']}.")
            except Exception as e:
                logging.error(f"Error saving ESGComplianceScore for item {framework_item.id}: {e}", exc_info=True)
        else:
            logging.warning(f"No best result found for framework item {framework_item.id} after checking all pages.")

    # Save summary for this evaluation
    if scores:
        total_possible = len(framework_items)  # One score per requirement
        total_score = sum(scores)
        compliance_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0

        try:
            summary = ESGComplianceSummary.objects.create(
                evaluation=evaluation,
                total_score=Decimal(str(total_score)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                total_possible=total_possible,
                compliance_percentage=Decimal(str(compliance_percentage)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
            logging.info(f"Evaluation {evaluation.id} completed. Total score: {total_score}, Compliance Percentage: {compliance_percentage:.2f}%")
            # Mark evaluation as completed
            evaluation.status = "Completed"
            evaluation.save()
            return summary  # Return the actual summary object
        except Exception as e:
            logging.error(f"Error saving ESGComplianceSummary for evaluation {evaluation.id}: {e}", exc_info=True)
            evaluation.status = "Failed"
            evaluation.save()
            return None
    else:
        logging.error(f"Evaluation completed for {evaluation.id}, but no scores were generated. "
                      "This might indicate issues with framework items, pages, or API responses.")
        evaluation.status = "Failed"
        evaluation.save()
    return None