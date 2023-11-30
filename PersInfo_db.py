# Создайте программу для управления клиентами на Python.
# Требуется хранить персональную информацию о клиентах:
# имя,
# фамилия,
# email,
# телефон.
# Сложность в том, что телефон у клиента может быть не один, а два, три и даже больше. А может и вообще не быть телефона, например, он не захотел его оставлять.
#
# Вам необходимо разработать структуру БД для хранения информации и несколько функций на Python для управления данными.
#
# Функция, создающая структуру БД (таблицы).
# Функция, позволяющая добавить нового клиента.
# Функция, позволяющая добавить телефон для существующего клиента.
# Функция, позволяющая изменить данные о клиенте.
# Функция, позволяющая удалить телефон для существующего клиента.
# Функция, позволяющая удалить существующего клиента.
# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
# Функции выше являются обязательными, но это не значит, что должны быть только они. При необходимости можете создавать дополнительные функции и классы.
#
# Также предоставьте код, демонстрирующий работу всех написанных функций.
#
# Результатом работы будет .py файл.

import psycopg2
class DataBase:
    def drop_db(self, conn):
        '''Снос БД'''
        with conn.cursor() as cur:
            cur.execute('''
                DROP TABLE IF EXISTS clientphone;
                DROP TABLE IF EXISTS phone;
                DROP TABLE IF EXISTS client;
                ''')
        conn.commit()
    def create_db(self, conn):
        '''Создание структуру БД'''
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS client(
                    client_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(20),
                    last_name VARCHAR(30),
                    email VARCHAR(60) UNIQUE
                );
                CREATE TABLE IF NOT EXISTS phone(
                    phone_id SERIAL PRIMARY key,
                    client_id INTEGER REFERENCES client(client_id) ON DELETE CASCADE,
                 	phone VARCHAR(20) UNIQUE
                );  
                ''')
        conn.commit()
    def add_client(self, conn, first_name:str=None, last_name:str=None, email:str=None):
        '''Добавить нового клиента'''
        with conn.cursor() as cur:
            request = 'INSERT INTO client('
            values = []
            if first_name:
                request += 'first_name, '
                values.append(first_name)
            if last_name:
                request += 'last_name, '
                values.append(last_name)
            if email:
                request += 'email, '
                values.append(email)
            request = request.rstrip(', ') + f') VALUES({"%s," * len(values)}'.rstrip(', ')
            request +=') RETURNING client_id, first_name, last_name, email'
            cur.execute(request, values)
            message = f'Добавлен клиент:\n ID: {cur.fetchone()[0]}\n '
            if first_name: message += f'Имя: {first_name}\n '
            if last_name: message += f'Фамилия: {last_name}\n '
            if email: message += f'e-mail: {email}\n '
            print(message)
    def add_client_phone(self, conn, client_id:int, phone:str):
        '''Добавить телефон для существующего клиента'''
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO phone(client_id, phone)
                VALUES(%s, %s) RETURNING phone_id, phone;
                ''', (client_id, phone))
            #print(f'Телефон {phone} добавлен юзеру # {cur.fetchone()[0]}')
    def client_data_change(self, conn, clinet_id:int, first_name:str=None, last_name:str=None, email:str=None):
        '''Изменить данные о клиенте'''
        with conn.cursor() as cur:
            request = 'UPDATE client SET '
            values = []
            if first_name:
                request += 'first_name = %s, '
                values.append(first_name)
            if last_name:
                request += 'last_name = %s, '
                values.append(last_name)
            if email:
                request += 'email = %s, '
                values.append(email)
            request = request.rstrip(', ')
            request += ' WHERE client_id = %s;'
            values.append(clinet_id)
            cur.execute(request, values)
        conn.commit()
    def client_phone_change(self, conn, phone_id:int, new_phone_number:str):
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE phone SET phone = %s
                WHERE phone_id = %s               
                ''', (new_phone_number, phone_id))
        conn.commit()
    def remove_client_phone(self, conn, phone:str):
        '''Удалить телефон для существующего клиента'''
        with conn.cursor() as cur:
            cur.execute('''
                DELETE FROM phone
                WHERE phone_id = %s;
                ''', (phone,))
        conn.commit()
    def remove_client(self, conn, client:int):
        '''Удалить существующего клиента'''
        with conn.cursor() as cur:
            cur.execute('''
                DELETE FROM client
                WHERE client_id = %s;
                ''', (client,))
    def client(self, conn, first_name:str=None, last_name:str=None, email:str=None, phone:str=None):
        '''Найти клиента по его данным: имени, фамилии, email или телефону'''
        with conn.cursor() as cur:
            request_with_phone = '''
            SELECT c.client_id, c.first_name, c.last_name, c.email, p.phone 
            FROM client c 
            JOIN phone p on c.client_id = p.client_id 
            WHERE 1=1
            '''
            request_without_phone = '''
            SELECT c. client_id, c.first_name, c.last_name, c.email
            FROM client c 
            WHERE 1=1
            '''
            request = ''
            values = []
            phone_dict = dict()
            if first_name:
                request += ' AND c.first_name = %s'
                values.append(first_name)
            if last_name:
                request += ' AND c.last_name = %s'
                values.append(last_name)
            if email:
                request += ' AND c.email = %s'
                values.append(email)
            if phone:
                request += ' AND p.phone = %s'
                values.append(phone)
            request_with_phone += request
            request_without_phone += request
            cur.execute(request_without_phone, values)
            for item in cur.fetchall():
                if item[0] not in phone_dict:
                    phone_dict[item[0]] = {k:v for (k,v) in zip(('Имя:', 'Фамилия:', 'Email:'),item[1:])}
                    phone_dict[item[0]]['Телефоны:'] = 'Отсутствуют'
            cur.execute(request_with_phone, values)
            for item in cur.fetchall():
                if item[0] not in phone_dict:
                    phone_dict[item[0]] = {k: v for (k, v) in zip(('Имя:', 'Фамилия:', 'Email:'), item[1:-1])}
                    phone_dict[item[0]]['Телефоны:'] = [item[-1]]
                else:
                    if phone_dict[item[0]]['Телефоны:'] == 'Отсутствуют':
                        phone_dict[item[0]]['Телефоны:'] = []
                    phone_dict[item[0]]['Телефоны:'].append(item[-1])
            if phone_dict:
                print('Результаты поиска:')
                for item in phone_dict:
                    print(f"ID: {item}\nИмя: {phone_dict[item]['Имя:']}\n"
                          f"Фамилия: {phone_dict[item]['Фамилия:']}\nEmail: {phone_dict[item]['Email:']}\n"
                          f"Телефоны: {phone_dict[item]['Телефоны:']}")

with psycopg2.connect(database='PersInfo_db', user='postgres', password='N0name89') as conn:
    clients = [['Vasya', 'Pupkin', 'pupkin@qwe.com'],
               ['Vasilii','Отсутвует','ne_pupkin@qwe.com'],
               ['Jenya', 'Jhonson', 'jynya@qwe.com'],
               ['Olexis', 'Sanchez', 'sanchez@qwe.com']
               ]
    PersonalInfo = DataBase()
    PersonalInfo.drop_db(conn)
    PersonalInfo.create_db(conn)
    [PersonalInfo.add_client(conn, *item) for item in clients]
    PersonalInfo.add_client_phone(conn, 2, '+7-912-22-45-656')
    PersonalInfo.add_client_phone(conn, 2, '+7-999-22-22-222')
    PersonalInfo.add_client_phone(conn, 2, '+7-999-3-2333-222')
    PersonalInfo.add_client_phone(conn, 3, '+9-912-22-45-656')
    PersonalInfo.client_data_change(conn, 1, last_name='Petrov')
    PersonalInfo.client_phone_change(conn, 3, '123_new')
    #PersonalInfo.remove_client_phone(conn, 1)
    #PersonalInfo.client(conn, first_name='Vasya')
    #PersonalInfo.remove_client(conn, 1)
    #print('remove id=1 Vasya')
    PersonalInfo.client_data_change(conn, 2, first_name='Vasya', email='new_email@qwe.com')
    print('rename id=2 from Vasilii to Vasya')
    PersonalInfo.client(conn, first_name='Vasya')




