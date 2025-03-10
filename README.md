# Smart Watering

Plataforma IoT para monitoramento e controle remoto de um sistema de irrigação sustentável desenvolvido com o ESP32.

![Badge](https://img.shields.io/static/v1?label=license&message=MIT&color=1E90FF)
![Badge](https://img.shields.io/static/v1?label=build&message=passing&color=00d110)

## Conteúdo

- [Sobre](#sobre)
  - [Funcionalidades](#funcionalidades)
- [Suporte](#suporte)
- [Materiais e Tecnologias](#materiais-e-tecnologias)
  - [Conectando os Componentes](#conectando-os-componentes)
  - [Diagrama Esquemático do Protótipo](#diagrama-esquemático-do-protótipo)
  - [Fluxograma do _Firmware_](#fluxograma-do-firmware)
- [Executando a Aplicação](#executando-a-aplicação)
  - [ESP32](#esp32)
  - [Plataforma IoT](#plataforma-iot)
- [Autor](#autor)
- [Licença](#licença)

## Sobre

O Smart Watering é um sistema de irrigação automatizado, sustentável e de baixo custo, composto por uma plataforma IoT (_SaaS_) com funcionalidades inovadoras, disponível para _smartphones_, _tablets_ e computadores. Este sistema também inclui uma API REST para realizar a comunicação entre a plataforma IoT e o Raspberry Pi Pico W.

Este projeto foi tema do meu Trabalho de Conclusão de Curso (TCC), com o título _“Smart Watering: Um Sistema de Monitoramento Remoto e Controle de Irrigação Sustentável Baseado em Plataforma IoT”_. Além disso, fui bolsista no projeto por um ano, que também foi aprovado e fomentado pelo [Programa Centelha](https://programacentelha.com.br/ce/) - Ceará (2022).

Veja este vídeo de exemplo no YouTube em [```https://www.youtube.com/watch?v=AMdGk-LIUu8```](https://www.youtube.com/watch?v=AMdGk-LIUu8).

![smart-watering](https://github.com/lucapwn/smart-watering-pico-w/blob/main/images/Login%20Page.png)

![smart-watering](https://github.com/lucapwn/smart-watering-pico-w/blob/main/images/Dashboard%20Page.png)

### Funcionalidades

O Smart Watering permite, ao agricultor, diversos recursos e funcionalidades, como:

- Painel de controle **interativo** com gráficos e _widgets_ para visualização, em **tempo real**, dos dados meteorológicos e de irrigação, como **umidade de ar** e **solo**, **temperatura** e **luminosidade** do ambiente, **ponto de orvalho**, **nível de água** do reservatório, **nível de chuva** e **consumo de água** referente aos meses do ano. Essa funcionalidade permite, aos usuários, monitorar a plantação e tomar decisões com base nas condições meteorológicas apresentadas.
- Os usuários podem **agendar a irrigação remotamente** (sem a necessidade de se deslocar até o local da plantação) de **várias formas**, por exemplo: **por dia**, **horário**, **umidade do solo** ou **fluxo de água**. Esta flexibilidade permite, ao agricultor, definir valores dinâmicos e específicos em cada uma das regas, tornando a plataforma adequada para a gestão de diversos tipos de plantas. A rega automática pode ser definida para períodos únicos ou diários.
- Em termos de gestão, os usuários podem **visualizar**, **adicionar**, **editar** e **remover** as regas agendadas. Além disso, podem pesquisar por atributos específicos, aplicar filtros e ordenar informações em colunas de tabelas, personalizar as unidades de temperatura, as medidas do reservatório de água, as notificações do sistema, os temas de cores e o menu da plataforma.
- Gerar relatórios **inteligentes** dos dados coletados dos sensores, presentes na plantação, para uma **análise** posterior e **aprimoramento** de recursos hídricos. Os usuários podem selecionar os dados e períodos de tempo pretendidos e arquivá-los para referência futura.
- Acesso a **página de administração** integrada, a qual facilita a gestão de dados dos usuários, sensores, permissões, autenticações e configurações, garantindo uma plataforma organizada e acessível aos administradores.
- Além disso, o Smart Watering permite acesso a uma **API REST** para usuários obter recursos da plataforma e do sistema de irrigação. Esta interface permite a coleta de dados, em **tempo real**, o envio de comandos para o sistema de irrigação e a configuração da plataforma. A API REST é protegida por autenticação, a qual concede acesso apenas aos usuários autorizados. Através deste recurso, os usuários podem obter acesso instantâneo a informações críticas, incluindo dados de sensores, agendas de irrigação, notificações, consumo de água e configurações da plataforma.

## Suporte

A plataforma é compatível e responsiva em _smartphones_, _tablets_ e computadores, a qual permite sua adaptação em diferentes tamanhos de telas e sistemas operacionais.

## Materiais e Tecnologias

Para montar e desenvolver o sistema de irrigação, são necessários os seguintes materiais e tecnologias:

Material                   | Tipo             | Tecnologia             | Descrição
-------------------------- | ---------------- | ---------------------- | --------------------------------------------------
FC-28                      | Sensor           | Wi-Fi (802.11)         | Protocolo de comunicação sem fio. 
YL-83                      | Sensor           | REST                   | Arquitetura de comunicação.
DHT11                      | Sensor           | JSON                   | Formato de dados da API.
MQ-135                     | Sensor           | PostgreSQL             | Banco de dados relacional.
BMP280                     | Sensor           | C/C++                  | Linguagem de programação do _firmware_.
GY-8511                    | Sensor           | Django                 | _Framework_ de desenvolvimento _web_ em Python.
TEMT6000                   | Sensor           | HTML, CSS e JavaScript | Linguagens de marcação, formatação e programação.
HCSR-04                    | Sensor           | Bootstrap 5            | _Framework front-end_.
YF-S201                    | Sensor           | jQuery                 | Biblioteca de manipulação do DOM em JavaScript.
Relé                       | Atuador          | ApexCharts             | Biblioteca de gráficos.
RTC DS3231                 | Módulo           | DataTables             | Biblioteca de tabelas.
ESP32-WROOM-32U DevKitC V4 | Microcontrolador | Ion.RangeSlider        | Biblioteca de _inputs_.

### Conectando os Componentes

Os GPIOs dos sensores e atuadores devem ser ligados ao ESP32 da seguinte forma:

ESP32 | DHT11 | HCSR-04 | YL-83 | Relay | YF-S201 | DS3231 | TEMT6000 | FC-28 | GY-8511  | MQ-135
----- | ----- | ------- | ----- | ----- | ------- | ------ | -------- | ----- | -------- | ------
4     | A0    |         |       |       |         |        |          |       |          | 
12    |       | ECHO    |       |       |         |        |          |       |          |
13    |       | TRIG    |       |       |         |        |          |       |          |
14    |       |         | A0    |       |         |        |          |       |          |
18    |       |         |       | IN    |         |        |          |       |          |
19    |       |         |       |       | D0      |        |          |       |          |
21    |       |         |       |       |         | SDA    |          |       |          |
22    |       |         |       |       |         | SCL    |          |       |          |
25    |       |         |       |       |         |        | A0       |       |          |
27    |       |         |       |       |         |        |          | A0    |          |
32    |       |         |       |       |         |        |          |       | A0       |
33    |       |         |       |       |         |        |          |       | EN e 3V3 |
34    |       |         |       |       |         |        |          |       |          | A0
3V3   |       |         |       |       |         |        |          |       | 3V3      |
GND   | GND   | GND     | GND   | GND   | GND     | GND    | GND      | GND   | GND      | GND
5V    | VCC   | VCC     | VCC   | VCC   | VCC     | VCC    | VCC      | VCC   |          | VCC

### Diagrama Esquemático do Protótipo

Após conectar todos os componentes, o sistema deve ser semelhante à imagem ilustrada abaixo.

<img src="https://github.com/lucapwn/smart-watering/assets/58787069/3ede2807-cf93-4cfe-ad45-bde694d29e4a" width="540">

### Fluxograma do _Firmware_

O fluxograma abaixo ilustra as interações do _firmware_ do ESP32 com a plataforma IoT e outros recursos do sistema.

<img src="https://github.com/lucapwn/smart-watering-pico-w/blob/main/images/Firmware%20Flowchart.svg" width="1000">

## Executando a Aplicação

### ESP32

Com o Arduino IDE instalado e configurado para executar aplicações do ESP32, instale as bibliotecas necessárias incluídas em [```esp32/libraries```](https://github.com/lucapwn/smart-watering/tree/main/esp32/libraries) na pasta principal do projeto.

Logo após, configure o ESP32 com suas preferências no arquivo [```smart_watering.h```](https://github.com/lucapwn/smart-watering/blob/main/esp32/main/smart_watering.h) em [```esp32/main```](https://github.com/lucapwn/smart-watering/tree/main/esp32/main).

Por fim, faça o _upload_ do código do arquivo [```main.ino```](https://github.com/lucapwn/smart-watering/blob/main/esp32/main/main.ino) em [```esp32/main```](https://github.com/lucapwn/smart-watering/tree/main/esp32/main) para o ESP32.

### Plataforma IoT

Com o Git instalado, clone o repositório do projeto:

~~~console
foo@bar:~$ git clone https://github.com/lucapwn/smart-watering.git
~~~

Com o Python instalado, navegue até a pasta principal do projeto e instale as dependências da aplicação:

~~~console
foo@bar:~$ pip install -r requirements.txt
~~~

Aplique as alterações no banco de dados da aplicação:

~~~console
foo@bar:~$ python manage.py migrate
~~~

Crie um usuário com permissões de administrador:

~~~console
foo@bar:~$ python manage.py createsuperuser
~~~

Por fim, execute o servidor da aplicação:

~~~console
foo@bar:~$ python manage.py runserver 0.0.0.0:80
~~~

Agora, você poderá acessar a aplicação no seu computador através de [http://localhost](http://localhost).

Para usá-la em outro dispositivo, obtenha o endereço IP do computador que está executando a aplicação.

Se tudo estiver configurado corretamente, os dados dos sensores serão exibidos, em tempo real, na plataforma.

Obrigado por chegar até aqui!

## Autor

Desenvolvido por [Lucas Araújo](https://github.com/lucapwn).

## Licença

Esse software é licenciado pelo [MIT](https://choosealicense.com/licenses/mit/).
