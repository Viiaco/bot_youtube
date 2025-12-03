"""
WARNING:

Please make sure you install the bot dependencies with `pip install --upgrade -r requirements.txt`
in order to get all the dependencies on your Python environment.

Also, if you are using PyCharm or another IDE, make sure that you use the SAME Python interpreter
as your IDE.

If you get an error like:
```
ModuleNotFoundError: No module named 'botcity'
```

This means that you are likely using a different Python interpreter than the one used to install the dependencies.
To fix this, you can either:
- Use the same interpreter as your IDE and install your bot with `pip install --upgrade -r requirements.txt`
- Use the same interpreter as the one used to install the bot (`pip install --upgrade -r requirements.txt`)

Please refer to the documentation for more information at
https://documentation.botcity.dev/tutorials/python-automations/web/
"""
from datetime import datetime

import logging

# Import for the Web Bot
from botcity.web import WebBot, Browser, By

# Import for integration with BotCity Maestro SDK
from botcity.maestro import *

from webdriver_manager.firefox import GeckoDriverManager

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

# Configuração do logging
logging.basicConfig(
    filename="log_canais_youtube.txt",  # Arquivo que será gerado para upload
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding='utf-8'
)

def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    # Recuperando o parametro "canais"
    canais = execution.parameters.get("canais")
    canais = canais.split(",")


    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = True

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.FIREFOX

    # Setando o caminho do WebDriver do Firefox via Webdriver manager
    bot.driver_path = GeckoDriverManager().install()

    #canais = ['botcity_br', 'botcity-dev', 'youtube', 'github']

    # Inicializa contadores
    total_canais = len(canais)
    canais_sucesso = 0
    canais_falha = 0

    maestro.alert(
        task_id=execution.task_id,
        title="BotYoutube - Inicio",
        message="Estamos iniciando o processo",
        alert_type=AlertType.INFO
    )

    for canal in canais:
        try:
            logging.info(f"Iniciando coleta de dados do canal: {canal}")
            # Inicia o navegador
            bot.browse(f"https://www.youtube.com/@{canal}")

            # Retorna lista de elementos
            element = bot.find_elements(selector='//span[@class="yt-core-attributed-string yt-content-metadata-view-model__metadata-text yt-core-attributed-string--white-space-pre-wrap yt-core-attributed-string--link-inherit-color" and @role="text"]', by=By.XPATH)
            # Captura o texto de cada elemento
            nome_canal = element[0].text
            numero_inscritos = element[1].text
            quantidade_videos = element[2].text
            
            logging.info(f"Canal: {nome_canal} | Inscritos: {numero_inscritos} | Vídeos: {quantidade_videos}")

            canais_sucesso += 1  # Incrementa contador de sucesso

            maestro.new_log_entry(
                activity_label="EstatisticasYoutube",
                values={
                    "canal": f"{nome_canal}",
                    "data_hora": datetime.now().strftime("%Y-%m-%d_%H-%M"),
                    "inscritos": f"{numero_inscritos}"
                }
            )

        except Exception as ex:
            logging.error(f"Erro ao coletar dados do canal {canal}: {ex}")
            canais_falha += 1  # Incrementa contador de falha

            # Salvando captura de tela do erro
            bot.save_screenshot("erro.png")
            # Dicionario de tags adicionais
            tags = {"canal": canal}

            # Registrando o erro
            maestro.error(
                task_id=execution.task_id,
                exception=ex,
                screenshot="erro.png",
                tags=tags
            )

        finally:
            # Espera 3 segundos e encerra o navegador
            bot.wait(3000)
            bot.stop_browser()

    if canais_sucesso == total_canais:
        # Define o status de finalização da tarefa
        message = f"Todos os {total_canais} canais foram processados com sucesso."
        status = AutomationTaskFinishStatus.SUCCESS

    elif canais_falha == total_canais:
        # Define o status de finalização da tarefa
        message = f"Todos os {total_canais} canais foram processados com erro."
        status = AutomationTaskFinishStatus.FAILED

    else:
        # Define o status de finalização da tarefa
        message = f'Dos {total_canais} canais pesquisados, número de falha: {canais_falha} e número de sucesso: {canais_sucesso}.'
        status = AutomationTaskFinishStatus.PARTIALLY_COMPLETED

    logging.info("Execução finalizada.")
    logging.info(f"Total canais: {total_canais} | Canais com sucesso: {canais_sucesso} | Canais com falha: {canais_falha}")

    # Enviando para a plataforma com o nome "Captura Canal..."
    maestro.post_artifact(
                task_id=execution.task_id,
                artifact_name=f"log_canais_youtube_{execution.task_id}.txt",
                filepath="log_canais_youtube.txt"
            )

    # Uncomment to mark this task as finished on BotMaestro
    maestro.finish_task(
        task_id=execution.task_id,
        status=status,
        message=message,
        total_items=total_canais, # Número total de itens processados
        processed_items=canais_sucesso, # Número de itens processados com sucesso
        failed_items=canais_falha # Número de itens processados com falha
        )


if __name__ == '__main__':
    main()
