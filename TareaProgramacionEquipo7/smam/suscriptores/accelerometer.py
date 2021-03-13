import pika
import sys
sys.path.append('../')
from monitor import Monitor
import time
import logging


class Acelerometro:

    def consume(self):
        try:
            # Se establece la conexión con el Distribuidor de Mensajes
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            # Se solicita un canal por el cuál se enviará la posición
            channel = connection.channel()
            # Se declara una cola para leer los mensajes enviados por el
            # Publicador
            channel.queue_declare(queue='accelerometer', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(on_message_callback=self.callback, queue='accelerometer')
            channel.start_consuming()  # Se realiza la suscripción en el Distribuidor de Mensajes
        except (KeyboardInterrupt, SystemExit):
            channel.close() 
            sys.exit("Conexión cerrada")
            time.sleep(1)
            sys.exit("Programa cerrado")

    def callback(self, ch, method, properties, body):
        json_message = self.string_to_json(body)
        if float(json_message['x_position']) <= 0.4 and float(json_message['y_position']) >= 0.6 and float(json_message['z_position']) <= 0.4:
            monitor = Monitor()
            valoresXYZ = json_message['x_position'], json_message['y_position'], json_message['z_position']
            monitor.print_notification(json_message['datetime'], json_message['id'], valoresXYZ,
                                       'aceleración', json_message['model'])
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
    p_acelerometro = Acelerometro()
    p_acelerometro.consume()
