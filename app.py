import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import sys
import os

def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funcione em dev ou como .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Configurações Iniciais da Interface ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PDFToolsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title("PDF Tools")
        self.geometry("600x550")
        self.resizable(False, False)
        self.iconbitmap(resource_path("icone.ico"))

        # Lista na memória para guardar os caminhos dos arquivos (na ordem definida pelo usuário)
        self.lista_imagens = []
        # Cache para as miniaturas não sumirem da tela
        self.cache_miniaturas = []

        # Titulo
        self.label_title = ctk.CTkLabel(self, text="PDF Tools", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=15)

        # Seção de Conversão de Imagens para PDF
        self.label = ctk.CTkLabel(self, text="Converter Imagens para PDF:", font=("Roboto", 16, "bold"))
        self.label.pack(pady=5)

        # Botão para abrir o diálogo de seleção de arquivos
        self.button_select = ctk.CTkButton(self, text="Selecionar Imagens", command=self.browse_files, font=("Roboto", 14, "bold"))
        self.button_select.pack(pady=10)

        # --- Frame de Rolagem para a Lista de Imagens ---
        self.lista_frame = ctk.CTkScrollableFrame(self, width=540, height=220)
        self.lista_frame.pack(pady=10)

        # Botão para realizar a conversão das imagens para PDF
        self.button_convert = ctk.CTkButton(self, text="Converter para PDF", command=self.converter_para_pdf, font=("Roboto", 16, "bold"), fg_color="green", hover_color="darkgreen")
        self.button_convert.pack(pady=15)
        
    def browse_files(self):
        tipos_arquivos = [("Imagens", "*.png *.jpg *.jpeg *.webp *.bmp")]
        filenames = filedialog.askopenfilenames(filetypes=tipos_arquivos)
        
        if filenames:
            self.lista_imagens.extend(list(filenames))
            self.atualizar_lista_interface()

    def atualizar_lista_interface(self):
        
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
            
        self.cache_miniaturas.clear()

        if not self.lista_imagens:
            label_vazia = ctk.CTkLabel(self.lista_frame, text="Nenhuma imagem selecionada", text_color="gray")
            label_vazia.pack(pady=20)
            return

        # lista
        for idx, caminho in enumerate(self.lista_imagens):
            row_frame = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=4, padx=5)

            # Carrega a miniatura (Thumbnail)
            try:
                img_pillow = Image.open(caminho)
                ctk_img = ctk.CTkImage(light_image=img_pillow, dark_image=img_pillow, size=(40, 40))
                self.cache_miniaturas.append(ctk_img)
            except Exception as e:
                ctk_img = None
                print(f"Erro ao carregar miniatura: {e}")

            # Nome do arquivo + Miniatura
            nome_arquivo = os.path.basename(caminho)
            label_nome = ctk.CTkLabel(
                row_frame, 
                text=f" {idx + 1}. {nome_arquivo}", 
                image=ctk_img, 
                compound="left", 
                anchor="w", 
                font=("Roboto", 12)
            )
            label_nome.pack(side="left", fill="x", expand=True, padx=5)

            # Botão Subir
            btn_subir = ctk.CTkButton(row_frame, text="▲", width=28, height=24, 
                                      command=lambda i=idx: self.mover_item(i, -1))
            btn_subir.pack(side="right", padx=2)
            if idx == 0:
                btn_subir.configure(state="disabled")

            # Botão Descer
            btn_descer = ctk.CTkButton(row_frame, text="▼", width=28, height=24, 
                                       command=lambda i=idx: self.mover_item(i, 1))
            btn_descer.pack(side="right", padx=2)
            if idx == len(self.lista_imagens) - 1:
                btn_descer.configure(state="disabled")

            # Botão Remover
            btn_remover = ctk.CTkButton(row_frame, text="X", width=28, height=24, fg_color="red", hover_color="darkred",
                                        command=lambda i=idx: self.remover_item(i))
            btn_remover.pack(side="right", padx=(10, 2))

    def mover_item(self, index, direcao):
        novo_index = index + direcao
        if 0 <= novo_index < len(self.lista_imagens):
            self.lista_imagens[index], self.lista_imagens[novo_index] = self.lista_imagens[novo_index], self.lista_imagens[index]
            self.atualizar_lista_interface()

    def remover_item(self, index):
        self.lista_imagens.pop(index)
        self.atualizar_lista_interface()

    def converter_para_pdf(self):
        if not self.lista_imagens:
            messagebox.showwarning("Aviso", "Por favor, selecione pelo menos uma imagem.")
            return

        nome_pdf_final = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")],
            title="Salvar PDF como..."
        )

        if not nome_pdf_final:
            return

        try:
            imagem_1 = Image.open(self.lista_imagens[0]).convert('RGB')
            
            lista_restante = []
            for caminho in self.lista_imagens[1:]:
                img = Image.open(caminho).convert('RGB')
                lista_restante.append(img)

            imagem_1.save(nome_pdf_final, save_all=True, append_images=lista_restante)
            messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\nSalvo em: {os.path.basename(nome_pdf_final)}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF:\n{str(e)}")

if __name__ == "__main__":
    app = PDFToolsApp()
    app.mainloop()