import heapq
import itertools  
import tkinter as tk
from tkinter import simpledialog, messagebox

# Início do problema, definição do mapa da prisão como uma matriz 42x42
mapa = [['A' for _ in range(42)] for _ in range(42)]

# Função para ler o mapa de um arquivo de texto e retornar uma matriz com os terrenos do mapa 
def ler_mapa(arquivo):
    with open(arquivo, 'r') as f:
        linhas = f.readlines()
    
    mapa = []
    for linha in linhas:
        mapa.append(list(linha.strip()))
    
    return mapa

# Caminho para o arquivo de texto que contém o mapa
arquivo_mapa = 'mapa.txt'

# Ler e preencher a matriz do mapa
mapa = ler_mapa(arquivo_mapa)

# Cores dos terrenos no mapa 
cores = {
    'A': 'darkgray',  # Asfalto
    'T': 'brown',     # Terra
    'G': 'green',     # Grama
    'P': 'lightgray', # Paralelepípedo
    'E': 'blue'       # Edifício, intransponível
}

# Custos dos terrenosm para atravessar de um ponto a outro no mapa 
custos = {
    'A': 1,  # Asfalto
    'T': 3,  # Terra
    'G': 5,  # Grama
    'P': 10, # Paralelepípedo
    #'E': float('inf') # Edifício, intransponível
}

# Cores dos personagens no mapa  
personagens_cores = {
    'Rick': 'red',
    'Carl': 'yellow',
    'Daryl': 'orange',
    'Glen': 'purple',
    'Maggie': 'pink',
    'Saida1': 'white',  
    'Saida2': 'white'   
}

# Posições iniciais dos personagens e saídas no mapa 
posicoes = {
    'Rick': (20, 12),
    'Glen': (32, 8),
    'Daryl': (35, 35),
    'Carl': (5, 32),
    'Maggie': (13, 31),
    'Saida1': (41, 21),
    'Saida2': (41, 22)
}

# função heurística para o A* usando a distância de Manhattan para o objetivo de um ponto a outro no mapa
def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Função para o algoritmo A* que encontra o caminho mais curto entre dois pontos em um mapa
def a_star(mapa, inicio, fim):
    fila = []
    heapq.heappush(fila, (0, inicio))
    custos_acumulados = {inicio: 0}
    caminhos = {inicio: None}
    
    # Enquanto a fila não estiver vazia 
    while fila:
        _, atual = heapq.heappop(fila)

        # Se o ponto atual for o ponto de destino, então retorna o caminho
        if atual == fim:
            caminho = []
            while atual:
                caminho.append(atual)
                atual = caminhos[atual]
            return caminho[::-1]

        # Para cada vizinho do ponto atual 
        x, y = atual
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            vizinho = (x + dx, y + dy)
            if 0 <= vizinho[0] < len(mapa) and 0 <= vizinho[1] < len(mapa[0]) and mapa[vizinho[0]][vizinho[1]] != 'E':
                novo_custo = custos_acumulados[atual] + custos[mapa[vizinho[0]][vizinho[1]]]
                if vizinho not in custos_acumulados or novo_custo < custos_acumulados[vizinho]:
                    custos_acumulados[vizinho] = novo_custo
                    prioridade = novo_custo + heuristica(vizinho, fim)
                    heapq.heappush(fila, (prioridade, vizinho))
                    caminhos[vizinho] = atual

    return None  # Caso não encontre caminho


# Função para calcular as distâncias entre todos os pontos de interesse no mapa
def calcular_distancias(pontos, mapa):
    distancias = {}
    for p1, p2 in itertools.combinations(pontos, 2):
        caminho = a_star(mapa, pontos[p1], pontos[p2])
        if caminho:
            custo = sum(custos[mapa[x][y]] for x, y in caminho)
            distancias[(p1, p2)] = custo
            distancias[(p2, p1)] = custo
        else:
            distancias[(p1, p2)] = float('inf')
            distancias[(p2, p1)] = float('inf')
    return distancias

# Função para resolver o problema do caixeiro viajante (TSP) com força bruta para encontrar o menor caminho entre os pontos de interesse
def resolver_tsp(distancias, origem, pontos, saidas):
    menor_custo = float('inf')
    melhor_percorrido = None
    
    # Exclui o agente de origem das permutações
    agentes = [p for p in pontos if p != origem]
    
    # Testa todas as permutações possíveis
    for percurso in itertools.permutations(agentes):
        for saida in saidas:
            # Inicia com o agente de origem e termina em uma saída
            percurso_completo = (origem,) + percurso + (saida,)
            custo_total = 0
            
            # Soma os custos para o percurso
            for i in range(len(percurso_completo) - 1):
                custo_total += distancias[(percurso_completo[i], percurso_completo[i + 1])]
                
            # Verifica se este é o menor custo encontrado
            if custo_total < menor_custo:
                menor_custo = custo_total
                melhor_percorrido = percurso_completo
    
    # Retorna o melhor percurso e o menor custo encontrado 
    return melhor_percorrido, menor_custo

# Função para executar o caminho ótimo encontrado no mapa e exibir o custo total do caminho
def executar_caminho(mapa, percurso):
    custo_total = 0
    caminho_completo = []
    
    for i in range(len(percurso) - 1):
        caminho_parcial = a_star(mapa, posicoes[percurso[i]], posicoes[percurso[i + 1]])
        custo_parcial = sum(custos[mapa[x][y]] for x, y in caminho_parcial)
        
        # Acumula o custo total e o caminho completo
        custo_total += custo_parcial
        caminho_completo.extend(caminho_parcial)
    
    # Exibe o caminho no mapa
    desenhar_rota(caminho_completo)
    
    # Exibe o custo total no final
    custo_label.config(text=f"Custo total do caminho: {custo_total}")
    
    # Retorna o caminho completo e o custo total
    return caminho_completo, custo_total

# Definir todos os pontos de interesse e saídas no mapa (excluindo as saídas) 
pontos_interesse = {k: posicoes[k] for k in posicoes if k not in ['Saida1', 'Saida2']}

# Calcular a matriz de distâncias entre todos os pontos de interesse e saídas
distancias = calcular_distancias({**pontos_interesse, **{saida: posicoes[saida] for saida in ['Saida1', 'Saida2']}}, mapa)


# Chamada principal para definir os agentes e executar o caminho ótimo encontrado no mapa 
def definir_agentes():
    origem = simpledialog.askstring("Agente de Origem", "Informe o nome do agente de origem (Rick, Carl, Daryl, Glen, Maggie):")
    saida = simpledialog.askstring("Saída", "Informe o nome da saída (Saida1, Saida2):")
    
    if origem not in posicoes or saida not in posicoes:
        messagebox.showerror("Erro", "Agente de origem ou saída não encontrado.")
        return
    
    melhor_percorrido, _ = resolver_tsp(distancias, origem, list(pontos_interesse.keys()), [saida])
    
    if melhor_percorrido:
        caminho_completo, custo_total = executar_caminho(mapa, melhor_percorrido)
        messagebox.showinfo("Sucesso", f"Melhor percurso encontrado!\nCusto total da rota: {custo_total}")
    else:
        messagebox.showwarning("Falha", "Caminho não encontrado.")


# Tamanho da célula do mapa em pixels (largura e altura iguais) 
cell_size = 16

# Criar a janela principal do Tkinter 
root = tk.Tk()
root.title("Mapa da Prisão")

# Criar um canvas onde o mapa será desenhado 
canvas = tk.Canvas(root, width=42*cell_size, height=42*cell_size)
canvas.pack()

# Desenhar o mapa no canvas com as cores dos terrenos 
for i in range(42):
    for j in range(42):
        x0 = j * cell_size
        y0 = i * cell_size
        x1 = x0 + cell_size
        y1 = y0 + cell_size
        canvas.create_rectangle(x0, y0, x1, y1, fill=cores[mapa[i][j]], outline="black")

# Desenhar os personagens no mapa com iniciais e cores 
for personagem, (linha, coluna) in posicoes.items():
    # Coordenadas para o círculo
    x0 = coluna * cell_size + cell_size // 4
    y0 = linha * cell_size + cell_size // 4
    x1 = x0 + cell_size // 2
    y1 = y0 + cell_size // 2
    
    # Desenhar o círculo do personagem 
    #canvas.create_oval(x0, y0, x1, y1, fill=personagens_cores[personagem])
    
    # Coordenadas para o texto da inicial do personagem 
    x_text = (x0 + x1) // 2
    y_text = (y0 + y1) // 2
    
    # Desenhar a inicial do personagem 
    canvas.create_text(x_text, y_text, text=personagem[0], fill="black", font=("Arial", 12, "bold"))


# Função para desenhar a rota encontrada no mapa 
def desenhar_rota(caminho):
    for (x, y) in caminho:
        x0 = y * cell_size + cell_size // 4
        y0 = x * cell_size + cell_size // 4
        x1 = x0 + cell_size // 2
        y1 = y0 + cell_size // 2
        canvas.create_oval(x0, y0, x1, y1, outline="blue")

# Criar um botão para iniciar a definição de agentes 
btn_iniciar = tk.Button(root, text="Definir Agentes", command=definir_agentes)
btn_iniciar.pack()

# Label para exibir o custo total do caminho 
custo_label = tk.Label(root, text="")
custo_label.pack()

# Iniciar o loop principal do Tkinter 
root.mainloop()
