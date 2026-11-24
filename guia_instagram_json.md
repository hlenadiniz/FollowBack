How Follow - Guia para Baixar Seguidores e Seguindo do Instagram (JSON)

Para verificar quem não te segue de volta com segurança (sem precisar informar sua senha), baixe seus dados oficiais diretamente pelo Instagram seguindo os passos abaixo.

1. Passo a Passo no Aplicativo ou Navegador

Passo 1: Acesse a Central de Contas

Abra o Instagram e vá até o seu Perfil.

Toque no menu (☰ no canto superior direito).

Entre em Central de Contas.

Passo 2: Vá para Suas informações e permissões

Role a tela até a seção de configurações da conta.

Selecione Suas informações e permissões > Baixar suas informações.

Passo 3: Solicite a exportação

Toque em Baixar ou transferir informações.

Se tiver mais de uma conta vinculada, marque apenas a do Instagram e avance.

Escolha a opção Algumas das suas informações.

Passo 4: Selecione Seguidores e seguindo

Role até a seção Conexões.

Marque apenas a caixa Seguidores e seguindo e toque em Avançar.

Passo 5: Configure o formato para JSON (Etapa Crítica)

Selecione Baixar no dispositivo.

Configure as opções exatamente assim:

Intervalo de datas: Desde o início (para garantir a lista completa)

Formato: Altere de HTML para JSON (o formato HTML não funciona)

Qualidade da mídia: Baixa (deixa o arquivo bem leve e rápido)

Passo 6: Crie e baixe o arquivo ZIP

Toque em Criar arquivos.

O Instagram levará alguns minutos para preparar o pacote e avisará por e-mail ou notificação quando o arquivo .zip estiver pronto para download.

2. Estrutura dos Arquivos no ZIP (Referência Técnica)

Ao descompactar o arquivo .zip baixado, os arquivos estarão no seguinte caminho de diretórios:

connections/followers_and_following/
├── following.json      # Contas que você segue
└── followers_1.json    # Contas que seguem você


Nota: Contas com muitos seguidores terão arquivos paginados como followers_2.json, followers_3.json, etc.

3. Estrutura do JSON Gerado pela Meta

Exemplo de objeto dentro de following.json:

{
  "relationships_following": [
    {
      "title": "",
      "media_list_data": [],
      "string_list_data": [
        {
          "href": "https://www.instagram.com/usuario_exemplo",
          "value": "usuario_exemplo",
          "timestamp": 1700000000
        }
      ]
    }
  ]
}


Observação para o parser: Enquanto o arquivo following.json encapsula os dados na chave "relationships_following", os arquivos followers_*.json costumam trazer o array de objetos diretamente na raiz do JSON.