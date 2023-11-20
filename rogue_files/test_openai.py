def test_openai():
    import os
    import openai

    openai.api_type = "azure"
    openai.api_base = "https://oai-int-azg-we-001.openai.azure.com/"
    openai.api_version = "2023-07-01-preview"
    openai.api_key = "..."

    message_text = [
        {
            "role": "system",
            "content": "You are an AI assistant that helps people find information.",
        }
    ]

    completion = openai.ChatCompletion.create(
        engine="dep-gpt-35-turbo",
        messages=message_text,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )

    x = completion
    text = x.choices[0].text
