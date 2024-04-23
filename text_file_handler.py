import aiohttp
import pdfminer.high_level as plto
import chardet
import tempfile
import os

async def txt_content(url, attachment):
    if url[0:26] == 'https://cdn.discordapp.com':
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                content = await resp.read()
                file_extension = attachment.filename.split(".")[-1].lower()

                if file_extension in ["txt", "md", "py", "java", "cpp", "cs", "php", "js", "html", "css"]:
                    # Handle Text Files
                    with tempfile.NamedTemporaryFile(delete=False, mode="w+b") as temp_file:
                        temp_file.write(content)
                        temp_file.flush()
                        temp_file_path = temp_file.name
                    try:
                        with open(temp_file_path, "rb") as f:
                            text = f.read()
                        result = chardet.detect(text)
                        text = text.decode(result['encoding'], errors='replace')
                        return attachment.filename, text
                    finally:
                        os.unlink(temp_file_path)

                if attachment.content_type.startswith('application/pdf'):
                    # Handle PDF
                    with tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
                        temp_pdf.write(content)
                        temp_pdf_path = temp_pdf.name
                    try:
                        layout_result = plto.extract_text(temp_pdf_path)
                        if isinstance(layout_result, str):
                            text = layout_result
                        else:
                            text = ""
                            for page in layout_result:
                                text += page.get_text()
                        return attachment.filename, text
                    finally:
                        os.unlink(temp_pdf_path)
