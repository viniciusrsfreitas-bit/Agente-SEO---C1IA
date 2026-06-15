import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from googleapiclient.discovery import build

# =====================================================================
# TRAVAS DE SEGURANÇA E TELEMETRIA
# =====================================================================
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

# =====================================================================
# 1. CONFIGURAÇÕES E CHAVES DE API
# =====================================================================
# Lendo a variável customizada para ignorar o bug do cabeçalho do GitHub
api_key_env = os.environ.get("C1IA_OPENAI_KEY")

definitive_llm = LLM(
    model="gpt-4o-mini",
    api_key=api_key_env
)

GOOGLE_API_KEY = "AIzaSyArriA38ty4TpTZBXpR6k7uhj8ZKLIjpzI"
GOOGLE_CSE_ID = "e0c02c422fb02448d"
# =====================================================================
# 2. FERRAMENTAS (TOOLS)
# =====================================================================
@tool("Google Search")
def google_search_tool(search_query: str) -> str:
    """Útil para pesquisar na internet sobre assuntos atuais, notícias e tendências de mercado."""
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        result = service.cse().list(q=search_query, cx=GOOGLE_CSE_ID).execute()

        search_results = []
        if 'items' in result:
            for item in result['items'][:5]:
                search_results.append(f"Título: {item['title']}\nLink: {item['link']}\nResumo: {item['snippet']}\n---")
            return "\n".join(search_results)
        else:
            return "Nenhum resultado encontrado para essa busca."
    except Exception as e:
        return f"Erro ao realizar busca no Google: {str(e)}"

@tool("Enviar Email")
def send_email_tool(conteudo_email: str) -> str:
    """Útil para enviar o texto final gerado e revisado diretamente para o e-mail do utilizador."""
    try:
        remetente = "comercial01.c1ia@gmail.com"
        senha = os.environ.get("GMAIL_APP_PASSWORD")
        destinatario = "viniciusrsfreitas@gmail.com"

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = "📝 Novo Conteúdo Gerado pela C1IA - Pronto para Publicação"

        msg.attach(MIMEText(conteudo_email, 'plain', 'utf-8'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        text = msg.as_string()
        server.sendmail(remetente, destinatario, text)
        server.quit()

        return "E-mail enviado com sucesso com o conteúdo final!"
    except Exception as e:
        return f"Erro ao enviar o e-mail: {str(e)}"

# =====================================================================
# 3. DEFINIÇÃO DOS AGENTES (COM LLM INJETADO EXPLICITAMENTE)
# =====================================================================
trend_analyzer = Agent(
    role="Analista de Tendências e Mercado",
    goal="Pesquisar na internet e identificar os assuntos mais quentes, dores reais e tendências atuais sobre Inteligência Artificial no mundo dos negócios e finanças corporativas.",
    backstory="""Você é um pesquisador focado em inovação tecnológica e mercado financeiro.
Seu objetivo é descobrir o que os empresários e diretores financeiros estão buscando
e debatendo neste momento nas redes e portais de notícias.
Você define tópicos estratégicos alinhados com o Método FOCO da C1IA, garantindo
que o tema escolhido seja focado em uma Dor Real e traga Vantagem Competitiva.
Para que você saiba sobre a C1IA, aqui está a missão e a visão da empresa:
Missão: Implantar Inteligência Artificial para resolver as dores reais que travam o crescimento das empresas. Nossa missão é devolver o tempo ao empresário para que ele foque no core do seu negócio.
Visão: Ser a referência em transformar tecnologias complexas em ferramentas simples de produtividade. Queremos que cada cliente nosso utilize a IA não como uma tendência, mas como uma vantagem competitiva real e indispensável para a escala do negócio.""",
    tools=[google_search_tool],
    allow_delegation=False,
    llm=definitive_llm,
    verbose=True
)

planner = Agent(
    role="Planejador de Conteúdo",
    goal="Planejar conteúdo envolvente e factually preciso sobre {topic}",
    backstory="Você está trabalhando no planejamento de uma publicação para a página da C1IA no Linkedin "
              "sobre o tema: {topic}."
              "Você coleta informações que ajudam o público a aprender algo e tomar decisões informadas. "
              "Seu trabalho é a base para que o Redator de Conteúdo escreva um artigo sobre esse tema."
              "Para que você saiba sobre a C1IA vou postar aqui a missão, visão e valores da empresa:"
              "Missão: Implantar Inteligência Artificial para resolver as dores reais que travam o crescimento das empresas. Nossa missão é devolver o tempo ao empresário para que ele foque no core do seu negócio."
              "Visão: Ser a referência em transformar tecnologias complexas em ferramentas simples de produtividade. Queremos que cada cliente nosso utilize a IA não como uma tendência, mas como uma vantagem competitiva real e indispensável para a escala do negócio."
              "Valores: Foco na Dor Real — resolvemos gargalos práticos, não vendemos tendências. Libertação Operacional — IA para tirar a equipe do braçal e focar no estratégico. Vantagem Competitiva — tecnologia que vira lucro e escala para o cliente. Segurança Absoluta — inovação com rigor total à LGPD e proteção de dados.",
    allow_delegation=False,
    llm=definitive_llm,
    verbose=True
)

writer = Agent(
    role="Redator de Conteúdo",
    goal="Escrever um artigo opinativo perspicaz e factually preciso sobre o tema: {topic}",
    backstory="Você está trabalhando na redação de uma nova publicação para a página do Linkedin da C1IA sobre o tema: {topic}. "
              "Você baseia sua escrita no trabalho do Planejador de Conteúdo, que fornece um esboço e contexto relevante sobre o tema. "
              "Você segue os principais objetivos e a direção do esboço, conforme fornecido pelo Planejador de Conteúdo. "
              "Você também fornece percepções objetivas e imparciais e as fundamenta com informações fornecidas pelo Planejador de Conteúdo. "
              "Você reconhece no seu artigo opinativo quando suas declarações são opiniões em oposição a declarações objetivas.",
    allow_delegation=False,
    llm=definitive_llm,
    verbose=True
)

editor = Agent(
    role="Editor",
    goal="Editar um post de blog para alinhar com o estilo de escrita da organization.",
    backstory="Você é um editor que recebe um post para a página da C1IA no Linkedin do Redator de Conteúdo. "
              "Seu objetivo é revisar o post do Linkedin para garantir que ele siga as melhores práticas jornalísticas, "
              "ofereça pontos de vista equilibrados ao apresentar opiniões ou afirmações, "
              "e também evite tópicos ou opiniões altamente controversos sempre que possível.",
    allow_delegation=False,
    llm=definitive_llm,
    verbose=True
)

email_notifier = Agent(
    role="Analista de Automação e Disparo",
    goal="Pegar no texto final revisado pelo Editor e enviar por e-mail para o utilizador, garantindo que o conteúdo chegue intacto.",
    backstory="Você é um assistant focado em integração de sistemas e automação de fluxos. Sua única e crucial missão é garantir que o trabalho da equipe de conteúdo chegue de forma rápida e segura à caixa de entrada do utilizador.",
    tools=[send_email_tool],
    allow_delegation=False,
    llm=definitive_llm,
    verbose=True
)

# =====================================================================
# 4. DEFINIÇÃO DAS TAREFAS (TASKS)
# =====================================================================
discover_trend_task = Task(
    description=(
        "1. Utilize a ferramenta de busca para pesquisar notícias recentes, artigos e discussões sobre "
        "'Inteligência Artificial aplicada a finanças corporativas', 'automação de processos financeiros' ou 'IA para CFOs'.\n"
        "2. Identifique um gargalo prático ou uma tendência em alta que os empresários estão enfrentando hoje.\n"
        "3. Defina e formule um Tópico claro e direto (ex: 'Como agentes de IA estão eliminando o trabalho braçal na auditoria de notas fiscais' ou 'O impacto da análise preditiva de IA no fluxo de caixa mensal')."
    ),
    expected_output="Apenas o título do tópico escolhido e um breve parágrafo justificando por que este assunto está em alta no mercado hoje.",
    agent=trend_analyzer,
)

plan = Task(
    description=(
        "1. Priorizar as tendências mais recentes, principais atores e notícias relevantes sobre {topic}.\n"
        "2. Identificar o público-alvo, considerando seus interesses e pontos de dor.\n"
        "3. Desenvolver um esboço de conteúdo detalhado incluindo uma introdução, pontos principais e uma chamada para ação.\n"
        "4. Incluir palavras-chave de SEO e dados ou fontes relevantes."
    ),
    expected_output="Um documento de plano de conteúdo abrangente com esboço, análise do público, palavras-chave de SEO e recursos.",
    agent=planner,
)

write = Task(
    description=(
        "1. Usar o plano de conteúdo para create um post de blog envolvendo sobre {topic}.\n"
        "2. Incorporar palavras-chave de SEO de forma natural.\n"
        "3. As seções/subtítulos devem estar nomeadas adequadamente de forma atraente.\n"
        "4. Garantir que o post esteja estruturado com uma introdução envolvendo, corpo com boas ideias e uma conclusão resumida.\n"
        "5. Revisar para corrigir erros gramaticais e alinhar com a voz da marca.\n"
    ),
    expected_output="Um post de blog bem escrito em formato markdown, pronto para publicação, cada seção deve conter 2 ou 3 parágrafos.",
    agent=writer,
)

edit = Task(
    description=("Revisar o post da página do Linkedin fornecido para corrigir erros gramaticais, "
                 "alinhar com a voz da marca, traduzir para o português brasileiro e garantir que a formatação markdown esteja correta e pronta para publicação."),
    expected_output="Um post da página do Linkedin bem escrito em formato markdown, pronto para publicação, cada seção deve conter 2 ou 3 parágrafos, com a formatação markdown correta.",
    agent=editor
)

send_email_task = Task(
    description=(
        "Pegue no texto final revisado e formatado que o Editor (editor) gerou no passo anterior. "
        "Utilize a ferramenta 'Enviar Email' para disparar esse conteúdo completo para o e-mail do utilizador."
    ),
    expected_output="Confirmação de que o e-mail foi enviado com sucesso.",
    agent=email_notifier,
)

# =====================================================================
# 5. EXECUÇÃO SÍNCRONA
# =====================================================================
if __name__ == "__main__":
    print("🔍 Passo 1: Analisando tendências no Google...")
    trend_crew = Crew(
        agents=[trend_analyzer],
        tasks=[discover_trend_task],
        verbose=True
    )
    
    topic_result = trend_crew.kickoff()
    dynamic_topic = str(topic_result.raw).strip()
    
    print("\n" + "="*80)
    print(f"📌 TÓPICO SELECIONADO NA NUVEM: {dynamic_topic}")
    print("="*80 + "\n")
    
    print("🚀 Passo 2: Alimentando a esteira de conteúdo e disparo...")
    production_crew = Crew(
        agents=[planner, writer, editor, email_notifier],
        tasks=[plan, write, edit, send_email_task],
        verbose=True
    )
    
    final_result = production_crew.kickoff(inputs={"topic": dynamic_topic})
    print("\n✨ Automação executada com sucesso pelo GitHub Actions!")
