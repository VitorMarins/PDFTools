import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import sys
import os
import json
from datetime import datetime

def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funcione em dev ou como .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Configurações Iniciais da Interface ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class PDFToolsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title("PDF Tools Pro")
        self.geometry("700x650")
        self.minsize(600, 500)
        
        # Tentar carregar ícone
        try:
            self.iconbitmap(resource_path("icone.ico"))
        except:
            pass

        # Lista na memória para guardar os caminhos dos arquivos
        self.lista_imagens = []
        self.cache_miniaturas = []
        self.arquivo_config = "pdf_tools_config.json"
        
        # Carregar configurações salvas
        self.configuracoes = self.carregar_configuracoes()

        # Configurar tema baseado nas preferências salvas
        if self.configuracoes.get("tema_escuro", False):
            ctk.set_appearance_mode("Dark")

        # --- Menu Principal ---
        self.menu_frame = ctk.CTkFrame(self, height=35, fg_color="transparent")
        self.menu_frame.pack(fill="x", pady=5, padx=10)

        # Menu Arquivo
        self.menu_arquivo = ctk.CTkOptionMenu(
            self.menu_frame,
            values=["Abrir Imagens", "Limpar Lista", "Salvar Configurações", "Sair"],
            command=self.menu_arquivo_click,
            width=120,
            font=("Roboto", 12)
        )
        self.menu_arquivo.pack(side="left", padx=5)

        # Menu Ajuda
        self.menu_ajuda = ctk.CTkOptionMenu(
            self.menu_frame,
            values=["Sobre", "Atalhos do Teclado", "Ajuda"],
            command=self.menu_ajuda_click,
            width=100,
            font=("Roboto", 12)
        )
        self.menu_ajuda.pack(side="left", padx=5)

        # Indicador de tema
        self.tema_btn = ctk.CTkButton(
            self.menu_frame,
            text="🌙 Tema Escuro" if not self.configuracoes.get("tema_escuro", False) else "☀️ Tema Claro",
            width=120,
            height=30,
            command=self.alternar_tema,
            font=("Roboto", 11)
        )
        self.tema_btn.pack(side="right", padx=5)

        # Título
        self.label_title = ctk.CTkLabel(self, text="PDF Tools Pro", font=("Roboto", 28, "bold"))
        self.label_title.pack(pady=10)

        # Subtítulo
        self.label_subtitle = ctk.CTkLabel(self, text="Converta suas imagens para PDF com facilidade", font=("Roboto", 14))
        self.label_subtitle.pack(pady=(0, 15))

        # --- Seção de Seleção de Imagens ---
        self.select_frame = ctk.CTkFrame(self)
        self.select_frame.pack(pady=5, padx=20, fill="x")

        self.label = ctk.CTkLabel(self.select_frame, text="📸 Selecionar Imagens:", font=("Roboto", 16, "bold"))
        self.label.pack(side="left", padx=10)

        # Botão para abrir o diálogo de seleção
        self.button_select = ctk.CTkButton(
            self.select_frame, 
            text="Selecionar Imagens", 
            command=self.browse_files, 
            font=("Roboto", 14, "bold"),
            width=150
        )
        self.button_select.pack(side="left", padx=10)

        # Contador de imagens
        self.label_contador = ctk.CTkLabel(
            self.select_frame, 
            text="0 imagens selecionadas",
            font=("Roboto", 12),
            text_color="gray"
        )
        self.label_contador.pack(side="right", padx=10)

        # --- Configurações do PDF ---
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.pack(pady=10, padx=20, fill="x")

        # Qualidade
        self.quality_label = ctk.CTkLabel(self.config_frame, text="Qualidade:", font=("Roboto", 13))
        self.quality_label.grid(row=0, column=0, padx=5, pady=8, sticky="w")

        self.quality_var = ctk.StringVar(value=self.configuracoes.get("qualidade", "Média"))
        self.quality_menu = ctk.CTkOptionMenu(
            self.config_frame,
            values=["Baixa", "Média", "Alta"],
            variable=self.quality_var,
            width=100
        )
        self.quality_menu.grid(row=0, column=1, padx=5, pady=8)

        # Orientação
        self.orientation_label = ctk.CTkLabel(self.config_frame, text="Orientação:", font=("Roboto", 13))
        self.orientation_label.grid(row=0, column=2, padx=5, pady=8, sticky="w")

        self.orientation_var = ctk.StringVar(value=self.configuracoes.get("orientacao", "Automática"))
        self.orientation_menu = ctk.CTkOptionMenu(
            self.config_frame,
            values=["Automática", "Retrato", "Paisagem"],
            variable=self.orientation_var,
            width=100
        )
        self.orientation_menu.grid(row=0, column=3, padx=5, pady=8)

        # Tamanho da página
        self.size_label = ctk.CTkLabel(self.config_frame, text="Tamanho:", font=("Roboto", 13))
        self.size_label.grid(row=0, column=4, padx=5, pady=8, sticky="w")

        self.size_var = ctk.StringVar(value=self.configuracoes.get("tamanho", "Original"))
        self.size_menu = ctk.CTkOptionMenu(
            self.config_frame,
            values=["Original", "A4", "Carta", "Ofício"],
            variable=self.size_var,
            width=100
        )
        self.size_menu.grid(row=0, column=5, padx=5, pady=8)

        # --- Frame de Rolagem para a Lista de Imagens ---
        self.lista_frame = ctk.CTkScrollableFrame(self, width=640, height=250)
        self.lista_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # --- Botões de Ação ---
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(pady=10)

        # Botão Converter
        self.button_convert = ctk.CTkButton(
            self.actions_frame, 
            text="📄 Converter para PDF", 
            command=self.converter_para_pdf, 
            font=("Roboto", 16, "bold"), 
            fg_color="#2e7d32", 
            hover_color="#1b5e20",
            width=200,
            height=45
        )
        self.button_convert.pack(side="left", padx=10)

        # Botão Limpar Lista
        self.button_clear = ctk.CTkButton(
            self.actions_frame, 
            text="🗑️ Limpar Lista", 
            command=self.limpar_lista, 
            font=("Roboto", 14), 
            fg_color="#c62828", 
            hover_color="#b71c1c",
            width=150,
            height=45
        )
        self.button_clear.pack(side="left", padx=10)

        # Botão Ordenar
        self.button_sort = ctk.CTkButton(
            self.actions_frame, 
            text="🔤 Ordenar", 
            command=self.ordenar_lista, 
            font=("Roboto", 14), 
            fg_color="#1565c0", 
            hover_color="#0d47a1",
            width=150,
            height=45
        )
        self.button_sort.pack(side="left", padx=10)

        # Barra de Progresso (inicialmente oculta)
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_frame.pack(pady=5, padx=20, fill="x")
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", font=("Roboto", 12))
        self.progress_label.pack()
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=500)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Ocultar inicialmente

        # --- Atalhos de Teclado ---
        self.bind('<Control-o>', lambda e: self.browse_files())
        self.bind('<Control-c>', lambda e: self.converter_para_pdf())
        self.bind('<Control-l>', lambda e: self.limpar_lista())
        self.bind('<Control-s>', lambda e: self.ordenar_lista())
        self.bind('<Control-q>', lambda e: self.sair())

        # Atualizar interface
        self.atualizar_lista_interface()

        # Salvar configurações ao fechar
        self.protocol("WM_DELETE_WINDOW", self.sair)

    def menu_arquivo_click(self, opcao):
        if opcao == "Abrir Imagens":
            self.browse_files()
        elif opcao == "Limpar Lista":
            self.limpar_lista()
        elif opcao == "Salvar Configurações":
            self.salvar_configuracoes()
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        elif opcao == "Sair":
            self.sair()

    def menu_ajuda_click(self, opcao):
        if opcao == "Sobre":
            messagebox.showinfo(
                "Sobre",
                "PDF Tools Pro v2.0\n\n"
                "Uma ferramenta simples para converter imagens em PDF.\n"
                "Desenvolvido com Python e CustomTkinter.\n\n"
                "© 2024 - Todos os direitos reservados."
            )
        elif opcao == "Atalhos do Teclado":
            messagebox.showinfo(
                "Atalhos do Teclado",
                "Ctrl + O - Abrir imagens\n"
                "Ctrl + C - Converter para PDF\n"
                "Ctrl + L - Limpar lista\n"
                "Ctrl + S - Ordenar lista\n"
                "Ctrl + Q - Sair\n"
                "Delete - Remover item selecionado"
            )
        elif opcao == "Ajuda":
            messagebox.showinfo(
                "Ajuda",
                "Como usar o PDF Tools Pro:\n\n"
                "1. Clique em 'Selecionar Imagens' para adicionar imagens\n"
                "2. Use os botões ▲/▼ para reordenar as imagens\n"
                "3. Configure qualidade, orientação e tamanho\n"
                "4. Clique em 'Converter para PDF' para gerar o arquivo\n"
                "5. Use 'Ordenar' para ordenar alfabeticamente\n"
                "6. As configurações são salvas automaticamente"
            )

    def alternar_tema(self):
        modo_atual = ctk.get_appearance_mode()
        novo_modo = "Dark" if modo_atual == "Light" else "Light"
        ctk.set_appearance_mode(novo_modo)
        
        # Atualizar texto do botão
        self.tema_btn.configure(
            text="🌙 Tema Escuro" if novo_modo == "Light" else "☀️ Tema Claro"
        )
        
        # Salvar preferência
        self.configuracoes["tema_escuro"] = (novo_modo == "Dark")
        self.salvar_configuracoes()

    def carregar_configuracoes(self):
        try:
            if os.path.exists(self.arquivo_config):
                with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def salvar_configuracoes(self):
        try:
            config = {
                "qualidade": self.quality_var.get(),
                "orientacao": self.orientation_var.get(),
                "tamanho": self.size_var.get(),
                "tema_escuro": ctk.get_appearance_mode() == "Dark"
            }
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def browse_files(self):
        tipos_arquivos = [
            ("Imagens", "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tiff *.tif"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("WebP", "*.webp"),
            ("BMP", "*.bmp"),
            ("GIF", "*.gif"),
            ("TIFF", "*.tiff *.tif"),
            ("Todos os arquivos", "*.*")
        ]
        filenames = filedialog.askopenfilenames(filetypes=tipos_arquivos)
        
        if filenames:
            # Filtrar arquivos duplicados
            for caminho in filenames:
                if caminho not in self.lista_imagens:
                    self.lista_imagens.append(caminho)
            self.atualizar_lista_interface()
            self.salvar_configuracoes()

    def atualizar_lista_interface(self):
        # Limpar widgets existentes
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
            
        self.cache_miniaturas.clear()

        # Atualizar contador
        self.label_contador.configure(text=f"{len(self.lista_imagens)} imagens selecionadas")

        if not self.lista_imagens:
            label_vazia = ctk.CTkLabel(
                self.lista_frame, 
                text="📭 Nenhuma imagem selecionada\n\nClique em 'Selecionar Imagens' para começar", 
                text_color="gray",
                font=("Roboto", 14)
            )
            label_vazia.pack(pady=40)
            return

        # Criar cabeçalho
        header_frame = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5), padx=5)
        
        ctk.CTkLabel(header_frame, text="#", width=30, font=("Roboto", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Arquivo", width=350, font=("Roboto", 12, "bold"), anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Tamanho", width=80, font=("Roboto", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Ações", width=150, font=("Roboto", 12, "bold")).pack(side="right", padx=5)

        # Separador
        ctk.CTkFrame(self.lista_frame, height=2, fg_color="gray").pack(fill="x", pady=5)

        # Lista de imagens
        for idx, caminho in enumerate(self.lista_imagens):
            row_frame = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=4, padx=5)

            # Miniatura
            ctk_img = self.carregar_miniatura(caminho)
            if ctk_img:
                self.cache_miniaturas.append(ctk_img)

            # Número
            label_num = ctk.CTkLabel(row_frame, text=f"{idx + 1}", width=30, font=("Roboto", 12))
            label_num.pack(side="left", padx=5)

            # Nome do arquivo
            nome_arquivo = os.path.basename(caminho)
            label_nome = ctk.CTkLabel(
                row_frame, 
                text=nome_arquivo[:30] + "..." if len(nome_arquivo) > 30 else nome_arquivo,
                image=ctk_img, 
                compound="left", 
                anchor="w", 
                font=("Roboto", 12)
            )
            label_nome.pack(side="left", fill="x", expand=True, padx=5)

            # Tamanho do arquivo
            tamanho = os.path.getsize(caminho)
            tamanho_str = self.formatar_tamanho(tamanho)
            label_tamanho = ctk.CTkLabel(row_frame, text=tamanho_str, width=80, font=("Roboto", 11))
            label_tamanho.pack(side="left", padx=5)

            # Botões de ação
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.pack(side="right")

            # Botão Subir
            btn_subir = ctk.CTkButton(
                actions_frame, text="▲", width=28, height=24,
                command=lambda i=idx: self.mover_item(i, -1),
                font=("Roboto", 12)
            )
            btn_subir.pack(side="left", padx=1)
            if idx == 0:
                btn_subir.configure(state="disabled")

            # Botão Descer
            btn_descer = ctk.CTkButton(
                actions_frame, text="▼", width=28, height=24,
                command=lambda i=idx: self.mover_item(i, 1),
                font=("Roboto", 12)
            )
            btn_descer.pack(side="left", padx=1)
            if idx == len(self.lista_imagens) - 1:
                btn_descer.configure(state="disabled")

            # Botão Remover
            btn_remover = ctk.CTkButton(
                actions_frame, text="✕", width=28, height=24,
                fg_color="#c62828", hover_color="#b71c1c",
                command=lambda i=idx: self.remover_item(i),
                font=("Roboto", 12)
            )
            btn_remover.pack(side="left", padx=1)

    def carregar_miniatura(self, caminho):
        try:
            img_pillow = Image.open(caminho)
            # Redimensionar mantendo proporção
            img_pillow.thumbnail((40, 40), Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=img_pillow, dark_image=img_pillow, size=(40, 40))
        except Exception as e:
            print(f"Erro ao carregar miniatura {caminho}: {e}")
            # Criar um placeholder
            img_placeholder = Image.new('RGB', (40, 40), color='gray')
            return ctk.CTkImage(light_image=img_placeholder, dark_image=img_placeholder, size=(40, 40))

    def formatar_tamanho(self, bytes):
        for unidade in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unidade}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"

    def mover_item(self, index, direcao):
        novo_index = index + direcao
        if 0 <= novo_index < len(self.lista_imagens):
            self.lista_imagens[index], self.lista_imagens[novo_index] = self.lista_imagens[novo_index], self.lista_imagens[index]
            self.atualizar_lista_interface()

    def remover_item(self, index):
        self.lista_imagens.pop(index)
        self.atualizar_lista_interface()
        self.salvar_configuracoes()

    def limpar_lista(self):
        if self.lista_imagens:
            if messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar toda a lista?"):
                self.lista_imagens.clear()
                self.atualizar_lista_interface()
                self.salvar_configuracoes()

    def ordenar_lista(self):
        if len(self.lista_imagens) > 1:
            self.lista_imagens.sort(key=lambda x: os.path.basename(x).lower())
            self.atualizar_lista_interface()
            messagebox.showinfo("Sucesso", "Lista ordenada alfabeticamente!")

    def converter_para_pdf(self):
        if not self.lista_imagens:
            messagebox.showwarning("Aviso", "Por favor, selecione pelo menos uma imagem.")
            return

        # Mostrar barra de progresso
        self.progress_bar.pack(pady=5)
        self.progress_label.configure(text="Iniciando conversão...")
        self.progress_bar.set(0)
        self.update()

        # Configurar qualidade
        qualidade_map = {
            "Baixa": 10,
            "Média": 50,
            "Alta": 95
        }
        qualidade = qualidade_map.get(self.quality_var.get(), 50)

        # Configurar tamanho da página
        tamanho_map = {
            "Original": None,
            "A4": (2480, 3508),  # 210x297mm em 300 DPI
            "Carta": (2550, 3300),  # 8.5x11in em 300 DPI
            "Ofício": (2550, 4200)  # 8.5x14in em 300 DPI
        }
        tamanho_pagina = tamanho_map.get(self.size_var.get(), None)

        nome_pdf_final = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")],
            title="Salvar PDF como..."
        )

        if not nome_pdf_final:
            self.progress_bar.pack_forget()
            return

        try:
            total_imagens = len(self.lista_imagens)
            lista_restante = []

            # Processar primeira imagem
            self.progress_label.configure(text="Processando imagens...")
            imagem_1 = Image.open(self.lista_imagens[0]).convert('RGB')
            
            # Aplicar orientação e redimensionamento
            imagem_1 = self.processar_imagem(imagem_1, tamanho_pagina)
            
            # Atualizar progresso
            self.progress_bar.set(0.1)
            self.update()

            # Processar imagens restantes
            for i, caminho in enumerate(self.lista_imagens[1:], start=1):
                self.progress_label.configure(text=f"Processando imagem {i+1}/{total_imagens}...")
                
                img = Image.open(caminho).convert('RGB')
                img = self.processar_imagem(img, tamanho_pagina)
                lista_restante.append(img)
                
                # Atualizar progresso
                progresso = 0.1 + (0.8 * (i / (total_imagens - 1)))
                self.progress_bar.set(progresso)
                self.update()

            # Salvar PDF
            self.progress_label.configure(text="Salvando PDF...")
            self.progress_bar.set(0.9)
            self.update()

            imagem_1.save(
                nome_pdf_final,
                save_all=True,
                append_images=lista_restante,
                quality=qualidade,
                dpi=(300, 300)
            )

            # Concluir
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="Concluído!")
            self.update()

            messagebox.showinfo(
                "Sucesso", 
                f"PDF gerado com sucesso!\n\n"
                f"Arquivo: {os.path.basename(nome_pdf_final)}\n"
                f"Páginas: {total_imagens}\n"
                f"Qualidade: {self.quality_var.get()}\n"
                f"Orientação: {self.orientation_var.get()}\n"
                f"Tamanho: {self.size_var.get()}"
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF:\n\n{str(e)}")
        
        finally:
            # Ocultar barra de progresso
            self.progress_bar.pack_forget()
            self.progress_label.configure(text="")

    def processar_imagem(self, imagem, tamanho_pagina=None):
        """Aplica orientação e redimensionamento à imagem"""
        
        # Orientação
        if self.orientation_var.get() == "Retrato":
            if imagem.width > imagem.height:
                imagem = imagem.rotate(90, expand=True)
        elif self.orientation_var.get() == "Paisagem":
            if imagem.height > imagem.width:
                imagem = imagem.rotate(90, expand=True)

        # Redimensionamento para o tamanho da página
        if tamanho_pagina:
            # Manter proporção
            proporcao = min(tamanho_pagina[0] / imagem.width, tamanho_pagina[1] / imagem.height)
            novo_largura = int(imagem.width * proporcao)
            novo_altura = int(imagem.height * proporcao)
            
            # Criar imagem em branco do tamanho da página
            imagem_final = Image.new('RGB', tamanho_pagina, 'white')
            # Centralizar imagem
            pos_x = (tamanho_pagina[0] - novo_largura) // 2
            pos_y = (tamanho_pagina[1] - novo_altura) // 2
            imagem_final.paste(imagem.resize((novo_largura, novo_altura), Image.Resampling.LANCZOS), (pos_x, pos_y))
            return imagem_final
        
        return imagem

    def sair(self):
        self.salvar_configuracoes()
        self.destroy()

if __name__ == "__main__":
    app = PDFToolsApp()
    app.mainloop()