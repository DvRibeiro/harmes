# 👁️⚡ HERMES — AI Desktop Companion & Local Services Orchestrator

> **HERMES** (inspirado no deus mensageiro *Hermes*) é um assistente de desktop temático com estética sombria e transparente, projetado para atuar como o **orquestrador central de Inteligências Artificiais e serviços locais** na sua máquina.

---

## 🌌 Visão do Projeto

Diferente de simples chatbots web ou janelas convencionais, o **HERMES** vive na sua área de trabalho:
- **Presença Flutuante & Imersiva**: Uma criatura animada translúcida que habita seu desktop, pronta para receber comandos sem abrir navegadores ou janelas pesadas.
- **Orquestrador Multi-IA**: Uma arquitetura modular projetada para canalizar solicitações para múltiplas IAs na nuvem (Google Gemini) e IAs/serviços locais (Ollama, LM Studio, ComfyUI, automações de sistema e homelab).
- **Leve & Independente**: Construído sobre **PyQt6** com cliente REST puro (sem SDKs pesados), consumindo o mínimo de memória e CPU.

---

## 📂 Estrutura do Repositório

O projeto adota uma arquitetura modular desacoplada:

```text
hermes/
├── assets/                     # Sprites e recursos visuais do companion
│   ├── frame_0.png .. frame_7.png
│   └── spritesheet_transparent.png
│
├── src/                        # Código-fonte da aplicação
│   ├── app.py                  # Ponto de entrada e ciclo de vida do PyQt6
│   ├── config.py               # Gerenciador de configurações (config.json)
│   │
│   ├── core/                   # Núcleo de orquestração
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Roteador central de solicitações, delegação e agentes
│   │   ├── task_logger.py      # Gerenciador e auditor de relatórios de missões (.md)
│   │   └── tools.py            # Ferramentas locais de diagnóstico de rede e homelab
│   │
│   ├── providers/              # Provedores de IA plugáveis
│   │   ├── __init__.py
│   │   ├── base.py             # Interface abstrata BaseProvider
│   │   ├── antigravity_provider.py # Conector com o Google AntiGravity via Python SDK
│   │   ├── gemini.py           # Cliente REST de alta performance para o Gemini
│   │   └── local_fallback.py   # Respostas locais, utilitários e matemática segura
│   │
│   └── ui/                     # Componentes visuais do PyQt6
│       ├── __init__.py
│       ├── companion.py        # Widget principal transparente e máquina de estados
│       ├── balloon.py          # Balão de fala dark/neon roxo com suporte a relatórios e links
│       ├── settings_dialog.py  # Modal para ajuste de chaves e provedores
│       └── icons.py            # Gerador dinâmico de ícones vetoriais via QPainter
│
├── tests/                      # Bateria de testes unitários
│   ├── __init__.py
│   ├── test_gemini_client.py   # Testes do cliente Gemini (paginação, erros e segurança)
│   └── test_orchestrator.py    # Testes do orquestrador, delegação e gerador de relatórios
│
├── tools/                      # Ferramentas auxiliares e offline
│   └── sprite_tools/           # Scripts de extração e tratamento alfa dos sprites
│       ├── analyze_sprites.py
│       ├── extract_frames.py
│       ├── inspect_img.py
│       ├── process_sprites.py
│       └── slice_alpha.py
│
├── reports/                    # Relatórios e auditorias das missões do AntiGravity (ignorado no git)
├── config.example.json         # Modelo de configuração seguro (sem credenciais)
├── config.json                 # Configurações locais ativas (ignorado no git)
├── iniciar.bat                 # Inicializador rápido para Windows
├── iniciar_sem_janela.vbs      # Inicializador silencioso em segundo plano
├── main.py                     # Script de inicialização da raiz
├── requirements.txt            # Dependências do projeto
└── README.md                   # Documentação do projeto
```

---

## ✨ Recursos Atuais

1. **Janela 100% Transparente & Flutuante**:
   - Apenas a criatura, os botões e a barra de interação flutuam sobre qualquer aplicativo ou jogo.
   - Arraste livremente para qualquer canto de qualquer monitor com o mouse.
2. **Máquina de Estados & Animações**:
   - **Idle**: Respiração sutil calculada senoidalmente enquanto a criatura foca no usuário.
   - **Envio**: Ao enviar um pedido, a criatura vira de costas e corre em perspectiva até desaparecer nas sombras da tela.
   - **Retorno**: Assim que a resposta do provedor de IA fica pronta, a criatura surge correndo do fundo e para em primeiro plano.
3. **Balão de Fala Neon & Ações Rápidas**:
   - Renderização rica de texto e HTML acima da cabeça da criatura.
   - Botão para **copiar** a resposta com 1 clique.
4. **Bandeja do Sistema (*System Tray*)**:
   - Permite minimizar o assistente para a bandeja ao lado do relógio do Windows, restaurando ou abrindo configurações pelo menu de contexto.
5. **Orquestrador Central Multi-Agente**:
   - Suporte nativo ao **Google Gemini** com descoberta dinâmica de modelos (`auto`), priorizando versões Flash estáveis e tratando atualizações/remoções de modelos (HTTP 404).
   - Modo **Local Fallback**: se nenhuma chave for inserida ou em falhas de rede, responde a utilitários locais, relógio, data e cálculos matemáticos com parser AST seguro.
6. **Integração com Google AntiGravity via Python SDK**:
   - O HERMES atua como maestro: ao receber pedidos técnicos (ex: *"Hermes, peça para o AntiGravity verificar o servidor de minecraft"*), delega autonomamente a tarefa para o agente **AntiGravity** com contexto e workspace direcionados.
   - Diagnósticos preliminares de rede e infraestrutura do Homelab (`tools.py`) via socket TCP e latência.
7. **Sistema de Auditoria & Relatórios Completos (`Task Reports`)**:
   - Para não sobrecarregar o balão com códigos e saídas extensas de terminal, o HERMES apresenta uma síntese executiva de 2 frases e salva a íntegra da análise em `reports/tasks/*.md`.
   - Botão de relatório e links clicáveis diretamente no balão abrem o arquivo `.md` no editor do sistema (ex: VS Code) em 1 clique.

---

## 🚀 Como Executar

### 1. Pré-requisitos

- Python 3.10 ou superior instalado.
- Ambiente virtual recomendado (o diretório pai já possui um ambiente pronto em `../venv`).

Instale as dependências:
```bash
python -m pip install -r requirements.txt
```

### 2. Inicialização

Você pode iniciar o HERMES de três maneiras:

- **Via Script em Lote (com console)**:
  Dê dois cliques em [`iniciar.bat`](file:///E:/SERVIDOR/GERENCIAMENTO/HERMES/hermes/iniciar.bat) ou execute no terminal:
  ```cmd
  iniciar.bat
  ```

- **Silencioso (Sem janela preta de comando)**:
  Dê dois cliques em [`iniciar_sem_janela.vbs`](file:///E:/SERVIDOR/GERENCIAMENTO/HERMES/hermes/iniciar_sem_janela.vbs).

- **Via Python diretamente**:
  ```bash
  python main.py
  ```

---

## ⚙️ Configuração da IA

1. Clique no ícone de engrenagem (**⚙**) no canto superior direito do assistente.
2. Insira sua **API Key do Google Gemini** (obtida no Google AI Studio).
3. Mantenha o modelo como `auto` (recomendado) ou especifique um modelo de sua preferência.
4. Clique em **Salvar Configurações**.

> 💡 **Nota de Segurança**: As chaves ficam salvas localmente no arquivo [`config.json`](file:///E:/SERVIDOR/GERENCIAMENTO/HERMES/hermes/config.json), que está incluído no `.gitignore` e **nunca** deve ser versionado publicamente. Você também pode definir a variável de ambiente `GEMINI_API_KEY`.

---

## 🧩 Adicionando Novos Provedores e Serviços

Para plugar um novo serviço local (como **Ollama**, **ComfyUI** ou automação do Windows):

1. Crie o provedor herdando de `BaseProvider` em `src/providers/meu_servico.py`:
   ```python
   from .base import BaseProvider

   class MeuServicoProvider(BaseProvider):
       def generate(self, prompt: str, **kwargs) -> str:
           # Comunicação com a API local (ex: localhost:11434)
           return "Resposta do serviço local"
   ```
2. Registre o provedor em [`src/core/orchestrator.py`](file:///E:/SERVIDOR/GERENCIAMENTO/HERMES/hermes/src/core/orchestrator.py).
3. Atualize [`config.example.json`](file:///E:/SERVIDOR/GERENCIAMENTO/HERMES/hermes/config.example.json) com as configurações do serviço.

---

## 🧪 Testes Unitários

Para rodar os testes automatizados da suíte:

```bash
python -m unittest discover tests
```

Os testes executam simulações completas da API em memória, sem consumir cotas nem necessitar de credenciais reais.

---

## 🗺️ Roadmap de Evolução

- [x] Arquitetura modular e desacoplada em `src/`.
- [x] Cliente REST resiliente com fallback e seleção dinâmica de modelos.
- [x] Balão flutuante estilizado e controle por System Tray.
- [ ] Provedor para LLMs locais via **Ollama** / **LM Studio**.
- [ ] Integração com **ComfyUI** / **Stable Diffusion** para geração local de imagens.
- [ ] Atalho global de teclado (*Global Hotkey*) para invocar a barra de comandos a qualquer momento.
- [ ] Integração com serviços de automação local e monitoramento de homelab.
