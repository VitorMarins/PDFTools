# 🛠️ PDFTools

> Uma ferramenta de desktop simples e intuitiva para converter e ordenar imagens em um único arquivo PDF.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![UI](https://img.shields.io/badge/UI-CustomTkinter-orange)

---

## ✨ Funcionalidades

- 🖼️ **Conversão Simples:** Transforma múltiplos formatos de imagem em PDF.
- 🔄 **Ordenação Personalizada:** Escolha e organize a ordem exata das imagens antes de gerar o PDF.
- 🎨 **Interface Moderna:** Visual limpo e amigável desenvolvido em CustomTkinter.

---

## 📋 Requisitos

Antes de começar, você precisará ter o Python 3.8 ou superior instalado em sua máquina. As principais bibliotecas utilizadas são:

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Interface gráfica)
- [Pillow](https://python-pillow.org/) (Processamento de imagem)
- [PyInstaller](https://pyinstaller.org/) (Para empacotar o executável)

---

## 🚀 Instalação e Execução (Desenvolvimento)

Siga os passos abaixo para rodar o projeto localmente:

1. **Clone o repositório:**
```bash
   git clone <repository-url>
   cd PDFTools

```

2. **Instale as dependências:**

```bash
   pip install -r requirements.txt

```

3. **Execute a aplicação:**

```bash
   python app.py

```

---

## 📦 Como Gerar o Executável (.exe ou Binário)

Se você deseja compilar o projeto para gerar um arquivo executável independente, utilize o comando correspondente ao seu sistema operacional:

### No Windows:

```bash
pyinstaller --noconsole --onefile --icon=icone.ico --add-data "icone.ico;." app.py

```

### No Linux:

```bash
pyinstaller --noconsole --onefile --icon=icone.ico --add-data "icone.ico:." app.py

```

Após a conclusão do processo:

1. Abra a pasta `dist` que foi criada na raiz do projeto.
2. O arquivo executável pronto para uso estará lá dentro.

---

## ⚖️ Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](/LICENSE) para mais detalhes.
