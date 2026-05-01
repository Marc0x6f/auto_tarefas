import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import pandas as pd
from leitor_csv import (
    ler_csv_sed,
    converter_nota_para_escala_10,
    remover_duplicatas_maior_nota,
    salvar_csv_limpo
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unicodedata
import time
import os
import subprocess
import psutil

def remover_acentos(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

def iniciar_chrome_com_perfil():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    return webdriver.Chrome(options=options)

def encontrar_chrome():
    candidatos = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
    ]
    for caminho in candidatos:
        if os.path.exists(caminho):
            return caminho
    return None

def abrir_chrome_debug():
    caminho_chrome = encontrar_chrome()
    if not caminho_chrome:
        messagebox.showerror(
            "Chrome não encontrado",
            "Não foi possível encontrar o Google Chrome instalado neste computador.\n\n"
            "Instale o Chrome e tente novamente."
        )
        return False

    user_data_dir = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")

    comando = [
        caminho_chrome,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}"
    ]

    try:
        subprocess.Popen(comando)
        return True
    except Exception as e:
        print(f"Erro ao abrir o Chrome: {e}")
        return False

def iniciar_lancamento(driver, df, log_callback):
    # Seleciona aba correta
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if "Lançamento das Avaliações" in driver.title:
            log_callback(f"✅ Aba correta selecionada: {driver.title}")
            break
    else:
        log_callback("❌ Aba 'Lançamento das Avaliações' não encontrada.")
        messagebox.showinfo("Aviso", "Acesse a aba manualmente e clique em OK para continuar.")

    # Loop de preenchimento
    for index, row in df.iterrows():
        try:
            nome_original = row["Nome do Aluno"]
            nome = remover_acentos(nome_original)
            nota = str(round(row["Nota (%)"], 1)).replace(".", ",")

            campo_busca = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input.dt-input"))
            )
            campo_busca.clear()
            campo_busca.send_keys(nome)
            time.sleep(0.3)

            log_callback(f"🔍 Buscando: {nome} → Nota: {nota}")

            campo_nota = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.NAME, "n.NotaAtribuida"))
            )
            campo_nota.clear()
            campo_nota.send_keys(nota)
            log_callback("✅ Nota preenchida.")
        except Exception:
            log_callback(f"⚠️ Aluno '{nome_original}' não encontrado ou nota não lançada.")
        time.sleep(0.5)

    # Final: limpa campo de busca, ativa foco e seleciona 100 resultados por página
    try:
        campo_busca = driver.find_element(By.CSS_SELECTOR, "input.dt-input")
        campo_busca.clear()
        campo_busca.click()  # força foco para garantir que a tabela recarregue
        log_callback("🧹 Campo de busca limpo e ativado.")

        seletor = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.NAME, "tableDiarioClasse_length"))
        )
        for option in seletor.find_elements(By.TAG_NAME, 'option'):
            if option.text.strip() == '100':
                option.click()
                log_callback("📄 Visualização ajustada para 100 alunos por página.")
                break
    except Exception:
        log_callback("⚠️ Não foi possível ajustar visualização final.")

# === INTERFACE TKINTER ===
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Lançador de Notas")

        self.caminho_csv = ""

        self.btn_chrome = tk.Button(root, text="📎 Abrir Chrome (modo conectado)", command=self.abrir_chrome)
        self.btn_chrome.pack(pady=5)

        self.btn_csv = tk.Button(root, text="📂 Selecionar CSV (Planilha de Notas)", command=self.selecionar_csv)
        self.btn_csv.pack(pady=5)

        self.btn_iniciar = tk.Button(root, text="▶️ Iniciar Lançamento", command=self.iniciar, state=tk.DISABLED)
        self.btn_iniciar.pack(pady=5)

        self.btn_ajuda = tk.Button(root, text="ℹ️ Ajuda", command=self.mostrar_ajuda)
        self.btn_ajuda.pack(pady=(5, 0))

        self.txt_log = tk.Text(root, height=20, width=60)
        self.txt_log.pack(padx=10, pady=10)

    def log(self, mensagem):
        self.txt_log.insert(tk.END, mensagem + "\n")
        self.txt_log.see(tk.END)
        self.root.update()


    def abrir_chrome(self):
        def chrome_ja_esta_aberto():
            for proc in psutil.process_iter(["name"]):
                if proc.info["name"] and "chrome" in proc.info["name"].lower():
                    return True
            return False

        if chrome_ja_esta_aberto():
            messagebox.showwarning("Chrome Aberto", "Feche todas as janelas do Chrome antes de usar esse botão.")
            return

        if abrir_chrome_debug():
            self.log("🌐 Chrome aberto em modo conectado. Aguarde ele carregar antes de continuar.")
        else:
            messagebox.showerror("Erro", "Não foi possível abrir o Chrome automaticamente.")

    def selecionar_csv(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if caminho:
            self.caminho_csv = caminho
            self.log(f"📄 CSV selecionado: {caminho}")
            self.btn_iniciar.config(state=tk.NORMAL)

    def mostrar_ajuda(self):
        ajuda_janela = tk.Toplevel(self.root)
        ajuda_janela.title("Ajuda - Como usar o Lançador de Notas")
        ajuda_janela.geometry("520x420")

        # Centraliza a janela de ajuda na tela
        ajuda_janela.update_idletasks()
        largura = ajuda_janela.winfo_width()
        altura = ajuda_janela.winfo_height()
        x = (ajuda_janela.winfo_screenwidth() // 2) - (largura // 2)
        y = (ajuda_janela.winfo_screenheight() // 2) - (altura // 2)
        ajuda_janela.geometry(f"+{x}+{y}")

        # Faz com que a janela de ajuda fique acima da principal e bloqueie interação
        ajuda_janela.transient(self.root)
        ajuda_janela.grab_set()

        texto = (
            "🧾 PASSO A PASSO\n\n"
            "1️ Acesse a SED e vá em:\n"
            "   Centro de Mídias → Tarefas → Relatório de Atividades do CMSP\n\n"
            "2️ Clique em 'Gerar Excel' e selecione:\n"
            "   'Arquivo CSV sem formatação'\n\n"
            "3️ Renomeie o arquivo com o nome da turma:\n"
            "   Exemplo: 1A, 2B, 3C...\n\n"
            "4️ No aplicativo Lançador de Notas:\n"
            "   - Abra o Chrome (modo conectado)\n"
            "   - Acesse a Sala do Futuro e vá até a página de lançamento das notas\n"
            "   - Selecione o CSV (Planilha com as notas)\n"
            "   - Clique em 'Iniciar Lançamento'"
        )

        frame_texto = tk.Frame(ajuda_janela)
        frame_texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame_texto)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(frame_texto, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Segoe UI", 11))
        text_widget.insert(tk.END, texto)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        btn_fechar = tk.Button(ajuda_janela, text="Fechar", command=ajuda_janela.destroy)
        btn_fechar.pack(pady=5)

        ajuda_janela.focus_set()  # garante que a janela pegue o foco

    def iniciar(self):
        threading.Thread(target=self.executar_processo).start()

    def executar_processo(self):
        try:
            self.log("🌐 Conectando ao navegador Chrome...")
            driver = iniciar_chrome_com_perfil()
        except Exception as e:
            messagebox.showerror(
                "Chrome não encontrado",
                "Não foi possível conectar ao Chrome.\n\n"
                "Use o botão 'Abrir Chrome (modo conectado)' antes de iniciar o lançamento."
            )
            self.log(f"❌ Erro ao conectar ao Chrome: {e}")
            return

        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.dt-input"))
            )
        except Exception:
            messagebox.showwarning(
                "Página incorreta",
                "Não encontramos o campo de busca.\n\n"
                "Acesse a aba de lançamento de notas no Sala de Aula do Futuro e tente novamente."
            )
            self.log("❌ Campo de busca não encontrado. Verifique a página aberta no Chrome.")
            return

        try:
            self.log("🚀 Iniciando limpeza do CSV...")
            df = ler_csv_sed(self.caminho_csv)
            df = converter_nota_para_escala_10(df)
            df = remover_duplicatas_maior_nota(df)

            os.makedirs("_dados_temp", exist_ok=True)
            caminho_saida = os.path.join("_dados_temp", "dados_limpos.csv")
            salvar_csv_limpo(df, caminho_saida)
            self.log("✅ CSV limpo gerado.")

            df_limpo = pd.read_csv(caminho_saida, sep=";")
            self.log("🧠 Iniciando automação...")
            iniciar_lancamento(driver, df_limpo, self.log)
            self.log("✅ Fim do processo.")

        except Exception as e:
            self.log(f"❌ Erro geral: {e}")
            messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()