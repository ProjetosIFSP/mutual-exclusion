from collections import deque

class DistributedSystem:
    def __init__(self, n_processes):
        self.n_processes = n_processes
        self.token = deque()  # Fila de pedidos
        self.has_token = [False] * n_processes  # Indica quem possui o token
        self.sequence = [0] * n_processes  # Números de sequência para cada processo

    def request_critical_section(self, process_id):
        self.sequence[process_id] += 1
        print(f"Processo {process_id} solicitando CS com sequência {self.sequence[process_id]}")
        if not any(self.has_token):  # Se ninguém tem o token
            self.token.append(process_id)

    def execute_critical_section(self, process_id):
        if self.has_token[process_id]:
            print(f"Processo {process_id} executando CS.")
            self.release_token(process_id)
        else:
            print(f"Processo {process_id} não possui o token.")

    def release_token(self, process_id):
        print(f"Processo {process_id} liberando o token.")
        self.has_token[process_id] = False
        if self.token:
            next_process = self.token.popleft()
            self.has_token[next_process] = True
            print(f"Token passado para o processo {next_process}.")

# Exemplo de uso
system = DistributedSystem(3)
system.request_critical_section(0)
system.request_critical_section(1)
system.execute_critical_section(0)  # Processo 0 executa a CS
system.execute_critical_section(1)  # Processo 1 só executará ao receber o token
