def consultar_descripcion_chatgpt(nombre, ean):
    prompt = f"""
Eres un experto en suplementos naturistas.

Basándote únicamente en el nombre del producto "{nombre}", explica en máximo 400 caracteres qué beneficios o propiedades naturales podría tener.

No necesitas buscar información específica de la marca ni del código EAN {ean}. Solo usa tu conocimiento general sobre suplementos naturistas.

Escribe de forma breve, clara, positiva y enfocada a beneficios de salud.
"""

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en productos naturistas y suplementos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )

        texto = respuesta.choices[0].message['content'].strip()
        return texto
    except Exception as e:
        # Mostrar exactamente el error de OpenAI
        return f"Error de API: {e}"
