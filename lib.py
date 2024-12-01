"""Реализация базы данных для хранения информации о книгах. В программе
используется стандартная библиотека sqlite3. Объект курсора curs, позволяющий
писать запросы SQL, является глобальным и используется во всех функциях,
выполняющих конкретную задачу. Запросы SQL создаются с использованием
заполнителей, препятствующих инъекциям SQL.

Программа позволяет добавлять, удалять, искать, отображать книги и изменять
их статус. Интерактивный интерфейс состоит из основного меню и меню по
конкретной операции, где пользователь может выполнить несколько действий
одного типа.
"""

from sqlite3 import connect

# Заголовок для вывода на экран
HEADER = ('id', 'title', 'author', 'year', 'status')

def help():
    """Краткое знакомство с интерфейсом программы."""
    print('\n1 - добавление книги')
    print('2 - удаление книги')
    print('3 - поиск книги')
    print('4 - отображение всех книг')
    print('5 - изменение статуса книги')
    print('h - помощь')
    print('q - выход из программы')

def print_row(row):
    """Вспомогательная функция, вывод на экран одной записи из базы данных
    в определённом формате. row - список или кортеж из 5 элементов"""
    print('| {:<6}| {:<40}| {:<40}| {:<5}| {:<9} |'.format(*row))

def insert():
    """Добавление книг в базу данных"""
    global curs
    print('Выбор 1 - добавление книги.')
    while True:
        title = input('\nНазвание книги: ')
        author = input('Автор: ')
        year = input('Год издания (со знаком минус для дат до н.э.): ')

        # Проверка входных данных
        if not 0 < len(title) <= 40 or not 0 < len(author) <= 40:
            print('Текстовые поля должны быть непустыми и содержать не более 40 символов.')
            continue
        try:
            year = int(year)
        except:
            print('Год должен быть целым числом.')
            continue
        if not -999 <= year <= 2050:
            print('Диапазон для года от -999 до 2050.')
            continue

        # Запись в базу данных
        # Использование заполнителей для предотвращения инъекций SQL
        sql = 'INSERT INTO books (title, author, year) VALUES(?, ?, ?)'
        curs.execute(sql, (title, author, year))
        print('\nДанные успешно добавлены.')

        i = input('Добавить ещё одну книгу (y/n)? ')
        if i != 'y' and i != 'yes':
            break # выход в основное меню

def delete():
    """Удаление книг из базы данных по id"""
    global curs
    print('Выбор 2 - удаление книги.')
    while True:
        id = input('\nВведите идентификатор книги (q для выхода в основное меню): ')

        # Проверка входных данных
        if id == 'q' or id == 'quit':
            return # выход в основное меню
        try:
            int(id)
        except:
            print('Идентификатор должен быть целым числом.')
            continue
        sql = 'SELECT rowid, * FROM books WHERE rowid=?'
        curs.execute(sql, (id,))
        res = curs.fetchall()
        if not res:
            print('Книга с данным идентификатором отсутствует.')
            continue

        # Вывод информации о книге и подтверждение её удаления
        print()
        print_row(HEADER)
        print('-' * 112)
        print_row(res[0])
        i = input('\nУдалить данную книгу (y/n)? ')
        if i != 'y' and i != 'yes':
            continue

        # Удаление книги
        sql = 'DELETE FROM books WHERE rowid=?'
        curs.execute(sql, (id,))
        print('\nКнига успешно удалена.')

        i = input('Удалить ещё одну книгу (y/n)? ')
        if i != 'y' and i != 'yes':
            break # выход в основное меню

def search():
    """Поиск книг по полям title, author, year"""
    global curs
    print('Выбор 3 - поиск книги.')
    print('Для текстовых полей можно вводить неполное название, пустой ввод для пропуска.')
    print('Для года можно задать диапазон, пустой ввод для пропуска.')
    while True:
        title = input('\nНазвание книги: ')
        author = input('Автор: ')
        year_min = input('Год издания (нижняя граница): ')
        year_max = input('Год издания (верхняя граница): ')

        # Проверка корректности задания года
        try:
            year_min = int(year_min)
        except:
            year_min = -999

        try:
            year_max = int(year_max)
        except:
            year_max = 2050

        # Получение информации о книгах
        sql = f'''SELECT rowid, * FROM books WHERE title LIKE "%{title}%"
        AND author LIKE "%{author}%" AND year BETWEEN {year_min} AND {year_max}'''
        curs.execute(sql)
        res = curs.fetchall()

        # Вывод на экран в удобном формате
        print()
        print_row(HEADER)
        print('-' * 112)
        for row in res:
            print_row(row)

        i = input('\nОбработать ещё один запрос (y/n)? ')
        if i != 'y' and i != 'yes':
            break # выход в основное меню

def show_table():
    """Вывод информации о всех книгах в базе данных"""
    global curs
    print('Выбор 4 - отображение всех книг.\n')

    # Получение информации о книгах
    curs.execute('SELECT rowid, * FROM books')
    res = curs.fetchall()

    # Вывод на экран в удобном формате
    print_row(HEADER)
    print('-' * 112)
    for row in res:
        print_row(row)

def change_status():
    """Изменение статуса книги с 'в наличии' на 'выдана' и наоборот"""
    global curs
    print('Выбор 5 - изменение статуса книги.')
    while True:
        id = input('\nВведите идентификатор книги (q для выхода в основное меню): ')

        # Проверка входных данных
        if id == 'q' or id == 'quit':
            return # выход в основное меню
        try:
            int(id)
        except:
            print('Идентификатор должен быть целым числом.')
            continue
        sql = 'SELECT rowid, * FROM books WHERE rowid=?'
        curs.execute(sql, (id,))
        res = curs.fetchall()
        if not res:
            print('Книга с данным идентификатором отсутствует.')
            continue

        # Вывод информации о книге и подтверждение изменения её статуса
        print()
        print_row(HEADER)
        print('-' * 112)
        print_row(res[0])
        status = res[0][4]
        new_status = 'выдана' if status == 'в наличии' else 'в наличии'
        i = input(f"\nИзменить статус на '{new_status}' (y/n)? ")
        if i != 'y' and i != 'yes':
            continue

        # Изменение статуса
        sql = 'UPDATE books SET status=? WHERE rowid=?'
        curs.execute(sql, (new_status, id))
        print('\nСтатус успешно изменён.')

        i = input('Изменить статус ещё одной книги (y/n)? ')
        if i != 'y' and i != 'yes':
            break # выход в основное меню

# Создание базы данных 'library.db' в случае необходимости и подключение к ней
conn = connect('library.db', autocommit=True)
curs = conn.cursor()

# Проверка существования таблицы 'books' и её создание в случае необходимости
curs.execute('SELECT * FROM sqlite_schema WHERE type="table" AND name="books"')
if not curs.fetchall():
    curs.execute('''CREATE TABLE books(title VARCHAR(40) NOT NULL,
    author VARCHAR(40), year INT, status VARCHAR(9) DEFAULT "в наличии")''')

# Приветствие и знакомство с интерфейсом
print('Вас приветствует электронная библиотека!')
print('Пожалуйста, выберите действие и введите нужную цифру.')
help()

# Реализация основного меню в виде цикла работы с базой данных
while True:
    i = input('\nlibrary_db> ')
    if i == '1':
        insert()
    elif i == '2':
        delete()
    elif i == '3':
        search()
    elif i == '4':
        show_table()
    elif i == '5':
        change_status()
    elif i == 'h' or i == 'help':
        help()
    else:
        break

# Закрытие базы данных
print('Закрытие базы данных.')
curs.close()
conn.close()
