import pika
import sys
sys.path.append('../')
from monitor import Monitor
import time


class alarmaMedicamento:
    horas={}
    horas['paracetamol'] = 1
    horas['ibuprofeno'] = 2
    horas['insulina'] = 3
    horas['furosemida'] = 4
    horas['piroxicam'] = 5
    horas['tolbutamida']=6
    def consume(self):
        try:
            # Se establece la conexión con el Distribuidor de Mensajes
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            # Se solicita un canal por el cuál se enviarán los signos vitales
            channel = connection.channel()
            # Se declara una cola para leer los mensajes enviados por el
            # Publicador
            channel.queue_declare(queue='medicamento', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(on_message_callback=self.callback, queue='medicamento')
            channel.start_consuming()  # Se realiza la suscripción en el Distribuidor de Mensajes
        except (KeyboardInterrupt, SystemExit):
            channel.close()  # Se cierra la conexión
            sys.exit("Conexión finalizada...")
            time.sleep(1)
            sys.exit("Programa terminado...")

    def callback(self, ch, method, properties, body):
        json_message = self.string_to_json(body)
        if str(json_message['hora']) == str(self.horas[json_message['simular_medicamento']]):
            monitor = Monitor()
            monitor.print_alarma_medicamento(json_message['datetime'], json_message['id'], json_message[
                                       'simular_medicamento'], 'Medicamento', json_message['model'])
        time.sleep(1)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def string_to_json(self, string):
        message = {}
        string = string.decode('utf-8')
        string = string.replace('{', '')
        string = string.replace('}', '')
        values = string.split(', ')
        for x in values:
            v = x.split(': ')
            message[v[0].replace('\'', '')] = v[1].replace('\'', '')
        return message

if __name__ == '__main__':
    p_alarma_medicamento = alarmaMedicamento()
    p_alarma_medicamento.consume()
