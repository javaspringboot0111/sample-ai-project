from openai import OpenAI

client = OpenAI()

def review_code(code):

    prompt=f"""

Review this code.

Find:

- Bugs

- Security issues

- Performance issues

- Suggest improvements

{code}

"""

    response=client.chat.completions.create(

        model="gpt-4.1",

        messages=[

            {"role":"user","content":prompt}

        ]

    )

    return response.choices[0].message.content
