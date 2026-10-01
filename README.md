# Radar 156

Aplicação de análise das solicitações do SP156, desenvolvida para identificar mudanças de demanda, pendências e comportamentos atípicos que possam merecer investigação pela gestão municipal.

**Aplicação publicada:** https://radar-156.streamlit.app/  
**Repositório:** https://github.com/samueldamasceno/radar-156

---

## Sobre o projeto

O SP156 recebe solicitações relacionadas a diversos serviços da Prefeitura de São Paulo. Com um grande volume de registros, nem sempre é simples identificar rapidamente quando determinado serviço ou região começa a apresentar um comportamento diferente do habitual.

O **Radar 156** transforma esses registros em sinais analíticos, permitindo acompanhar a demanda e destacar combinações de distrito e serviço que apresentem crescimento, maior pendência, maior tempo de atendimento ou comportamento estatisticamente atípico.

A solução foi pensada principalmente como ferramenta de apoio para equipes de análise e gestão municipal.

## Dados

Foram utilizados dados públicos reais do **SP156**, disponibilizados no Portal de Dados Abertos da Prefeitura de São Paulo:

- Dados do SP156, 1º trimestre de 2026
- Dados do SP156, 2º trimestre de 2026

A base é publicada pela Prefeitura de São Paulo e atualizada pela Secretaria Municipal de Inovação e Tecnologia (SMIT).

Os principais campos utilizados foram:

- data de abertura;
- data de finalização;
- tema;
- serviço;
- status;
- distrito.

Não foram utilizados dados sintéticos ou simulados.

Os arquivos brutos não fazem parte do repositório devido ao tamanho das bases. O arquivo processado utilizado pelo dashboard está versionado em `data/processed/`.

Os dados originais podem ser obtidos no Portal de Dados Abertos da Prefeitura de São Paulo. Os links para o conjunto completo e para os dois arquivos utilizados estão disponíveis na seção **Fonte** ao final deste README.

## Scripts de análise e processamento

Além da aplicação, o projeto contém alguns scripts utilizados durante a exploração, validação e preparação dos dados.

- `verificar_dados.py`: utilizado inicialmente para identificar encoding, separador, estrutura das colunas e visualizar amostras dos arquivos recebidos.
- `verificar_status.py`: utilizado para analisar os valores existentes no campo `Status` e sua relação com a presença de data de finalização.
- `auditar_distritos.py`: verifica a qualidade do campo `Distrito`, separando registros com nome de distrito, códigos numéricos e valores ausentes. Essa análise orientou quais registros poderiam ser utilizados nas análises territoriais.
- `auditar_categorias.py`: verifica possíveis variações de escrita e duplicidades em nomes de distritos e prefeituras operacionais por meio de normalização textual.
- `preparar_dados.py`: realiza o pipeline principal de preparação. Ele limpa e agrega os registros, calcula os indicadores, cria o Índice de Atenção, executa o Isolation Forest e gera `data/processed/radar156.parquet`.

Os scripts de auditoria foram mantidos no projeto para registrar parte do processo de exploração e das decisões tomadas durante o tratamento da base, além de facilitar novas verificações caso os dados de origem sejam atualizados.

## Executando localmente

Para executar somente o dashboard, não é necessário baixar os arquivos CSV originais, pois o dataset processado já está incluído no repositório.

Clone o projeto:

```bash
git clone https://github.com/samueldamasceno/radar-156.git
cd radar-156
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute a aplicação:

```bash
streamlit run streamlit_app.py
```

A aplicação utiliza diretamente:

```text
data/processed/radar156.parquet
```

### Reproduzindo o processamento

Caso queira executar também os scripts de auditoria e gerar novamente o arquivo processado, baixe os CSVs do 1º e 2º trimestres de 2026 do SP156 e coloque-os em:

```text
data/raw/
```

O pipeline procura os arquivos seguindo este padrão:

```text
sp156_2026_q*.csv
```

Portanto, após o download, utilize os seguintes nomes:

```text
sp156_2026_q1.csv
sp156_2026_q2.csv
```

Depois execute:

```bash
python scripts/preparar_dados.py
```

O arquivo processado será gerado em:

```text
data/processed/radar156.parquet
```

Os scripts de auditoria também podem ser executados individualmente, por exemplo:

```bash
python scripts/verificar_dados.py
python scripts/verificar_status.py
python scripts/auditar_distritos.py
python scripts/auditar_categorias.py
```

## Fonte

**Portal de Dados Abertos da Prefeitura de São Paulo**  
Conjunto de dados: **Dados do SP156 - Solicitações**

Bases utilizadas:

- **Dados do SP156 - 1º TRI 2026**, CSV
- **Dados do SP156 - 2º TRI 2026**, CSV

Os dados utilizados cobrem o primeiro semestre de 2026.