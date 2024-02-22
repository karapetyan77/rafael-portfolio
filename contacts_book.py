import tkinter as tk
import sqlite3


class ContactsBook:
    def __init__(self):
        try:
            self.data_base = sqlite3.connect("Contacts.db")
            self.cursor = self.data_base.cursor()
            # Create the main application window
            self.root = tk.Tk()
            # List to store labels displaying contact records
            self.contact_rows = []
            # Initialize the graphical user interface
            self.initGUI()
            # Start the Tkinter event loop
            self.root.mainloop()
        finally:
            self.data_base.close()

    def __exit__(self):
        self.data_base.close()

    def initGUI(self):
        # Set window title and dimensions
        self.root.title("Contacts Book")
        self.root.geometry("400x600")

        # Create entry fields and labels for name, surname, address, and phone number
        self.name = tk.Entry(self.root, width=30)
        self.name.grid(row=0, column=1, padx=20, pady=(10, 0))
        name_label = tk.Label(self.root, text="Name")
        name_label.grid(row=0, column=0, pady=(10, 0))

        self.surname = tk.Entry(self.root, width=30)
        self.surname.grid(row=1, column=1)
        surname_label = tk.Label(self.root, text="Surname")
        surname_label.grid(row=1, column=0)

        self.address = tk.Entry(self.root, width=30)
        self.address.grid(row=2, column=1)
        address_label = tk.Label(self.root, text="Address")
        address_label.grid(row=2, column=0)

        self.phone_number = tk.Entry(self.root, width=30)
        self.phone_number.grid(row=3, column=1)
        phone_number_label = tk.Label(self.root, text="Phone Number")
        phone_number_label.grid(row=3, column=0)

        # Entry field and label for selecting contact ID
        self.select = tk.Entry(self.root, width=30)
        self.select.grid(row=6, column=1, pady=5)
        select_label = tk.Label(self.root, text="Select ID")
        select_label.grid(row=6, column=0, pady=5)

        # Buttons for adding, showing, deleting, and editing records
        submit_btn = tk.Button(self.root, text="Add Record", command=self.submit)
        submit_btn.grid(row=4, column=0, padx=10, columnspan=2, pady=10, ipadx=100)

        query_btn = tk.Button(self.root, text="Show Records", command=self.query)
        query_btn.grid(row=5, column=0, padx=10, columnspan=2, pady=10, ipadx=137)

        remove_btn = tk.Button(self.root, text="Delete Record", command=self.remove)
        remove_btn.grid(row=7, column=0, padx=10, columnspan=2, pady=10, ipadx=136)

        edit_btn = tk.Button(self.root, text="Edit Record", command=self.edit)
        edit_btn.grid(row=8, column=0, padx=10, columnspan=2, pady=10, ipadx=143)

    def initEditorGUI(self):
        # Hide the main window
        self.root.withdraw()
        # Create a new window for editing records
        self.editor = tk.Tk()
        self.editor.title("Edit contact")
        self.editor.geometry("400x300")

        # Entry fields and labels for editing contact information
        self._name = tk.Entry(self.editor, width=30)
        self._name.grid(row=0, column=1, padx=20, pady=(10, 0))
        _name_label = tk.Label(self.editor, text="Name")
        _name_label.grid(row=0, column=0, pady=(10, 0))

        self._surname = tk.Entry(self.editor, width=30)
        self._surname.grid(row=1, column=1)
        _surname_label = tk.Label(self.editor, text="Surname")
        _surname_label.grid(row=1, column=0)

        self._address = tk.Entry(self.editor, width=30)
        self._address.grid(row=2, column=1)
        _address_label = tk.Label(self.editor, text="Address")
        _address_label.grid(row=2, column=0)

        self._phone_number = tk.Entry(self.editor, width=30)
        self._phone_number.grid(row=3, column=1)
        _phone_number_label = tk.Label(self.editor, text="Phone Number")
        _phone_number_label.grid(row=3, column=0)

        # Button to save edited contact information
        _save_btn = tk.Button(self.editor, text="Save Contact", command=self.update)
        _save_btn.grid(row=4, column=0, padx=10, pady=10, columnspan=2, ipadx=145)

    def submit(self):
        try:
            self.cursor.execute("""INSERT INTO contacts VALUES
                                (:name, :surname, :add, :num)""",
                                {
                                   'name': self.name.get(),
                                   'surname': self.surname.get(),
                                   'add': self.address.get(),
                                   'num': self.phone_number.get()
                                })
        except sqlite3.OperationalError:
            return

        self.data_base.commit()

        # Clear entry fields after adding a record
        self.name.delete(0, tk.END)
        self.surname.delete(0, tk.END)
        self.address.delete(0, tk.END)
        self.phone_number.delete(0, tk.END)

    def query(self):
        # Clear previously displayed records
        for label in self.contact_rows:
            label.destroy()

        try:
            # Retrieve all records from the database
            self.cursor.execute("SELECT *, oid FROM contacts")
        except sqlite3.OperationalError:
            return

        records = self.cursor.fetchall()
        r = 12
        # Display each record as a label in the GUI
        for item in records:
            my_str = f"{item[4]}. {item[0]} {item[1]} {item[2]} {item[3]}"
            my_label = tk.Label(self.root, text=my_str)
            my_label.grid(row=r, column=0, columnspan=2)
            self.contact_rows.append(my_label)
            r += 1

    def update(self):
        selected_id = self.select.get()
        try:
            self.cursor.execute("""UPDATE contacts SET
                              name = :first,
                              surname = :last,
                              address = :add,
                              phone_number = :num
                              WHERE oid = :oid""",

                                {
                                 'first': self._name.get(),
                                 'last': self._surname.get(),
                                 'add': self._address.get(),
                                 'num': self._phone_number.get(),
                                 'oid': selected_id
                                })
        except sqlite3.OperationalError:
            return

        self.data_base.commit()
        # Clear entry field for selecting ID after updating record
        self.select.delete(0, tk.END)
        # Close the editor window and show the main window
        self.editor.destroy()
        self.root.deiconify()

    def edit(self):
        selected_id = self.select.get()
        try:
            # Retrieve the selected record from the database
            self.cursor.execute(f"SELECT * FROM contacts WHERE oid = {selected_id}")
            records = self.cursor.fetchall()
        except sqlite3.OperationalError:
            return

        # Initialize the editor GUI with the selected record's information
        self.initEditorGUI()
        self._name.insert(0, records[0][0])
        self._surname.insert(0, records[0][1])
        self._address.insert(0, records[0][2])
        self._phone_number.insert(0, records[0][3])

    def remove(self):
        try:
            self.cursor.execute(f"DELETE from contacts WHERE oid = {self.select.get()}")
        except sqlite3.OperationalError:
            return
        # Clear entry field for selecting ID after deleting record
        self.select.delete(0, tk.END)
        self.data_base.commit()


if __name__ == "__main__":
    cb = ContactsBook()
