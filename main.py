from collections import UserDict
from abc import ABC, abstractmethod
from clean import main as clean_main

import pickle


class UserInterface(ABC):
    @abstractmethod
    def display_contacts(self, contacts):
        pass

    @abstractmethod
    def display_commands(self, commands):
        pass


class ConsoleUI(UserInterface):
    def display_contacts(self, contacts):
        print("Contacts:")
        for contact in contacts:
            print(contact.name)

    def display_commands(self, commands):
        print("Available Commands:")
        for command in commands:
            print(command)


class AddressBookApplication:
    def __init__(self, user_interface):
        self.user_interface = user_interface

    def display_contacts(self):
        contacts = [record for record in address_book.data.values()]
        self.user_interface.display_contacts(contacts)

    def display_commands(self):
        commands = list(COMMANDS.keys())
        self.user_interface.display_commands(commands)


class Field:
    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value

    def __str__(self):
        return str(self.__value)


class Name(Field):
    pass


class Email(Field):
    def __init__(self, value):
        super().__init__(value)
        self.value = value

    @staticmethod
    def validate_email(email):
        return "@" in email


class Address(Field):
    def __init__(self, value):
        super().__init__(value)
        self.value = value


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.value = value

    @Field.value.setter
    def value(self, new_value):
        if not self.validate_phone(new_value):
            raise ValueError("Invalid phone number format")
        self.__value = new_value

    @staticmethod
    def validate_phone(phone):
        return len(phone) == 10 and phone.isdigit()


class Note:
    def __init__(self):
        self.notes = []

    def add_note(self, note):
        self.notes.append(note)

    def remove_note(self, note):
        if note in self.notes:
            self.notes.remove(note)

    def search_note(self, search_note):
        return [note for note in self.notes if search_note in note]

    def __str__(self):
        return "\n".join(self.notes)


class Clean:

    @staticmethod
    def clean(file_path):
        clean_main(file_path)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.email = []
        self.address = []
        self.note = Note()

    def add_phone(self, phone):
        if Phone.validate_phone(phone):
            new_phone = Phone(phone)
            self.phones.append(new_phone)
        else:
            print("Invalid phone number")

    def edit_phone(self, old_phone, new_phone):
        if not Phone.validate_phone(new_phone):
            raise ValueError("Invalid phone")
        phone_found = False
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                phone_found = True
                break
        if phone_found:
            print(f"Phone number {old_phone} edited to {new_phone}")
        else:
            raise ValueError(f"Phone number {old_phone} not found")

    def find_phone(self, phone):
        for phone_number in self.phones:
            if phone_number.value == phone:
                return phone_number
        return None

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def add_email(self, email):
        if Email.validate_email(email):
            self.email = Email(email)
        else:
            raise ValueError("Invalid email address")

    def edit_email(self, new_email):
        if Email.validate_email(new_email):
            self.email.value = new_email
        else:
            raise ValueError("Invalid email address")

    def remove_email(self, _):
        self.email = None

    def add_address(self, address):
        self.address = Address(address)

    def edit_address(self, new_address):
        self.address.value = new_address

    def remove_address(self, _):
        self.address = None

    def add_note(self, note_value):
        self.note.add_note(note_value)

    def remove_note(self, note_value):
        self.note.remove_note(note_value)

    def search_note(self, search_term):
        return self.note.search_note(search_term)

    def __str__(self):
        phones_info = '; '.join(p.value for p in self.phones)
        email_info = f", Email: {self.email}" if self.email else ""
        address_info = f", Address: {self.address}" if self.address else ""
        note_info = f", Note: {self.note}" if self.note else ""
        return (f"Contact name: {self.name.value}, "
                f"phones: {phones_info}{email_info}{address_info}{note_info}")


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return f"Contact name {name} deleted"
        else:
            return f"Contact name {name} not found"

    def find(self, name):
        return self.data.get(name, None)

    def save_to_file(self, file_name):
        with open(file_name, "wb") as file:
            pickle.dump(self.data, file)

    def load_from_file(self, file_name):
        try:
            with open(file_name, "rb") as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print("File not found")
        except Exception as e:
            print(f"Error when downloading data from a file: {e}")

    def search(self, query):
        results = []
        for record in self.data.values():
            for phone in record.phones:
                if query in phone.value:
                    results.append(record)
                    break

        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                if record not in results:
                    results.append(record)

        return results


COMMANDS = {}


def register_command(command):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as err:
                print(f"Error while registering command: {err}")

        COMMANDS[command] = wrapper
        return wrapper
    return decorator


@register_command(command="hello")
def hello():
    print("Hello user")


@register_command(command="add_contact")
def add_contact(name):
    record = Record(name)
    address_book.add_record(record)
    address_book.save_to_file("address_book.pkl")
    print(f"Contact {name} added")


# @register_command(command="find_contact")
# def find_contact(name):
#     record = Record(name)
#     address_book.find(record)
#     print(f"Contact {name}")


@register_command(command="delete_contact")
def delete_contact(name):
    record = Record(name)
    address_book.delete(record)
    address_book.save_to_file("address_book.pkl")
    print(f"Contact {name} delete")


@register_command(command="add_phone")
def add_phone(name, phone):
    record = address_book.find(name)
    record.add_phone(phone)
    address_book.add_record(record)
    address_book.save_to_file("address_book.pkl")
    print(f"Contact {name} Add phone: {phone}")


@register_command(command="edit_phone")
def edit_phone(name, new_number):
    record = address_book.find(name)
    if record:
        record.phones = []
        record.add_phone(new_number)
        address_book.save_to_file("address_book.pkl")
        print(f"Change name:{name}, phone number:{new_number}")
    else:
        print(f"Not {name} found")


@register_command(command="search_phone")
def search_phone(name):
    record = address_book.find(name)
    if record:
        print(f"Phone number: {record.phones[0].value}" if record.phones else f"No phone number for {name}")


@register_command(command="del_phone")
def delete_phone(name, phone):
    record = address_book.find(name)
    if record:
        record.remove_phone(phone)
        address_book.save_to_file("address_book.pkl")
        print(f"Phone {phone} removed")
    else:
        print(f"Not {name} or {phone} found")


@register_command(command="add_email")
def add_email(name, email):
    record = address_book.find(name)
    if record:
        try:
            record.add_email(email)
            address_book.save_to_file("address_book.pkl")
            print(f"Email added: {email} to contact {name}")
        except ValueError as err:
            print(f"Error: {err}")
    else:
        print(f"Contact {name} not found")


@register_command(command="edit_email")
def edit_email(name, new_email):
    record = address_book.find(name)
    if record:
        record.email = []
        record.add_email(new_email)
        address_book.save_to_file("address_book.pkl")
        print(f"Email change: {new_email} to contact {name}")
    else:
        print(f"Not {name} found")


@register_command(command="del_email")
def delete_email(name, email):
    record = address_book.find(name)
    if record:
        record.remove_email(email)
        address_book.save_to_file("address_book.pkl")
        print(f"Email address {email} removed")
    else:
        print(f"Not {name} or {email} found")


@register_command(command="add_address")
def add_address(name, address):
    record = address_book.find(name)
    if record:
        record.add_address(address)
        address_book.save_to_file("address_book.pkl")
        print(f"Address added to contact: {name}")
    else:
        print(f"Contact {name} not found")


@register_command(command="edit_address")
def edit_address(name, new_address):
    record = address_book.find(name)
    if record:
        record.address = []
        record.add_address(new_address)
        address_book.save_to_file("address_book.pkl")
        print(f"Address change: {new_address}")
    else:
        print(f"Contact {name} not found")


@register_command(command="del_address")
def delete_address(name, address):
    record = address_book.find(name)
    if address:
        record.remove_address(address)
        address_book.save_to_file("address_book.pkl")
        print(f"Address {address} removed")
    else:
        print(f"Contact {name} or {address} not found")


@register_command(command="add_note")
def add_note(name, *note_text):
    record = address_book.find(name)
    if record:
        if record.note is None:
            record.note = Note()
        record.note.add_note(' '.join(note_text))
        address_book.save_to_file("address_book.pkl")
        print(f"Note added to {name}: {' '.join(note_text)}")
    else:
        print("Contact {name} not found")


# @register_command(command="search_notes")
# def search_notes():


@register_command(command="del_note")
def delete_note(name, *note_text):
    record = address_book.find(name)
    if record:
        if record.note:
            note = ' '.join(note_text)
            if note in record.note.notes:
                record.note.remove_note(note)
                address_book.save_to_file("address_book.pkl")
                print(f"Note '{note}' removed from {name}")
            else:
                print(f"Note '{note}' not found for {name}")
        else:
            print(f"No notes found for {name}")
    else:
        print(f"Contact {name} not found")


@register_command(command="contact_info")
def contact_info(name):
    record = address_book.find(name)
    if record:
        print(record)
    else:
        print(f"Contact {name} not found")


@register_command(command="all_contacts")
def display_contacts():
    app.display_contacts()


@register_command(command="all_commands")
def display_commands():
    app.display_commands()


@register_command(command="clean")
def clean(path):
    Clean.clean(path)


@register_command(command="load")
def load():
    address_book.load_from_file('address_book.pkl')
    print("Address book loaded")


@register_command(command="exit")
def exit_cli():
    print("Good bye")


def main():
    while True:
        user_input = input(">>> ").strip()
        user_input = user_input.lower()
        command_name, *args = user_input.split()

        if command_name in COMMANDS:
            COMMANDS[command_name](*args)
            if command_name in ["exit"]:
                break
        else:
            print("Unknown command")


app = AddressBookApplication(ConsoleUI())
address_book = AddressBook()

if __name__ == "__main__":
    main()
