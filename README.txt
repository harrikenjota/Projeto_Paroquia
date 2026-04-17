============================================================
       SANTUÁRIO SÃO JOSÉ - SISTEMA DE GESTÃO DE ESTOQUE
============================================================

1. VISÃO GERAL
--------------
Este sistema foi desenvolvido em Python/Flask para o controle 
administrativo das doações da Paróquia. Ele gerencia desde 
a entrada de donativos até a entrega para as famílias, 
oferecendo transparência através de dashboards estatísticos 
e busca dinâmica de registros.

2. PRINCIPAIS FUNCIONALIDADES
-----------------------------
[X] CONTROLE DE ESTOQUE: Entradas e saídas com trava de segurança.
[X] BUSCA DINÂMICA: Filtros em tempo real nas tabelas (DataTables).
[X] GESTÃO DE PESSOAS: Separação entre DOADORES e ASSISTIDOS.
[X] FEEDBACK VISUAL: Mensagens Flash para confirmação de ações.
[X] DASHBOARD: Gráficos de fluxo e níveis críticos de itens.
[X] RELATÓRIOS: Exportação de movimentações e contatos em CSV.

3. ESTRUTURA DO PROJETO (ORGANIZAÇÃO POR SEÇÕES)
------------------------------------------------
O código foi estruturado em blocos numerados para facilitar 
a leitura e futuras manutenções (Clean Code):

- SEÇÃO 1: Configurações e Banco de Dados (app.py / models.py)
- SEÇÃO 2: Identidade Visual e CSS (base.html)
- SEÇÃO 3: Painel Operacional e Inventário (index.html)
- SEÇÃO 4: Inteligência de Dados e Gráficos (dashboard.html)
- SEÇÃO 5: Cadastro e Categorização Social (beneficiarios.html)
- SEÇÃO 6: Scripts de Busca e Tradução (DataTables Integration)

4. REQUISITOS E INSTALAÇÃO
--------------------------
Para rodar o projeto, você precisará do Python instalado.

Passo 1: Instalar dependências
> pip install flask flask_sqlalchemy

Passo 2: Executar o servidor
> python app.py

Passo 3: Acessar no navegador
> URL: http://127.0.0.1:5000

5. REGRAS DE NEGÓCIO IMPORTANTES
--------------------------------
- VALIDAÇÃO DE ESTOQUE: O sistema NÃO permite saída de itens sem 
  estoque, exibindo um alerta crítico ao usuário.
- SEGURANÇA DE DADOS: O banco de dados (SQLite) é gerado 
  automaticamente, garantindo portabilidade.
- ESTATÍSTICA SOCIAL: A Dashboard conta APENAS famílias assistidas 
  como "atendidas", separando os doadores para não distorcer a 
  análise de impacto social.
- INTERFACE: Tabelas com busca automática em português para 
  agilizar o atendimento no balcão de doações.

------------------------------------------------------------
   "Ide a José" - Gestão Administrativa Santuário São José
------------------------------------------------------------