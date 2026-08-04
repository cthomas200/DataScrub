from dotenv import load_dotenv
import os
import json
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def ai_suggestions(df, issues):
    data_sum = {
        'columns': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'shape': df.shape, 
        'sample': df.head(5).to_dict(orient='records')
    }

    prompt = f"""
    You are a data quality expert. Analyze the following dataset issues and suggest specfic fixes.

    DATASET INFO:
    {json.dumps(data_sum, indent=2, default=str)}

    ISSUES DETECTED:
    {json.dumps(issues, indent=2, default=str)}

    Return ONLY a JSON array with no markdown, no explanation, no code fences. Each object must follow this exact schema:
    [
        {{
            "issue_type": "the type field from the issue",
            "column": "column name",
            "recommended_action": "specific action to take",
            "reasoning": "plain English explanation a non-technical person could understand",
            "risk": "low or medium or high"
        }}
    ]"""

    response = client.messages.create(
    model='claude-sonnet-4-6',
    max_tokens=2048,
    messages=[
        {'role': 'user', 'content': prompt}
    ]

    )

    raw = response.content[0].text.strip()
    if raw.startswith('```'):
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]

    try:
        return json.loads(raw), ''
    except json.JSONDecodeError as e:
        return [], f'Failed to parse AI response: {e}\n\nRaw response: {raw}'
