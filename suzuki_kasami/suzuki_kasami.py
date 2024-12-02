import threading
import time
import random

class SuzukiKasamiMutex:
    def __init__(self, site_id, total_sites):
        self.site_id = site_id  # ID do site atual
        self.total_sites = total_sites  # Número total de sites
        self.token = None  # O token é um dicionário com o contador e a fila de acesso
        self.request_count = [0] * total_sites  # Contador de solicitações para cada site
        self.state = "Released"  # Estados possíveis: Released, Want, Held
        self.lock = threading.Lock()  # Lock para evitar concorrência
        self.request_queue = []  # Fila local de solicitações pendentes
    
    # Função para inicializar o token (somente no site inicial)
    def initialize_token(self):
        self.token = {"queue": [], "last_request": [0] * self.total_sites}
    
    # Função para enviar REQUEST para todos os outros sites
    def send_request(self, sites):
        with self.lock:
            self.state = "Want"
            self.request_count[self.site_id] += 1  # Incrementa o contador de solicitação
            print(f"Site {self.site_id} enviando REQUEST.")
            for site in sites:
                if site.site_id != self.site_id:
                    delay = random.uniform(0.5, 2)  # Simula atraso na comunicação
                    threading.Thread(target=site.receive_request, args=(self.site_id, self.request_count[self.site_id], delay)).start()
    
    # Função chamada quando o site recebe uma solicitação REQUEST
    def receive_request(self, sender_id, sender_request_count, delay=0):
        time.sleep(delay)  # Simula atraso na comunicação
        with self.lock:
            self.request_count[sender_id] = max(self.request_count[sender_id], sender_request_count)
            print(f"Site {self.site_id} recebeu REQUEST de Site {sender_id} com contador {sender_request_count}.")
            if self.token and self.state != "Held":  # Se tem o token e não está na CS, envia-o
                self.send_token(sender_id)
    
    # Função para enviar o token
    def send_token(self, receiver_id):
        with self.lock:
            print(f"Site {self.site_id} enviando TOKEN para Site {receiver_id}.")
            receiver = sites[receiver_id]
            threading.Thread(target=receiver.receive_token, args=(self.token,)).start()
            self.token = None  # Libera o token localmente
    
    # Função chamada quando o site recebe o token
    def receive_token(self, token):
        with self.lock:
            print(f"Site {self.site_id} recebeu o TOKEN.")
            self.token = token
            self.enter_critical_section()
    
    # Função para entrar na seção crítica
    def enter_critical_section(self):
        with self.lock:
            if self.token and self.state == "Want":
                self.state = "Held"
                print(f"Site {self.site_id} entrou na seção crítica.")
                time.sleep(random.uniform(1, 3))  # Simula tempo de execução na CS
                self.exit_critical_section()
    
    # Função para sair da seção crítica e liberar o token
    def exit_critical_section(self):
        with self.lock:
            print(f"Site {self.site_id} saindo da seção crítica.")
            self.state = "Released"
            self.token["last_request"][self.site_id] = self.request_count[self.site_id]
            # Transfere o token para o próximo site na fila, se houver
            if self.token["queue"]:
                next_site = self.token["queue"].pop(0)
                self.send_token(next_site)
    
    # Função principal que executa o algoritmo
    def execute(self, sites):
        if not self.token:  # Se não tem o token, envia REQUEST
            self.send_request(sites)
        else:  # Se já tem o token, entra na seção crítica
            self.enter_critical_section()

# Função para simular execução de um site
def simulate_site(site, sites):
    time.sleep(random.uniform(1, 3))  # Espera inicial aleatória
    site.execute(sites)

# Criando sites
total_sites = 3
sites = [SuzukiKasamiMutex(site_id=i, total_sites=total_sites) for i in range(total_sites)]

# Inicializando o token no site 0
sites[0].initialize_token()

# Simulando a execução dos sites em threads
threads = []
for site in sites:
    thread = threading.Thread(target=simulate_site, args=(site, sites))
    threads.append(thread)
    thread.start()

# Aguarda que todas as threads terminem
for thread in threads:
    thread.join()
