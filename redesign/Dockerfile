# Usa uma imagem oficial do Python
FROM python:3.13.2-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta usada pelo Panel
EXPOSE 5006

# Comando para rodar a aplicação
CMD ["panel", "serve", "SCANPLOT_V2.0.0a1.py", "--address", "0.0.0.0", "--port", "5006", "--allow-websocket-origin=*"]

